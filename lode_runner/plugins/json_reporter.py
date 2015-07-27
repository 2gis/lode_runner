import logging
import os
import sys
import codecs
import re
import inspect
import traceback
import json
from time import time
from cStringIO import StringIO

from nose.plugins import Plugin
from nose.exc import SkipTest
from nose.pyversion import UNICODE_STRINGS


log = logging.getLogger('nose.plugins.lode_json_reporter')

# Invalid XML characters, control characters 0-31 sans \t, \n and \r
CONTROL_CHARACTERS = re.compile(r"[\000-\010\013\014\016-\037]")

TEST_ID = re.compile(r'^(.*?)(\(.*\))$')


def id_split(idval):
    m = TEST_ID.match(idval)
    if m:
        name, fargs = m.groups()
        head, tail = name.rsplit(".", 1)
        return [head, tail+fargs]
    else:
        return idval.rsplit(".", 1)


def nice_classname(obj):
    """Returns a nice name for class object or class instance.

        >>> nice_classname(Exception()) # doctest: +ELLIPSIS
        '...Exception'
        >>> nice_classname(Exception) # doctest: +ELLIPSIS
        '...Exception'

    """
    if inspect.isclass(obj):
        cls_name = obj.__name__
    else:
        cls_name = obj.__class__.__name__
    mod = inspect.getmodule(obj)
    if mod:
        name = mod.__name__
        # jython
        if name.startswith('org.python.core.'):
            name = name[len('org.python.core.'):]
        return "%s.%s" % (name, cls_name)
    else:
        return cls_name


def exc_message(exc_info):
    """Return the exception's message."""
    exc = exc_info[1]
    if exc is None:
        # str exception
        result = exc_info[0]
    else:
        try:
            result = str(exc)
        except UnicodeEncodeError:
            try:
                result = unicode(exc)
            except UnicodeError:
                # Fallback to args as neither str nor
                # unicode(Exception(u'\xe6')) work in Python < 2.6
                result = exc.args[0]
    return result


def format_exception(exc_info):
    ec, ev, tb = exc_info

    # formatError() may have turned our exception object into a string, and
    # Python 3's traceback.format_exception() doesn't take kindly to that (it
    # expects an actual exception object).  So we work around it, by doing the
    # work ourselves if ev is a string.
    if isinstance(ev, basestring):
        tb_data = ''.join(traceback.format_tb(tb))
        return tb_data + ev
    else:
        return ''.join(traceback.format_exception(*exc_info))


class Tee(object):
    def __init__(self, *args):
        self._streams = args

    def write(self, *args):
        _args = ()
        for arg in args:
            if isinstance(arg, unicode):
                arg = arg.encode('utf-8')
            _args += (arg, )

        for s in self._streams:
            s.write(*_args)

    def flush(self):
        for s in self._streams:
            s.flush()


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