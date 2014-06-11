import logging
import os
import sys

from contesto.basis.test_case import ContestoTestCase


_start_driver = ContestoTestCase._start_driver


class Colors(object):
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'


def print_debug(debug, color=None):
    debug = unicode(debug)
    debug += "\n"

    if color is not None:
        sys.stdout.write(color + debug + Colors.ENDC)
    else:
        sys.stdout.write(debug)
    sys.stdout.flush()


def start_driver(cls, desired_capabilities, command_executor):
    print_debug("START new session", Colors.WARNING)
    print_debug("command_executor%s: %s" % (Colors.ENDC, command_executor), Colors.BLUE)
    print_debug("desired_capabilities%s: %s" % (Colors.ENDC, desired_capabilities), Colors.BLUE)

    driver = _start_driver(desired_capabilities, command_executor)

    capabilities = driver.capabilities
    important_capabilities = {key: capabilities[key] for key in ["platform", "browserName", "version"]}
    print_debug("important_capabilities%s: %s" % (Colors.ENDC, important_capabilities), Colors.BLUE)
    print_debug("session_id%s: %s" % (Colors.ENDC, driver.session_id), Colors.BLUE)
    return driver


def patch():
    ContestoTestCase._start_driver = start_driver


from nose.plugins import Plugin
log = logging.getLogger('nose.plugins.printer')


class ContestoPlugin(Plugin):
    name = 'contesto'

    def options(self, parser, env=os.environ):
        super(ContestoPlugin, self).options(parser, env=env)

    def configure(self, options, conf):
        super(ContestoPlugin, self).configure(options, conf)
        # self.enabled = True
        if not self.enabled:
            return

    def begin(self):
        patch()