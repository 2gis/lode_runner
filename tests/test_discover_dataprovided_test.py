# coding: utf-8
import unittest
from cStringIO import StringIO

from lode_runner import run
from lode_runner.lode_runner import LodeRunner


class DiscoverTest(unittest.TestCase):
    # TODO: fix dataprovided.pyc caching inside tests
    
    ran_1_test = "Ran 1 test"
    ran_0_test = "Ran 0 test"
    no_such_test = "ValueError: No such test"

    def test_z_discover_dataprovided_test_by_regexp(self):
        stream = StringIO()
        result = run(testRunner=LodeRunner(stream=stream), argv=[
            "lode_runner",
            "--dataproviders-first",
            "-m", "test_with_dataprovider_FIXTURE_2",
            "tests/data/dataprovided/dataprovided.py"])
        self.assertTrue(self.ran_1_test in stream.getvalue(),
                        "\n%s in stream output:\n%s" % (self.ran_1_test, stream.getvalue()))
        self.assertTrue(result)

    def test_z_discover_dataprovided_test_by_name(self):
        stream = StringIO()
        result = run(testRunner=LodeRunner(stream=stream), argv=[
            "lode_runner",
            "--dataproviders-first",
            "tests/data/dataprovided/dataprovided.py:TestCase.test_with_dataprovider_FIXTURE_2"])
        self.assertTrue(self.ran_1_test in stream.getvalue(),
                        "\n%s in stream output:\n%s" % (self.ran_1_test, stream.getvalue()))
        self.assertTrue(result)