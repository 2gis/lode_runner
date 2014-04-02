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
    "test_unicode_string_dataprovider_Первый Тест",
    u"test_unicode_string_dataprovider_Второй Тест",
    "test_class_dataprovider_1",
    "test_class_dataprovider_2",
    "test_class_dataprovider_3",
    "test_dict_dataprovider_{'two': u'второй тест', 'one': 'первый тест'}",
    "test_list_dataprovider_['первый тест', u'второй тест']",
    "test_tuple_dataprovider_('первый тест', u'второй тест')",
]


def function_provider():
    return [1, 2, 3]


class DataproviderTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.set_up_class_called = True

    def setUp(self):
        self.set_up_called = True

    @dataprovider([1, 2, 3])
    def test_data_dataprovider(self, data):
        tests_to_run.remove("%s_%s" % ("test_data_dataprovider", data))

    @property
    def value(self):
        return 1

    def method_provider(self):
        value = self.value
        return [(x + value) for x in (0, 1, 2)]

    @dataprovider(method_provider)
    def test_method_dataprovider(self, data):
        tests_to_run.remove("%s_%s" % ("test_method_dataprovider", data))

    @dataprovider(function_provider)
    def test_function_dataprovider(self, data):
        tests_to_run.remove("%s_%s" % ("test_function_dataprovider", data))

    @dataprovider(['Первый Тест', u"Второй Тест"])
    def test_unicode_string_dataprovider(self, data):
        tests_to_run.remove("%s_%s" % ("test_unicode_string_dataprovider", data))

    @dataprovider([(55.028748, 82.936757, 18, 'data.attributes.filials,data.attributes.sight,data.geometry.selection', 'parking', u'Парковка ТРЦ Аура', u'Военная, 5Подземная, 2 этажа Общедоступная, платная первые 3 часа - бесплатно 1600 мест')])
    def test_failed_test_with_unicode_string_in_dataprovider(self, data):
        print data
        self.assertTrue(False)

    @dataprovider([1])
    def test_setup_runs(self, data):
        self.assertTrue(self.set_up_called)
        self.assertTrue(self.set_up_class_called)


class NestedDataprovidersTest(unittest.TestCase):
    @dataprovider([['первый тест', u'второй тест']])
    def test_list_dataprovider(self, data):
        list_string = "['%s', u'%s']" % (data[0], data[1].encode('utf-8'))
        tests_to_run.remove("%s_%s" % ("test_list_dataprovider", list_string))

    @dataprovider([{'one': 'первый тест', 'two': u'второй тест'}])
    def test_dict_dataprovider(self, data):
        l = list(data.iteritems())
        key1, value1 = l[0]
        key2, value2 = l[1]
        dict_string = "{'%s': u'%s', '%s': '%s'}" % (key1, value1.encode('utf-8'), key2, value2)
        test_name = "%s_%s" % ("test_dict_dataprovider", dict_string)
        tests_to_run.remove(test_name)

    @dataprovider([('первый тест', u'второй тест')])
    def test_tuple_dataprovider(self, data):
        tuple_string = "('%s', u'%s')" % (data[0], data[1].encode('utf-8'))
        tests_to_run.remove("%s_%s" % ("test_tuple_dataprovider", tuple_string))


@dataprovider([1, 2, 3])
class ClassDataproviderTest(unittest.TestCase):
    def test_class_dataprovider(self, data):
        tests_to_run.remove("%s_%s" % ("test_class_dataprovider", data))


class TestAllTestsRan(unittest.TestCase):
    def test_all_tests_ran(self):
        self.assertEqual([], tests_to_run)
