# -*- coding: utf-8 -*-

import unittest

from lode_runner.dataprovider import dataprovider


tests_to_run = [
    "test_data_dataprovider_1",
    "test_data_dataprovider_2",
    "test_data_dataprovider_3",
    "test_method_dataprovider_1",
    "test_method_dataprovider_2",
    "test_method_dataprovider_3",
    "test_function_dataprovider_1",
    "test_function_dataprovider_2",
    "test_function_dataprovider_3",
    u"test_unicode_string_dataprovider_первый",
    u"test_unicode_string_dataprovider_второй"
]


def function_provider():
    return [1, 2, 3]


class DataproviderTest(unittest.TestCase):
    def setUp(self):
        self.value = 1

    @dataprovider([
        1, 2, 3
    ])
    def test_data_dataprovider(self, data):
        tests_to_run.remove("%s_%s" % ("test_data_dataprovider", data))

    def method_provider(self):
        self.setUp()
        value = self.value
        return [(x + value) for x in (0, 1, 2)]

    @dataprovider(
        method_provider
    )
    def test_method_dataprovider(self, data):
        tests_to_run.remove("%s_%s" % ("test_method_dataprovider", data))

    @dataprovider(
        function_provider
    )
    def test_function_dataprovider(self, data):
        tests_to_run.remove("%s_%s" % ("test_function_dataprovider", data))

    @dataprovider([
        u'первый',
        u'второй',
    ])
    def test_unicode_string_dataprovider(self, data):
        tests_to_run.remove("%s_%s" % ("test_unicode_string_dataprovider", data))