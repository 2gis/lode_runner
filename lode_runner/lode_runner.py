from nose.core import TextTestResult, TextTestRunner, TestProgram
from nose.proxy import ResultProxyFactory, ResultProxy
from nose.loader import TestLoader
from nose.suite import ContextSuiteFactory
from nose.case import Test
from nose.failure import Failure
from unittest import suite

from .dataprovider import Dataprovider
from .xunit import Xunit
from .contesto_plugin import ContestoPlugin
from .json_reporter import LodeJsonReporter
from .priority import AttributeSelector
from .multiprocess import MultiProcess


class ContextSuiteFactory(ContextSuiteFactory):
    def makeSuite(self, tests, context, **kw):
        _tests = list()
        for test in tests:
            if isinstance(test, Test):
                test_method = getattr(test.test, test.test._testMethodName).__func__
                if hasattr(test.test, 'priority'):
                    priority = test.test.priority
                elif hasattr(test_method, 'priority'):
                    priority = test_method.priority
                else:
                    priority = "unknown"

                test.priority = priority

            _tests.append(test)
        return super(ContextSuiteFactory, self).makeSuite(_tests, context, **kw)


class ResultProxy(ResultProxy):
    def assertMyTest(self, test):
        pass


class ResultProxyFactory(ResultProxyFactory):
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


class TestLoader(TestLoader):
    def __init__(self, *args, **kwargs):
        super(TestLoader, self).__init__(*args, **kwargs)
        self.suiteClass = ContextSuiteFactory(self.config, resultProxy=ResultProxyFactory(config=self.config))

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
            return self.suiteClass(map(testCaseClass, test_case_names))
        else:
            return result


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
        if self.testRunner is None:
            self.testRunner = LodeRunner(
                stream=self.config.stream,
                verbosity=self.config.verbosity,
                config=self.config)

        super(LodeProgram, self).runTests()


# must return always new set of plugins
def plugins():
    return [
        Dataprovider(),
        Xunit(),
        ContestoPlugin(),
        LodeJsonReporter(),
        AttributeSelector(),
        MultiProcess()
    ]


def main():
    LodeProgram(
        addplugins=plugins(),
        testLoader=TestLoader)


def run(*args, **kwargs):
    kwargs['exit'] = False
    kwargs['addplugins'] = plugins()
    kwargs['testLoader'] = TestLoader
    try:
        argv = kwargs['argv']
    except KeyError:
        argv = ['run']
    return LodeProgram(argv=argv, *args, **kwargs).success
