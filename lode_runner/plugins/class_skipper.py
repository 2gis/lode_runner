# coding: utf-8

from nose.plugins import Plugin
from nose.exc import SkipTest


class ClassSkipper(Plugin):
    name = 'class_skipper'
    enabled = True

    def configure(self, options, conf):
        super(ClassSkipper, self).configure(options, conf)
        self.enabled = True

    def startContext(self, context):
        if getattr(context, '__unittest_skip__', False):
            raise SkipTest(getattr(context, '__unittest_skip_why__', 'Unknown skip reason'))
