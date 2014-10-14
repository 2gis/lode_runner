# coding: utf-8

import unittest
from lode_runner.dataprovider import dataprovider


class TestCase(unittest.TestCase):
    @dataprovider([1, 2, 3])
    def test_with_dataprovider_fixture(self, data):
        pass


class MasterTestCase(unittest.TestCase):
    pass


class SubTestCase(MasterTestCase):
    @dataprovider([1])
    def test_sub_testcase_with_dataprovider(self, data):
        pass