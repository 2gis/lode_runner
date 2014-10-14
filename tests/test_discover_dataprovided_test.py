# coding: utf-8
import unittest
import sys
from cStringIO import StringIO

from lode_runner import run
from lode_runner.lode_runner import LodeRunner
from nose.config import Config
from nose.plugins import PluginManager

from lode_runner.lode_runner import TestLoader, LodeTestResult, Dataprovider


class DiscoverTest(unittest.TestCase):
    tests_location = "tests/data/dataprovided/dataprovided.py"
    tested_test = ":TestCase.test_with_dataprovider_fixture_2"
    argv = []

    ran_1_test = "Ran 1 test"
    no_such_test = "ValueError: No such test"

    def setUp(self):
        self.config = Config()
        self.config.plugins = PluginManager()
        self.config.plugins.addPlugin(Dataprovider())
        self.config.configure(self.argv)

    def tearDown(self):
        del sys.modules["dataprovided"]
        self.argv = []


class DiscoverWithDataprovidersFirstTest(DiscoverTest):
    def setUp(self):
        self.argv = [
            # 0 is always program
            "lode_runner",
            "--dataproviders-first"
        ]
        super(DiscoverWithDataprovidersFirstTest, self).setUp()

    def test_discover_dataprovided_test_by_regexp(self):
        stream = StringIO()
        result = run(testRunner=LodeRunner(stream=stream), argv=[
            "lode_runner",
            "--dataproviders-first",
            "-m", "test_with_dataprovider_fixture_2",
            "tests/data/dataprovided/dataprovided.py"])
        self.assertTrue(self.ran_1_test in stream.getvalue(),
                        "\n%s in stream output:\n%s" % (self.ran_1_test, stream.getvalue()))
        self.assertTrue(result)

    def test_success_discover_dataprovided_test_by_name(self):
        stream = StringIO()
        tests = TestLoader(config=self.config).loadTestsFromName(self.tests_location + self.tested_test)
        result = LodeTestResult(stream, None, 0)
        tests.run(result)

        self.assertEqual(1, result.testsRun)
        self.assertEqual([], result.errors)
        self.assertTrue(result.wasSuccessful())


class DiscoverWithoutDataprovidersFirstTest(DiscoverTest):
    def test_discover_all_tests(self):
        stream = StringIO()
        tests = TestLoader(config=self.config).loadTestsFromName(self.tests_location)
        extracted_tests = list()
        for t in tests._tests:
            extracted_tests += t._precache
        result = LodeTestResult(stream, None, 0)
        tests.run(result)
        self.assertTrue(result)
        self.assertEqual(4, result.testsRun)
        self.assertEqual(4, len(extracted_tests))
        self.assertTrue(result.wasSuccessful())

    def test_fail_discover_dataprovided_test_by_name(self):
        traceback = \
            "Traceback (most recent call last):\n" \
            "  File \"/usr/local/lib/python2.7/dist-packages/nose/failure.py\", line 41, in runTest\n" \
            "    raise self.exc_class(self.exc_val)\n" \
            "ValueError: No such test TestCase.test_with_dataprovider_fixture_2\n"

        stream = StringIO()
        tests = TestLoader(config=self.config).loadTestsFromName(self.tests_location + self.tested_test)
        result = LodeTestResult(stream, None, 0)
        tests.run(result)

        self.assertEqual(1, result.testsRun)
        tb = result.errors[0][1]
        self.assertEqual(traceback, tb)
        self.assertFalse(result.wasSuccessful())