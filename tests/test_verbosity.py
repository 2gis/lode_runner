# -*- coding: utf-8 -*-

import unittest
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from lode_runner import run
from lode_runner.core import LodeRunner
from nose.config import Config
from nose.plugins.manager import DefaultPluginManager


def mksuite():
    class TestCase(unittest.TestCase):
        def runTest(self):
            pass
    test = TestCase()

    return [test]


class TestVerbosity(unittest.TestCase):
    def test_verbosity_1(self):
        stream = StringIO()
        result = run(suite=mksuite(), testRunner=LodeRunner(stream=stream, verbosity=1))
        self.assertEqual(".", stream.getvalue().split("\n")[0])
        self.assertTrue(result)

    def test_verbosity_2(self):
        stream = StringIO()
        result = run(suite=mksuite(), testRunner=LodeRunner(stream=stream, verbosity=2))
        self.assertEqual("runTest (test_verbosity.TestCase) ... ok", stream.getvalue().split("\n")[0])
        self.assertTrue(result)

    def test_verbosity_1_config(self):
        stream = StringIO()
        result = run(suite=mksuite(), config=Config(verbosity=1, stream=stream, plugins=DefaultPluginManager()))
        self.assertEqual(".", stream.getvalue().split("\n")[0])
        self.assertTrue(result)

    def test_verbosity_2_config(self):
        stream = StringIO()
        result = run(suite=mksuite(), config=Config(verbosity=2, stream=stream, plugins=DefaultPluginManager()))
        self.assertEqual("runTest (test_verbosity.TestCase) ... ok", stream.getvalue().split("\n")[0])
        self.assertTrue(result)
