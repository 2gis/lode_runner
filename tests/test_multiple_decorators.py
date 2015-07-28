import unittest

from nose.plugins.attrib import attr
from lode_runner.plugins.dataprovider import dataprovider

tests_to_run = set([
    "test_multiple_decorators_slow_1",
    "test_multiple_decorators_slow_2",
    "test_multiple_decorators_fast_1",
    "test_multiple_decorators_fast_2",
])


class MultipleDecoratorsTest(unittest.TestCase):

    @dataprovider([1, 2])
    @attr(speed='slow')
    def test_multiple_decorators_slow(self, number):
        tests_to_run.remove("%s_%s" % ("test_multiple_decorators_slow", number))

    @attr(speed='fast')
    @dataprovider([1, 2])
    def test_multiple_decorators_fast(self, number):
        tests_to_run.remove("%s_%s" % ("test_multiple_decorators_fast", number))