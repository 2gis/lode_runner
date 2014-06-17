# -*- coding: utf-8 -*-
import unittest
import cStringIO

from lode_runner import TestAction


def temp(test_action):
    with test_action:
        pass


class TestActionTest(unittest.TestCase):
    """
    Common use is:
    from lode_runner import TestAction


    class Test(unittest.TestCase):
        def test(self):
            with TestAction(u"doing stuff"):
                do_stuff()

            with TestAction(u"doing another stuff"):
                do_another_stuff()

            with TestAction(u"making assertions"):
                self.assertTrue(True)
                self.assertFalse(False)
    """

    def setUp(self):
        self._resultForDoCleanups.config.verbosity = 2

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

    def test_error_test_action(self):
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
        self.assertEquals("...error", parts.pop(0))

    def test_fail_test_action(self):
        msg = u"test_action_message"
        output = cStringIO.StringIO()
        test_action = TestAction(msg, output)
        try:
            with test_action:
                self.assertTrue(False)
        except AssertionError:
            pass
        parts = output.getvalue().split()
        time = test_action.current_time

        self.assertEquals("[%s]" % time, parts.pop(0))
        self.assertEquals(msg, parts.pop(0))
        self.assertEquals("...fail", parts.pop(0))

    def test_test_action_in_function(self):
        msg = u"test_action_message"
        output = cStringIO.StringIO()
        test_action = TestAction(msg, output)
        temp(test_action)
        parts = output.getvalue().split()
        time = test_action.current_time

        self.assertEquals("[%s]" % time, parts.pop(0))
        self.assertEquals(msg, parts.pop(0))
        self.assertEquals("...ok", parts.pop(0))