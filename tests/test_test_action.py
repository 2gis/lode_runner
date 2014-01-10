# -*- coding: utf-8 -*-
import unittest
import cStringIO

from lode_runner import TestAction


class TestActionTest(unittest.TestCase):

    def test_ok_test_action(self):
        msg = u"test_action_message"
        output = cStringIO.StringIO()
        test_action = TestAction(msg, output)
        with test_action:
            pass
        parts = output.getvalue().split()
        time = test_action.current_time

        self.assertEquals("[%s]" % time, parts.pop(0))
        self.assertEquals(msg, parts.pop(0))
        self.assertEquals("...ok", parts.pop(0))

    def test_failing_test_action(self):
        asdf
        msg = u"test_action_message"
        output = cStringIO.StringIO()
        test_action = TestAction(msg, output)
        try:
            with test_action:
                raise Exception("some exception")
        except Exception:
            pass
        parts = output.getvalue().split()
        time = test_action.current_time

        self.assertEquals("[%s]" % time, parts.pop(0))
        self.assertEquals(msg, parts.pop(0))
        self.assertEquals("...fail", parts.pop(0))

    def test_some(self):
        with TestAction(u'asdf'):
            pass