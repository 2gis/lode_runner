# coding: utf-8

import logging
import sys
from functools import wraps

from nose.plugins import Plugin
log = logging.getLogger('nose.plugins.initializer')


def initializer(test):
    @wraps(test)
    def wrapper(*args, **kwargs):
        initialize = getattr(test.__self__, 'initialize', lambda: None)
        finalize = getattr(test.__self__, 'finalize', lambda: None)
        initialize()
        try:
            result = test(*args, **kwargs)
        finally:
            finalize()
        return result
    return wrapper


def _get_test_method(test):
    return getattr(test.test, test.test._testMethodName)


def _set_test_method(test, method):
    setattr(test.test, test.test._testMethodName, method)


class Initializer(Plugin):
    name = 'initializer'
    enabled = True

    def options(self, parser, env):
        """Sets additional command line options."""
        Plugin.options(self, parser, env)

    def configure(self, options, conf):
        super(Initializer, self).configure(options, conf)
        self.enabled = True
        if not self.enabled:
            return

    def beforeTest(self, test):
        test_method = _get_test_method(test)
        _set_test_method(test, initializer(test_method))