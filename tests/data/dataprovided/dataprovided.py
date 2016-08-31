# coding: utf-8

import unittest
from collections import namedtuple, OrderedDict

from lode_runner.plugins.dataprovider import dataprovider


def function_provider():
    return [1, 2, 3]


class DataproviderTest(unittest.TestCase):
    @classmethod
    def method_provider(cls):
        return [1, 2, 3]

    @dataprovider([1, 2, 3])
    def test_raw_dataprovider(self, data):
        pass

    @dataprovider(method_provider)
    def test_method_dataprovider(self, data):
        pass

    @dataprovider(function_provider)
    def test_function_dataprovider(self, data):
        pass

    @dataprovider([u'Первый Тест', u'Второй Тест'])
    def test_unicode_string_dataprovider(self, data):
        pass

    @dataprovider([
        ('.1', '/2'),
    ])
    def test_single_dataprovider(self, data1, data2):
        pass


class NestedDataprovidersTest(unittest.TestCase):
    @dataprovider([[u'первый тест', u'второй тест']])
    def test_list_dataprovider(self, data):
        pass

    @dataprovider([
        OrderedDict([('one', u'первый тест'), ('two', u'второй тест')])
    ])
    def test_dict_dataprovider(self, data):
        pass

    @dataprovider([(u'первый тест', u'второй тест')])
    def test_tuple_dataprovider(self, first, second):
        pass

    NamedTuple = namedtuple('NamedTuple', 'one two')
    @dataprovider([(NamedTuple(u'первый тест', u'второй тест'),)])
    def test_namedtuple_dataprovider(self, data):
        pass


@dataprovider([1, 2, 3])
class ClassDataproviderTest(unittest.TestCase):
    def test_class_dataprovider(self, data):
        pass
