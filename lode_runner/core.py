# coding: utf-8

import logging
from unittest import suite

from nose.core import TextTestResult, TextTestRunner, TestProgram
from nose.proxy import ResultProxyFactory as NoseResultProxyFactory, ResultProxy as NoseResultProxy
from nose.loader import TestLoader as NoseTestLoader
from nose.suite import ContextSuiteFactory
from nose.failure import Failure


log = logging.getLogger('lode_runner.core')


class ResultProxy(NoseResultProxy):
    def assertMyTest(self, test):
        pass

    def addFailure(self, test, err):
        super(ResultProxy, self).addFailure(test, err)
        self.check_fail_limit()

    def addError(self, test, err):
        super(ResultProxy, self).addError(test, err)
        self.check_fail_limit()

    def check_fail_limit(self):
        fail_limit = getattr(self.config, "failLimit", None)
        if fail_limit and len(self.failures) + len(self.errors) >= fail_limit:
            self.shouldStop = True


class ResultProxyFactory(NoseResultProxyFactory):
    def __call__(self, result, test):
        """Return a ResultProxy for the current test.

        On first call, plugins are given a chance to replace the
        result used for the remaining tests. If a plugin returns a
        value from prepareTestResult, that object will be used as the
        result for all tests.
        """
        if not self.__prepared:
            self.__prepared = True
            plug_result = self.config.plugins.prepareTestResult(result)
            if plug_result is not None:
                self.__result = result = plug_result
        if self.__result is not None:
            result = self.__result
        return ResultProxy(result, test, config=self.config)


class TestLoader(NoseTestLoader):
    def __init__(self, *args, **kwargs):
        super(TestLoader, self).__init__(*args, **kwargs)
        self.suiteClass = ContextSuiteFactory(self.config, resultProxy=ResultProxyFactory(config=self.config))

    def makeTest(self, obj, parent=None):
        if getattr(self.config, "suppressTearDownExceptions", False):
            obj_to_wrap = obj if isinstance(obj, type) else parent
            if obj_to_wrap:
                self._wrap_with_suppressor(obj_to_wrap)

        return super(TestLoader, self).makeTest(obj, parent)

    def loadTestsFromTestCase(self, testCaseClass):
        """Return a suite of all tests cases contained in testCaseClass"""
        if issubclass(testCaseClass, suite.TestSuite):
            raise TypeError("Test cases should not be derived from TestSuite."
                            " Maybe you meant to derive from TestCase?")

        test_case_names = self.getTestCaseNames(testCaseClass)
        if not test_case_names and hasattr(testCaseClass, 'runTest'):
            test_case_names = ['runTest']

        result = self._makeTest(test_case_names, testCaseClass)
        if isinstance(result, Failure):
            return self.suiteClass(list(map(testCaseClass, test_case_names)))
        else:
            return result

    def loadTestsFromModule(self, module, path=None, discovered=False):
        plugin_tests = []
        for test in self.config.plugins.loadTestsFromModule(module, path=None, discovered=False):
            plugin_tests.append(test)
        if plugin_tests:
            return plugin_tests
        return super(TestLoader, self).loadTestsFromModule(module, path=None, discovered=False)

    def _wrap_with_suppressor(self, obj):
        try:
            from lode_runner.plugins.suppressor import suppress_exceptions
        except ImportError:
            log.exception('Error wrapping with lode_runner.plugins.suppressor ()')
            return

        names_list = ['tearDown'] + list(self.suiteClass.suiteClass.classTeardown)
        methods_to_wrap = [getattr(obj, _name) for _name in names_list if hasattr(obj, _name)]
        for _method in methods_to_wrap:
            setattr(obj, _method.__name__, suppress_exceptions(_method))


class LodeTestResult(TextTestResult):
    pass


class LodeRunner(TextTestRunner):
    def _makeResult(self):
        return LodeTestResult(
            self.stream,
            self.descriptions,
            # TODO: make custom output and then set verbosity 0
            self.verbosity,
            self.config
        )


class LodeProgram(TestProgram):
    def runTests(self):
        from lode_runner.plugins import multiprocess
        multiprocess._instantiate_plugins = [
            plugin.__class__ for plugin in self.config.plugins
        ]

        if self.testRunner is None:
            self.testRunner = LodeRunner(
                stream=self.config.stream,
                verbosity=self.config.verbosity,
                config=self.config)

        super(LodeProgram, self).runTests()


# must return always new set of plugins
def plugins():
    from lode_runner.plugins.dataprovider import Dataprovider
    from lode_runner.plugins.xunit import Xunit
    from lode_runner.plugins.multiprocess import MultiProcess
    from lode_runner.plugins.testid import TestId
    from lode_runner.plugins.initializer import Initializer
    from lode_runner.plugins.failer import Failer
    from lode_runner.plugins.class_skipper import ClassSkipper
    from lode_runner.plugins.suppressor import Suppressor

    plugs = [
        Dataprovider, Xunit, MultiProcess, TestId, Initializer, Failer, ClassSkipper, Suppressor
    ]

    from nose.plugins import builtin
    overwritten_names = [plug.__name__ for plug in plugs]
    for plug in builtin.plugins:
        if plug.__name__ not in overwritten_names:
            plugs.append(plug)

    return [plug() for plug in plugs]


def main():
    LodeProgram(
        plugins=plugins(),
        testLoader=TestLoader
    )


def run(*args, **kwargs):
    kwargs['exit'] = False
    kwargs['plugins'] = plugins()
    kwargs['testLoader'] = TestLoader
    try:
        argv = kwargs['argv']
        del kwargs['argv']
    except KeyError:
        argv = ['run']
    return LodeProgram(argv=argv, *args, **kwargs).success


if __name__ == "__main__":
    main()
