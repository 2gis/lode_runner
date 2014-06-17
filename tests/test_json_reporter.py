# -*- coding: utf-8 -*-
import unittest
import os
import optparse
import sys
import re
import json

from nose.config import Config

from lode_runner.json_reporter import LodeJsonReporter


time_taken = re.compile(r'\d\.\d\d')


def mktest():
    class TestCase(unittest.TestCase):
        def runTest(self):
            pass
    test = TestCase()
    return test


class XunitTest(unittest.TestCase):
    def setUp(self):
        self.reportfile = os.path.abspath(
            os.path.join(os.path.dirname(__file__), 'report.json'))
        parser = optparse.OptionParser()
        self.x = LodeJsonReporter()
        self.x.add_options(parser, env={})
        (options, args) = parser.parse_args([
            "--with-lodejson",
            "--lode-report=%s" % self.reportfile
        ])
        self.x.configure(options, Config())

    def tearDown(self):
        os.unlink(self.reportfile)

    def test_with_unicode_string_in_output(self):
        a = "тест"
        b = u'тест'
        print a, b
        self.assertTrue(True)

    def get_json_report(self):
        class DummyStream:
            pass
        self.x.report(DummyStream())
        f = open(self.reportfile, 'rb')
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

        result = json.loads(self.get_json_report())
        stats = result['stats']
        self.assertEqual(stats, {
            u'total': 1,
            u'errors': 0,
            u'failures': 1,
            u'skipped': 0,
            u'passes': 0
        })

        tc = result['testcases'][0]
        self.assertEqual(tc['classname'], u"test_json_reporter.TestCase")
        self.assertEqual(tc['name'], "runTest")
        self.assertTrue(time_taken.match(unicode(tc['time'])),
                        'Expected decimal time: %s' % tc['time'])

        err = tc['error']
        self.assertEqual(err['type'], "%s.AssertionError" % (AssertionError.__module__,))

        err_lines = err['tb'].strip().split("\n")
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

        result = json.loads(self.get_json_report())

        stats = result['stats']
        self.assertEqual(stats, {
            u'total': 1,
            u'errors': 1,
            u'failures': 0,
            u'skipped': 0,
            u'passes': 0
        })

        tc = result['testcases'][0]
        self.assertEqual(tc['classname'], "test_json_reporter.TestCase")
        self.assertEqual(tc['name'], "runTest")
        self.assertTrue(time_taken.match(unicode(tc['time'])),
                        'Expected decimal time: %s' % tc['time'])

        err = tc['error']
        self.assertEqual(err['type'], "%s.RuntimeError" % (RuntimeError.__module__,))
        err_lines = err['tb'].strip().split("\n")
        self.assertEqual(err_lines[-1], str)
        self.assertEqual(err_lines[-2], '    raise RuntimeError(str)')