import unittest
import optparse

from lode_runner.plugins.priority import critical, AttributeSelector
from lode_runner.core import TestLoader
from nose.config import Config


def mk_critical_class():
    @critical
    class TestCase(unittest.TestCase):
        def runTest(self):
            pass
    test = TestCase()
    return test


def mk_critical_method():
    class TestCase(unittest.TestCase):
        @critical
        def runTest(self):
            pass
    test = TestCase()
    return test


def mk_unknown_priority_method():
    class TestCase(unittest.TestCase):
        def runTest(self):
            pass
    test = TestCase()
    return test


class PriorityTest(unittest.TestCase):
    def setUp(self):
        self.loader = TestLoader()

    def test_priority_class(self):
        test = mk_critical_class()
        suited_test = self.loader.suiteClass([test])
        tests = suited_test._tests
        for test in tests:
            self.assertTrue(hasattr(test, "priority"))
            self.assertEqual("critical", test.priority)

    def test_priority_method(self):
        test = mk_critical_method()

        suited_test = self.loader.suiteClass([test])
        tests = suited_test._tests
        for test in tests:
            self.assertTrue(hasattr(test, "priority"))
            self.assertEqual("critical", test.priority)

    def test_priority_unknown(self):
        test = mk_unknown_priority_method()
        suited_test = self.loader.suiteClass([test])
        tests = suited_test._tests
        for test in tests:
            self.assertTrue(hasattr(test, "priority"))
            self.assertEqual("unknown", test.priority)


class PriorityChooseTest(unittest.TestCase):
    def setUp(self):
        parser = optparse.OptionParser()
        self.x = AttributeSelector()
        self.x.add_options(parser, env={})
        (options, args) = parser.parse_args([
            "-a priority=%s" % "critical"
        ])
        self.x.configure(options, Config())

    def test_choose_method(self):
        test = mk_critical_method()
        self.assertTrue(self.x.wantMethod(test.runTest) is None)

    def test_choose_class(self):
        test = mk_critical_class()
        self.assertTrue(self.x.wantMethod(test.runTest) is None)

    def test_dont_choose(self):
        test = mk_unknown_priority_method()
        self.assertFalse(self.x.wantMethod(test.runTest))
