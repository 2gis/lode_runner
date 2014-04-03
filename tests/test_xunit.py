# -*- coding: utf-8 -*-
import unittest

from lode_runner.dataprovider import dataprovider


class XunitTest(unittest.TestCase):
    @dataprovider([
        (55.028748, 82.936757, 18, 'data.attributes.filials,data.attributes.sight,data.geometry.selection',
         'parking', u'Парковка ТРЦ Аура',
         u'Военная, 5Подземная, 2 этажа Общедоступная, платная первые 3 часа - бесплатно 1600 мест'),
    ])
    def test_failed_test_with_unicode_string_in_output(self, data):
        print "тест"
        print u'тест'
        self.assertTrue(True)
