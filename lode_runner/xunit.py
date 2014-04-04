from nose.plugins.xunit import Xunit, Tee
from cStringIO import StringIO
import sys


class Tee(Tee):
    def write(self, *args):
        _args = ()
        for arg in args:
            if isinstance(arg, unicode):
                arg = arg.encode('utf-8')
            _args += (arg, )
        super(Tee, self).write(*_args)


class Xunit(Xunit):
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