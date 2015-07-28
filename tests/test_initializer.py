# coding: utf-8
import unittest

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from lode_runner import run
from lode_runner.core import LodeRunner


teardown_to_run = [
    "ErrorInInitializerTest",
    "FinalizeTest",
    "ErrorInFinalizeTest"
]


class InitializeTest(unittest.TestCase):
    def initialize(self):
        self.foo = 1

    def test_initializer(self):
        self.assertEqual(1, self.foo)


class NoInitializeTest(unittest.TestCase):
    def test_no_initializer(self):
        pass


def mksuite():
    class ErrorInInitializerTest(unittest.TestCase):
        def initialize(self):
            raise Exception("asdf")

        def runTest(self):
            pass

        def tearDown(self):
            teardown_to_run.remove("%s" % (self.__class__.__name__))

    class FinalizeTest(unittest.TestCase):
        def finalize(self):
            self.foo = 1

        def runTest(self):
            raise Exception("asdf")

        def tearDown(self):
            assert self.foo == 1
            teardown_to_run.remove("%s" % (self.__class__.__name__))

    class ErrorInFinalizeTest(unittest.TestCase):
        def finalize(self):
            raise Exception("asdf")

        def runTest(self):
            pass

        def tearDown(self):
            teardown_to_run.remove("%s" % (self.__class__.__name__))

    return [ErrorInInitializerTest(), FinalizeTest(), ErrorInFinalizeTest()]


class TestInitializerAllTeardownsRan(unittest.TestCase):
    def test_all_teardowns_ran(self):
        stream = StringIO()
        run(suite=mksuite(), testRunner=LodeRunner(stream=stream))
        self.assertEqual([], teardown_to_run)