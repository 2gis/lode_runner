import sys
import codecs
import multiprocessing
from time import time

from StringIO import StringIO

from nose.plugins.xunit import Xunit, Tee


MANAGER = multiprocessing.Manager()
MP_ERRORLIST = MANAGER.list()
MP_STATS = MANAGER.dict()


class Tee(Tee):
    def write(self, *args):
        _args = ()
        for arg in args:
            if isinstance(arg, unicode):
                arg = arg.encode('utf-8')
            _args += (arg, )
        super(Tee, self).write(*_args)


class Xunit(Xunit):
    def configure(self, options, config):
        """Configures the xunit plugin."""
        super(Xunit, self).configure(options, config)
        self.config = config
        if self.enabled:
            if hasattr(options, 'multiprocess_workers') and options.multiprocess_workers:
                self.stats = MP_STATS
                self.stats.update(
                    {'errors': 0,
                     'failures': 0,
                     'passes': 0,
                     'skipped': 0})
                self.errorlist = MP_ERRORLIST
            else:
                super(Xunit, self).configure(options, config)
            self.error_report_filename = options.xunit_file

    def beforeTest(self, test):
        """Initializes a timer before starting a test."""
        self._timer = time()
        self._startCapture()

    def _startCapture(self):
        self._capture_stack.append((sys.stdout, sys.stderr))
        self._currentStdout = StringIO()
        self._currentStderr = StringIO()
        sys.stdout = Tee(self._currentStdout, sys.stdout)
        sys.stderr = Tee(self._currentStderr, sys.stderr)

    def addError(self, test, err, capt=None):
        ec, ev, tb = err
        if isinstance(ev, unicode):
            ev = ev.encode(self.encoding)
        err = (ec, ev, tb)
        super(Xunit, self).addError(test, err, capt)

    def addFailure(self, test, err, capt=None, tb_info=None):
        ec, ev, tb = err
        if isinstance(ev, unicode):
            ev = ev.encode(self.encoding)
        err = (ec, ev, tb)
        super(Xunit, self).addFailure(test, err, capt, tb_info)

    def report(self, stream):
        """Writes an Xunit-formatted XML file

        The file includes a report of test errors and failures.

        """
        self.error_report_file = codecs.open(self.error_report_filename, 'w',
                                             self.encoding, 'replace')
        self.stats['encoding'] = self.encoding
        self.stats['total'] = (self.stats['errors'] + self.stats['failures']
                               + self.stats['passes'] + self.stats['skipped'])
        self.error_report_file.write(
            u'<?xml version="1.0" encoding="%(encoding)s"?>'
            u'<testsuite name="nosetests" tests="%(total)d" '
            u'errors="%(errors)d" failures="%(failures)d" '
            u'skip="%(skipped)d">' % self.stats)
        self.error_report_file.write(u''.join([
            self._forceUnicode(error) for error in self.errorlist
        ]))

        self.error_report_file.write(u'</testsuite>')
        self.error_report_file.close()
        if self.config.verbosity > 1:
            stream.writeln("-" * 70)
            stream.writeln("XML: %s" % self.error_report_file.name)