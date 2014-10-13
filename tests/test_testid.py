# -*- coding: utf-8 -*-
import unittest
import os
import optparse
from cStringIO import StringIO

from nose.config import Config
from nose.plugins import PluginManager

from lode_runner.testid import parse_test_name
from lode_runner.lode_runner import TestLoader, LodeTestResult, Dataprovider, TestId


class TestIdTest(unittest.TestCase):
    tests_location = "tests/data/testid/testid.py"
    idfile_location = "data/testid/.noseids"

    def setUp(self):
        self.idfile = os.path.abspath(
            os.path.join(os.path.dirname(__file__), self.idfile_location))
        parser = optparse.OptionParser()
        argv = [
            "--failed",
            "--with-id",
            "--id-file=%s" % self.idfile
        ]
        self.x = TestId()
        self.x.add_options(parser, env={})
        (options, args) = parser.parse_args(argv)
        self.config = Config()
        self.x.configure(options, self.config)
        self.config.plugins = PluginManager()
        self.config.plugins.addPlugin(Dataprovider())
        self.config.plugins.addPlugin(TestId())
        self.config.configure(argv)

    def tearDown(self):
        try:
            os.remove(self.idfile)
        except OSError:
            pass

    def test_load_tests_path_with_no_info_in_idfile(self):
        names = self.x.loadTestsFromNames([self.tests_location])
        self.assertEqual((None, [self.tests_location]), names)

    def test_loaded_names_with_failing_tests_in_idfile(self):
        stream = StringIO()

        tests = TestLoader(config=self.config).loadTestsFromName(self.tests_location)
        result = LodeTestResult(stream, None, 0)
        tests.run(result)
        # generate needed idfile
        self.config.plugins.finalize(result)

        names = self.x.loadTestsFromNames([self.tests_location])
        loaded_tests = [(parse_test_name(name)[1], parse_test_name(name)[2]) for name in names[1]]
        self.assertEqual(
            [('DataprovidedTestCase','test_with_dataprovider_failing_on_everything_except_2_1'),
             ('DataprovidedTestCase','test_with_dataprovider_failing_on_everything_except_2_3')], loaded_tests)