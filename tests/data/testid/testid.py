# coding: utf-8

import unittest

from lode_runner.plugins.dataprovider import dataprovider


class DataprovidedTestCase(unittest.TestCase):
    @dataprovider([1, 2, 3])
    def test_with_dataprovider_failing_on_everything_except_2(self, data):
        self.assertEqual(2, data)


class AnotherTestCase(unittest.TestCase):
    @dataprovider([1, 2, 3])
    def test_nothing(self, data):
        pass