# coding: utf-8

import unittest

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from optparse import OptionValueError
from nose.config import Config
from nose.plugins import PluginManager
from lode_runner.core import LodeTestResult, TestLoader
from lode_runner.exceptions import PluginConfigureException
from lode_runner.plugins.failer import Failer


def get_test_class_failures():
    class TestFailures(unittest.TestCase):
        def test_will_fail_1(self):
            self.assertTrue(False)

        def test_will_fail_2(self):
            self.assertTrue(False)

        def test_will_fail_3(self):
            self.assertTrue(False)
    return TestFailures


def get_test_class_errors():
    class TestFailures(unittest.TestCase):
        def test_will_fail_1(self):
            raise

        def test_will_fail_2(self):
            raise

        def test_will_fail_3(self):
            raise
    return TestFailures


class TestFailer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stream = StringIO()

    def setUp(self):
        self.config = Config()
        self.config.plugins = PluginManager()
        self.config.plugins.addPlugin(Failer())

        self.argv = []
        self.argv.append("lode_runner")  # 0 is always should be program name

    def tearDown(self):
        self.argv = []


class TestFailerWithEnvVar(TestFailer):
    def setUp(self):
        self.addCleanup(self.cleanup)
        super(TestFailerWithEnvVar, self).setUp()

    def cleanup(self):
        self.config.env = {}

    def test_run_with_correct_env_var(self):
        self.config.env = {'FAIL_LIMIT': '1'}
        self.config.configure(self.argv)

        tests = TestLoader(config=self.config).loadTestsFromTestClass(get_test_class_failures())
        result = LodeTestResult(self.stream, None, 0)
        tests.run(result)
        self.assertEqual(1, result.testsRun)

    def test_run_with_empty_env_var(self):
        self.config.env = {'FAIL_LIMIT': ''}
        self.assertRaises(OptionValueError, self.config.configure, self.argv)

    def test_run_with_incorrect_env_var(self):
        self.config.env = {'FAIL_LIMIT': '23123sgsjdgajshd'}
        self.assertRaises(OptionValueError, self.config.configure, self.argv)


class TestFailerRunWithArg(TestFailer):
    def setUp(self):
        super(TestFailerRunWithArg, self).setUp()
        self.argv.append("--fail-limit")


class TestFailerOnFailures(TestFailerRunWithArg):
    def test_dont_stop(self):
        """
        Expected: Run all tests from TestFailures (3 failures)
        """
        self.argv.append("4")
        self.config.configure(self.argv)

        tests = TestLoader(config=self.config).loadTestsFromTestClass(get_test_class_failures())
        result = LodeTestResult(self.stream, None, 0)
        tests.run(result)
        self.assertEqual(3, result.testsRun)

    def test_stop_after_2_failures(self):
        """
        Expected: Run 2 tests and stop after 2 failures
        """
        self.argv.append("2")
        self.config.configure(self.argv)

        tests = TestLoader(config=self.config).loadTestsFromTestClass(get_test_class_failures())
        result = LodeTestResult(self.stream, None, 0)
        tests.run(result)
        self.assertEqual(2, result.testsRun)

    def test_negative_value(self):
        """
        Expected: PluginConfigureException
        """
        self.argv.append("-1")
        self.assertRaises(PluginConfigureException, self.config.configure, self.argv)

    def test_zero_value(self):
        """
        Expected: PluginConfigureException
        """
        self.argv.append("-1")
        self.assertRaises(PluginConfigureException, self.config.configure, self.argv)


class TestFailerOnErrors(TestFailerRunWithArg):
    def test_dont_stop(self):
        """
        Expected: Run all tests from TestFailures (3 errors)
        """
        self.argv.append("4")
        self.config.configure(self.argv)

        tests = TestLoader(config=self.config).loadTestsFromTestClass(get_test_class_errors())
        result = LodeTestResult(self.stream, None, 0)
        tests.run(result)
        self.assertEqual(3, result.testsRun)

    def test_stop_after_2_failures(self):
        """
        Expected: Run 2 tests and stop after 2 errors
        """
        self.argv.append("2")
        self.config.configure(self.argv)

        tests = TestLoader(config=self.config).loadTestsFromTestClass(get_test_class_errors())
        result = LodeTestResult(self.stream, None, 0)
        tests.run(result)
        self.assertEqual(2, result.testsRun)

    def test_negative_value(self):
        """
        Expected: PluginConfigureException
        """
        self.argv.append("-1")
        self.assertRaises(PluginConfigureException, self.config.configure, self.argv)

    def test_zero_value(self):
        """
        Expected: PluginConfigureException
        """
        self.argv.append("-1")
        self.assertRaises(PluginConfigureException, self.config.configure, self.argv)
