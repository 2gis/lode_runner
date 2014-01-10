from time import time
from sys import stdout
from codecs import getwriter
from datetime import datetime


class TestAction(object):
    def __init__(self, text, out=stdout):
        self.out = getwriter('utf-8')(out)
        self.text = text

    def __enter__(self):
        self._start = time()
        self.current_time = datetime.now().strftime('%H:%M:%S')
        msg = "[%s] %s" % (self.current_time, self.text)
        self.out.write(msg)
        self.out.flush()

    def __exit__(self, exc_type, exc_val, exc_tb):
        _end = time()
        _duration = _end - self._start
        if exc_type:
            msg = "  ...fail\n"
        else:
            msg = "  ...ok\n"

        self.out.write(msg)
        self.out.flush()