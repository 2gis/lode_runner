# -*- coding: utf-8 -*-
import unittest
import optparse
import sys
import json

import os
import re
from nose.config import Config
from lode_runner.plugins.json_reporter import LodeJsonReporter
from lode_runner.core import ContextSuiteFactory

time_taken = re.compile(r'\d\.\d\d')


def mktest():
    class TestCase(unittest.TestCase):
        def runTest(self):
            pass
    test = TestCase()
    test.priority = 'unknown'
    return test


class JsonReporterTest(unittest.TestCase):
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
        suite = ContextSuiteFactory

    def tearDown(self):
        os.unlink(self.reportfile)

    def test_with_unicode_string_in_output(self):
        a = "тест"
        b = u'тест'
        print(a, b)
        self.assertTrue(True)

    def get_json_report(self):
        class DummyStream:
            pass
        self.x.report(DummyStream())
        f = open(self.reportfile, 'r')
        data = f.read()
        f.close()
        return data

    def test_addFailure(self):
        test = mktest()
        self.x.beforeTest(test)
        message = u"%s is not 'equal' to %s" % (u'Тест', u'тест')
        try:
            raise AssertionError(message)
        except AssertionError:
            some_err = sys.exc_info()

        ec, ev, tb = some_err
        some_err = (ec, ev.args[0], tb)

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
        tc_report = {
            u'status': u'fail',
            u'systemerr': u'',
            u'name': u'runTest',
            u'systemout': u'',
            u'actions': [],
            u'classname': u'test_json_reporter.TestCase',
            u'priority': u'unknown'
        }

        self.assertDictContainsSubset(tc_report, tc)
        self.assertTrue(time_taken.match(str(tc['time'])),
                        'Expected decimal time: %s' % tc['time'])

        err = tc['error']
        self.assertEqual(err['type'], "%s.AssertionError" % (AssertionError.__module__,))

        err_lines = err['tb'].strip().split("\n")
        self.assertEqual(err_lines[-1], message)
        self.assertEqual(err_lines[-2], '    raise AssertionError(message)')

    def test_addError(self):
        test = mktest()
        self.x.beforeTest(test)
        message = "some error happened"
        try:
            raise RuntimeError(message)
        except RuntimeError:
            some_err = sys.exc_info()

        ec, ev, tb = some_err
        some_err = (ec, ev.args[0], tb)

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
        tc_report = {
            u'status': u'error',
            u'systemerr': u'',
            u'name': u'runTest',
            u'systemout': u'',
            u'actions': [],
            u'classname': u'test_json_reporter.TestCase',
            u'priority': u'unknown'
        }
        self.assertDictContainsSubset(tc_report, tc)
        self.assertEqual(tc['classname'], "test_json_reporter.TestCase")
        self.assertTrue(time_taken.match(str(tc['time'])),
                        'Expected decimal time: %s' % tc['time'])

        err = tc['error']
        self.assertEqual(err['type'], "%s.RuntimeError" % (RuntimeError.__module__,))
        err_lines = err['tb'].strip().split("\n")
        self.assertIn(message, err_lines[-1])
        self.assertEqual(err_lines[-2], '    raise RuntimeError(message)')

    def test_addSuccess(self):
        test = mktest()
        self.x.beforeTest(test)

        self.x.addSuccess(test)

        result = json.loads(self.get_json_report())

        stats = result['stats']
        self.assertEqual(stats, {
            u'total': 1,
            u'errors': 0,
            u'failures': 0,
            u'skipped': 0,
            u'passes': 1
        })

        tc = result['testcases'][0]
        tc_report = {
            u'status': u'success',
            u'systemerr': u'',
            u'name': u'runTest',
            u'systemout': u'', u'actions': [],
            u'classname': u'test_json_reporter.TestCase',
            u'priority': u'unknown'
        }
        self.assertDictContainsSubset(tc_report, tc)
        self.assertTrue(time_taken.match(str(tc['time'])),
                        'Expected decimal time: %s' % tc['time'])

        self.assertTrue(not tc.get('error'))
