# coding: utf-8

import logging
from functools import wraps
from nose.plugins import Plugin

log = logging.getLogger('lode.plugins.suppressor')


def suppress_exceptions(func):
    @wraps(func)
    def wrapped_tear_down(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            log.exception('Suppressed error in {} {}'.format(func.__name__, func))

    return wrapped_tear_down


class Suppressor(Plugin):
    """
    Suppressor plugin: if enabled - suppress all exceptions in tearDown-like methods.
    """
    name = 'suppressor'
    enabled = True

    def options(self, parser, env):
        Plugin.options(self, parser, env)
        parser.add_option(
            '--suppress-teardown-exceptions',
            action='store_true',
            default=False,
            help="Suppress any exceptions in tearDown/tearDownClass-like methods"
        )

    def configure(self, options, conf):
        if not options.suppress_teardown_exceptions:
            return

        conf.suppressTearDownExceptions = options.suppress_teardown_exceptions
