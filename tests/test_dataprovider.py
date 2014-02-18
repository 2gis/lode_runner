import unittest

from lode_runner.dataprovider import dataprovider


tests_to_run = set([
    "test_data_dataprovider_1",
    "test_data_dataprovider_2",
    "test_data_dataprovider_3",
    "test_method_dataprovider_2",
    "test_method_dataprovider_3",
    "test_method_dataprovider_4",
])


class DataproviderTest(unittest.TestCase):
    @staticmethod
    def data_method():
        value = 2
        return [x + value for x in (0, 1, 2)]

    @dataprovider([
        1, 2, 3
    ])
    def test_data_dataprovider(self, data):
        tests_to_run.remove("%s_%s" % ("test_data_dataprovider", data))

    @dataprovider(
        data_method
    )
    def test_method_dataprovider(self, data):
        tests_to_run.remove("%s_%s" % ("test_method_dataprovider", data))