# -*- coding: utf-8 -*-

import unittest
from cStringIO import StringIO

from lode_runner import run
from lode_runner.core import LodeRunner


def mksuite():
    class TestCase(unittest.TestCase):
        def runTest(self):
            pass
    test = TestCase()

    return [test]


class TestRun(unittest.TestCase):
    def test_run_suite(self):
        stream = StringIO()
        result = run(suite=mksuite(), testRunner=LodeRunner(stream=stream))
        self.assertTrue(result)