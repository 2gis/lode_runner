# -*- coding: utf-8 -*-

import unittest

from lode_runner.dataprovider import property_provider
from lode_runner.dataprovider import dataprovider


tests_to_run = [
    "test_property_provider_json",
    "test_property_provider_xml",
    "test_class_property_provider_json",
    "test_class_property_provider_xml",
    "test_property_provider_and_dataprovider_1_json",
    "test_property_provider_and_dataprovider_1_xml",
    "test_property_provider_and_dataprovider_2_json",
    "test_property_provider_and_dataprovider_2_xml"
]


class PropertyProviderTest(unittest.TestCase):
    # just to show how can we make pretty property provider
    from functools import partial
    request_type = partial(property_provider, 'request_type')

    @request_type(['json', 'xml'])
    def test_property_provider(self):
        tests_to_run.remove("%s_%s" % ("test_property_provider", self.request_type))


@property_provider('request_type', ['json', 'xml'])
class ClassPropertyProviderTest(unittest.TestCase):
    def test_class_property_provider(self):
        tests_to_run.remove("%s_%s" % ("test_class_property_provider", self.request_type))


class PropertyProviderAndDataproviderTest(unittest.TestCase):
    @dataprovider([1, 2])
    @property_provider('request_type', ['json', 'xml'])
    def test_property_provider_and_dataprovider(self, data):
        tests_to_run.remove("%s_%s_%s" % ("test_property_provider_and_dataprovider", data, self.request_type))


class TestAllTestsRan(unittest.TestCase):
    def test_all_tests_ran(self):
        self.assertEqual([], tests_to_run)