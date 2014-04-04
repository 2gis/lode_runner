# -*- coding: utf-8 -*-
import unittest
import os
import optparse
import sys
import re

from nose.config import Config

from lode_runner.xunit import Xunit


time_taken = re.compile(r'\d\.\d\d')


def mktest():
    class TestCase(unittest.TestCase):
        def runTest(self):
            pass
    test = TestCase()
    return test


class XunitTest(unittest.TestCase):
    def setUp(self):
        self.xmlfile = os.path.abspath(
            os.path.join(os.path.dirname(__file__), 'xunit.xml'))
        parser = optparse.OptionParser()
        self.x = Xunit()
        self.x.add_options(parser, env={})
        (options, args) = parser.parse_args([
            "--with-xunit",
            "--xunit-file=%s" % self.xmlfile
        ])
        self.x.configure(options, Config())

        try:
            import xml.etree.ElementTree
        except ImportError:
            self.ET = False
        else:
            self.ET = xml.etree.ElementTree

    def tearDown(self):
        os.unlink(self.xmlfile)

    def test_with_unicode_string_in_output(self):
        a = "тест"
        b = u'тест'
        print a, b
        self.assertTrue(True)

    def get_xml_report(self):
        class DummyStream:
            pass
        self.x.report(DummyStream())
        f = open(self.xmlfile, 'rb')
        data = f.read()
        f.close()
        return data

    def test_addFailure(self):
        test = mktest()
        self.x.beforeTest(test)
        str = u"%s is not 'equal' to %s" % (u'Тест', u'тест')
        try:
            raise AssertionError(str)
        except AssertionError:
            some_err = sys.exc_info()

        ec, ev, tb = some_err
        ev = unicode(ev)
        some_err = (ec, ev, tb)

        self.x.addFailure(test, some_err)

        result = self.get_xml_report()
        print result

        if self.ET:
            tree = self.ET.fromstring(result)
            self.assertEqual(tree.attrib['name'], "nosetests")
            self.assertEqual(tree.attrib['tests'], "1")
            self.assertEqual(tree.attrib['errors'], "0")
            self.assertEqual(tree.attrib['failures'], "1")
            self.assertEqual(tree.attrib['skip'], "0")

            tc = tree.find("testcase")
            self.assertEqual(tc.attrib['classname'], "test_xunit.TestCase")
            self.assertEqual(tc.attrib['name'], "runTest")
            assert time_taken.match(tc.attrib['time']), (
                        'Expected decimal time: %s' % tc.attrib['time'])

            err = tc.find("failure")
            self.assertEqual(err.attrib['type'], "%s.AssertionError" % (AssertionError.__module__,))
            err_lines = err.text.strip().split("\n")
            print err_lines
            self.assertEqual(err_lines[-1], str)
            self.assertEqual(err_lines[-2], '    raise AssertionError(str)')

    def test_addError(self):
        test = mktest()
        self.x.beforeTest(test)
        str = "some error happened"
        try:
            raise RuntimeError(str)
        except RuntimeError:
            some_err = sys.exc_info()

        ec, ev, tb = some_err
        ev = unicode(ev)
        some_err = (ec, ev, tb)

        self.x.addError(test, some_err)

        result = self.get_xml_report()
        print result

        if self.ET:
            tree = self.ET.fromstring(result)
            self.assertEqual(tree.attrib['name'], "nosetests")
            self.assertEqual(tree.attrib['tests'], "1")
            self.assertEqual(tree.attrib['errors'], "1")
            self.assertEqual(tree.attrib['failures'], "0")
            self.assertEqual(tree.attrib['skip'], "0")

            tc = tree.find("testcase")
            self.assertEqual(tc.attrib['classname'], "test_xunit.TestCase")
            self.assertEqual(tc.attrib['name'], "runTest")
            assert time_taken.match(tc.attrib['time']), (
                        'Expected decimal time: %s' % tc.attrib['time'])

            err = tc.find("error")
            self.assertEqual(err.attrib['type'], "%s.RuntimeError" % (RuntimeError.__module__,))
            err_lines = err.text.strip().split("\n")
            print err_lines
            self.assertEqual(err_lines[-1], str)
            self.assertEqual(err_lines[-2], '    raise RuntimeError(str)')