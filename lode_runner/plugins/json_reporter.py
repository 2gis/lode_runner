import logging
import os
import sys
import codecs
import json
from time import time
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from nose.plugins import Plugin
from nose.plugins.xunit import id_split, nice_classname, format_exception, exc_message, Tee
from nose.exc import SkipTest
from nose.pyversion import UNICODE_STRINGS


log = logging.getLogger('nose.plugins.lode_json_reporter')


class LodeJsonReporter(Plugin):
    name = 'lodejson'
    encoding = 'UTF-8'
    report_file = None

    def __init__(self):
        super(LodeJsonReporter, self).__init__()
        self._capture_stack = []
        self._currentStdout = None
        self._currentStderr = None

    def options(self, parser, env=os.environ):
        """Sets additional command line options."""
        Plugin.options(self, parser, env)
        parser.add_option(
            '--lode-report', action='store',
            dest='lode_report', metavar="FILE",
            default=env.get('LODE_REPORT_FILE', 'lode-report.json'),
            help=("Path to xml file to store the lode report in. "
                  "Default is lode-report.xml in the working directory "
                  "[LODE_REPORT_FILE]"))

    def configure(self, options, config):
        super(LodeJsonReporter, self).configure(options, config)
        self.config = config
        if self.enabled:
            self.stats = {
                'errors': 0,
                'failures': 0,
                'passes': 0,
                'skipped': 0
            }
            self.testcases = []
            self.report_file = codecs.open(
                options.lode_report, 'w', self.encoding, 'replace'
            )

    def _timeTaken(self):
        if hasattr(self, '_timer'):
            taken = time() - self._timer
        else:
            # test died before it ran (probably error in setup())
            # or success/failure added before test started probably
            # due to custom TestResult munging
            taken = 0.0
        return taken

    def report(self, stream):
        self.stats['total'] = (self.stats['errors'] + self.stats['failures']
                               + self.stats['passes'] + self.stats['skipped'])

        report = dict()
        report['encoding'] = self.encoding
        report['stats'] = self.stats
        report['testcases'] = [testcase for testcase in self.testcases]
        self.report_file.write(json.dumps(report))
        self.report_file.close()

    def _startCapture(self):
        self._capture_stack.append((sys.stdout, sys.stderr))
        self._currentStdout = StringIO()
        self._currentStderr = StringIO()
        sys.stdout = Tee(self._currentStdout, sys.stdout)
        sys.stderr = Tee(self._currentStderr, sys.stderr)

    def startContext(self, context):
        self._startCapture()

    def beforeTest(self, test):
        test.test_actions = list()
        self._timer = time()
        self._startCapture()

    def _endCapture(self):
        if self._capture_stack:
            sys.stdout, sys.stderr = self._capture_stack.pop()

    def afterTest(self, test):
        self._endCapture()
        self._currentStdout = None
        self._currentStderr = None

    def finalize(self, test):
        while self._capture_stack:
            self._endCapture()

    def _getCapturedStdout(self):
        if self._currentStdout:
            value = self._currentStdout.getvalue()
            if value:
                return value
        return ''

    def _getCapturedStderr(self):
        if self._currentStderr:
            value = self._currentStderr.getvalue()
            if value:
                return value
        return ''

    def form_test_report(self, test, err=None, status=None):
        time = self._timeTaken()
        id = test.id()
        actions = test.test_actions
        priority = test.priority

        if not status:
            status = 'success'

        report = {
            'classname': id_split(id)[0],
            'name': id_split(id)[-1],
            'actions': actions,
            'time': time,
            'status': status,
            'priority': priority,
            'systemout': self._getCapturedStdout(),
            'systemerr': self._getCapturedStderr(),
        }

        if err:
            report['error'] = {
                'type': nice_classname(err[0]),
                'message': exc_message(err),
                'tb': format_exception(err),
            }

        self.testcases.append(report)

    def addError(self, test, err, capt=None):
        if issubclass(err[0], SkipTest):
            status = 'skipped'
            self.stats['skipped'] += 1
        else:
            status = 'error'
            self.stats['errors'] += 1

        self.form_test_report(test, err, status)

    def addFailure(self, test, err, capt=None, tb_info=None):
        self.stats['failures'] += 1
        status = 'fail'

        self.form_test_report(test, err, status)

    def addSuccess(self, test, capt=None):
        self.stats['passes'] += 1
        self.form_test_report(test)

    def _forceUnicode(self, s):
        if not UNICODE_STRINGS:
            if isinstance(s, str):
                s = s.decode(self.encoding, 'replace')
        return s