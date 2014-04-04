from nose.core import TextTestResult, TextTestRunner, TestProgram
from nose.proxy import ResultProxyFactory, ResultProxy
from nose.loader import TestLoader
from nose.suite import ContextSuiteFactory
from unittest import suite


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
            raise TypeError("Test cases should not be derived from TestSuite." \
                                " Maybe you meant to derive from TestCase?")
        testCaseNames = self.getTestCaseNames(testCaseClass)
        if not testCaseNames and hasattr(testCaseClass, 'runTest'):
            testCaseNames = ['runTest']

        if testCaseNames:
            return self._makeTest(testCaseNames, testCaseClass)
        else:
            return super(TestLoader, self).loadTestsFromTestCase(testCaseClass)


class LodeTestResult(TextTestResult):
    pass
    # TODO: fix printErrorList for different encoding
    # def printErrorList(self, flavour, errors):
    #     unicode_escaped_errors = []
    #     for test, _err in errors:
    #         try:
    #             error_str = str(_err)
    #         except UnicodeEncodeError:
    #             error = unicode(_err)
    #         else:
    #             # 'ignore': ignore malformed data and continue decoding without further notice
    #             error = error_str.decode(encoding='unicode-escape', errors='ignore')
    #         unicode_escaped_errors.append((test, error))
    #     super(LodeTestResult, self).printErrorList(flavour, unicode_escaped_errors)


class LodeRunner(TextTestRunner):
    def _makeResult(self):
        # return LodeTestResult(
        return LodeTestResult(
            self.stream,
            self.descriptions,
            # TODO: make custom output and then set verbosity 0
            self.verbosity,
            self.config
        )


class LodeProgram(TestProgram):
    def runTests(self):
        self.testRunner = LodeRunner(
            stream=self.config.stream,
            verbosity=self.config.verbosity,
            config=self.config)

        super(LodeProgram, self).runTests()