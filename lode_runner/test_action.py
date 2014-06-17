import inspect
from time import time
from sys import stdout
from codecs import getwriter
from datetime import datetime

from traceback import format_tb
from unittest.case import SkipTest


def print_debug(stream, message):
    stream.write(message)
    stream.flush()


class TestAction(object):
    testcase = None

    start = None
    end = None
    duration = None
    current_time = None
    result = None
    error = None
    traceback = None

    def __init__(self, text, out=None):
        stack = inspect.stack()
        for f in stack:
            try:
                self.testcase = f[0].f_locals.get('result', None).test
            except AttributeError:
                pass
            else:
                break

        assert self.testcase, "use TestAction inside test case"
        # self.out = getwriter('utf-8')(out)
        self.out = self.testcase.config.stream if not out else out
        self.text = text

    def __enter__(self):
        self.start = time()
        self.current_time = datetime.now().strftime('%H:%M:%S')
        msg = "[%s] %s" % (self.current_time, self.text)
        if self.testcase.config.verbosity > 1:
            print_debug(self.out, msg)

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.end = time()
        self.duration = self.end - self.start
        if exc_type:
            if issubclass(exc_type, SkipTest):
                self.result = 'SKIP'
            else:
                if issubclass(exc_type, AssertionError):
                    self.result = 'FAIL'
                    self.traceback = ''.join(format_tb(exc_tb)[:-1])
                else:
                    self.result = 'ERROR'
                    self.traceback = ''.join(format_tb(exc_tb))
                    self.error = '%s: %s' % (
                        exc_type.__name__, unicode(exc_value)
                    )
        else:
            self.result = 'OK'

        if hasattr(self.testcase, 'test_actions'):
            self.testcase.test_actions.append({
                "text": self.text,
                "start": self.start,
                "end": self.end,
                "duration": self.duration,
                "result": self.result,
                "error": self.error,
                "traceback": self.traceback
            })

        if self.testcase.config.verbosity > 1:
            msg = " ...%s\n" % self.result.lower()
            print_debug(self.out, msg)