# coding: utf-8

import logging

from lode_runner.exceptions import PluginConfigureException
from nose.plugins import Plugin

log = logging.getLogger('lode.plugins.Failer')


class Failer(Plugin):
    name = 'failer'
    enabled = True

    def options(self, parser, env):
        """Sets additional command line options."""
        Plugin.options(self, parser, env)
        parser.add_option(
            '--fail-limit',
            type=int,
            default=env.get('FAIL_LIMIT', None),
            help="Limit of failures/errors to stop after (positive integer)"
        )

    def configure(self, options, conf):
        super(Failer, self).configure(options, conf)
        self.enabled = True
        if not options.fail_limit:
            return

        try:
            fail_limit = int(options.fail_limit)
        except TypeError:
            log.warning("Argument fail_limit wrong integer value \"{}\"".format(options.fail_limit))
            fail_limit = None
        else:
            if fail_limit <= 0:
                raise PluginConfigureException(
                    "Argument fail_limit must be positive integer. Got \"{}\"".format(fail_limit))
        conf.failLimit = fail_limit
