# coding: utf-8

import unittest
from unittest.case import SkipTest
import sys
import optparse
from xml.etree import ElementTree
from StringIO import StringIO

import os
from nose.config import Config
from lode_runner.plugins.xunit import Xunit
from lode_runner.lode_merge_xunit import merge, write_output


def mktest():
    class TestCase(unittest.TestCase):
        def runTest(self):
            pass
    test = TestCase()
    return test


class LodeMergeXunitTest(unittest.TestCase):
    def setUp(self):
        self.xmlfile = os.path.abspath(
            os.path.join(os.path.dirname(__file__), 'xunit.xml'))
        self.stream = StringIO()

    def setup_xunit(self):
        parser = optparse.OptionParser()
        x = Xunit()
        x.add_options(parser, env={})
        (options, args) = parser.parse_args([
            "--with-xunit",
            "--xunit-file=%s" % self.xmlfile
        ])
        x.configure(options, Config())
        return x

    def tearDown(self):
        try:
            os.remove(self.xmlfile)
        except OSError:
            pass

    def get_xml_report(self, xunit):
        class DummyStream:
            pass
        xunit.report(DummyStream())
        f = open(self.xmlfile, 'rb')
        data = f.read()
        f.close()
        return data

    def get_success_report(self):
        x = self.setup_xunit()
        test = mktest()
        x.beforeTest(test)
        x.addSuccess(test)
        result = self.get_xml_report(x)
        return result

    def get_failure_report(self):
        x = self.setup_xunit()
        test = mktest()
        str = u"%s is not 'equal' to %s" % (u'Тест', u'тест')
        try:
            raise AssertionError(str)
        except AssertionError:
            some_err = sys.exc_info()

        ec, ev, tb = some_err
        ev = unicode(ev)
        some_err = (ec, ev, tb)

        x.beforeTest(test)
        x.addFailure(test, some_err)
        result = self.get_xml_report(x)
        return result

    def get_error_report(self):
        x = self.setup_xunit()
        test = mktest()
        str = "some error happened"
        try:
            raise RuntimeError(str)
        except RuntimeError:
            some_err = sys.exc_info()

        ec, ev, tb = some_err
        ev = unicode(ev)
        some_err = (ec, ev, tb)

        x.beforeTest(test)
        x.addError(test, some_err)
        result = self.get_xml_report(x)
        return result

    def get_skip_report(self):
        x = self.setup_xunit()
        test = mktest()
        try:
            raise SkipTest
        except SkipTest:
            some_err = sys.exc_info()

        ec, ev, tb = some_err
        ev = unicode(ev)
        some_err = (ec, ev, tb)

        x.beforeTest(test)
        x.addError(test, some_err)
        result = self.get_xml_report(x)
        return result

    def test_merge_single_root(self):
        report = self.get_success_report()

        report_root = ElementTree.fromstring(report)
        result_root = merge([report_root])
        write_output(result_root, self.stream)
        self.assertEqual(report, self.stream.getvalue())

    def test_merge_with_failed_test_root(self):
        success_report = self.get_success_report()
        failure_report = self.get_failure_report()

        success_report_root = ElementTree.fromstring(success_report)
        failure_report_root = ElementTree.fromstring(failure_report)
        result_root = merge([success_report_root, failure_report_root])
        write_output(result_root, self.stream)
        self.assertEqual(failure_report, self.stream.getvalue())

    def test_merge_with_errored_test_root(self):
        success_report = self.get_success_report()
        error_report = self.get_error_report()

        success_report_root = ElementTree.fromstring(success_report)
        error_report_root = ElementTree.fromstring(error_report)
        result_root = merge([success_report_root, error_report_root])
        write_output(result_root, self.stream)
        self.assertEqual(error_report, self.stream.getvalue())

    def test_merge_with_skipped_test_root(self):
        success_report = self.get_success_report()
        skip_report = self.get_skip_report()

        success_report_root = ElementTree.fromstring(success_report)
        skip_report_root = ElementTree.fromstring(skip_report)
        result_root = merge([success_report_root, skip_report_root])
        write_output(result_root, self.stream)
        self.assertEqual(skip_report, self.stream.getvalue())

    def test_merge_overwrite_error_with_success(self):
        success_report = self.get_success_report()
        error_report = self.get_error_report()

        success_report_root = ElementTree.fromstring(success_report)
        error_report_root = ElementTree.fromstring(error_report)
        result_root = merge([error_report_root, success_report_root])
        write_output(result_root, self.stream)
        self.assertEqual(success_report, self.stream.getvalue())