# -*- coding: utf-8 -*-
import unittest
import os
import sys
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from lode_runner.plugins.dataprovider import Dataprovider
from lode_runner.core import TestLoader, LodeTestResult

from nose.config import Config
from nose.plugins import PluginManager
from nose.failure import Failure


PY2 = sys.version_info[0] == 2

verbose_test_names = [
    "test_class_dataprovider_1 (dataprovided.ClassDataproviderTest)",
    "test_class_dataprovider_2 (dataprovided.ClassDataproviderTest)",
    "test_class_dataprovider_3 (dataprovided.ClassDataproviderTest)",
    "test_function_dataprovider_1 (dataprovided.DataproviderTest)",
    "test_function_dataprovider_2 (dataprovided.DataproviderTest)",
    "test_function_dataprovider_3 (dataprovided.DataproviderTest)",
    "test_method_dataprovider_1 (dataprovided.DataproviderTest)",
    "test_method_dataprovider_2 (dataprovided.DataproviderTest)",
    "test_method_dataprovider_3 (dataprovided.DataproviderTest)",
    "test_raw_dataprovider_1 (dataprovided.DataproviderTest)",
    "test_raw_dataprovider_2 (dataprovided.DataproviderTest)",
    "test_raw_dataprovider_3 (dataprovided.DataproviderTest)",
    "test_single_dataprovider_('<dot>1', '<slash>2') (dataprovided.DataproviderTest)",
    "test_unicode_string_dataprovider_Первый Тест (dataprovided.DataproviderTest)",
    "test_unicode_string_dataprovider_Второй Тест (dataprovided.DataproviderTest)",
]

if PY2:
    verbose_test_names += [
        "test_dict_dataprovider_OrderedDict([('one', u'первый тест'), ('two', u'второй тест')]) (dataprovided.NestedDataprovidersTest)",
        "test_list_dataprovider_[u'первый тест', u'второй тест'] (dataprovided.NestedDataprovidersTest)",
        "test_namedtuple_dataprovider_(NamedTuple(one=u'первый тест', two=u'второй тест'),) (dataprovided.NestedDataprovidersTest)",
        "test_tuple_dataprovider_(u'первый тест', u'второй тест') (dataprovided.NestedDataprovidersTest)",
    ]
else:
    verbose_test_names += [
        "test_dict_dataprovider_OrderedDict([('one', 'первый тест'), ('two', 'второй тест')]) (dataprovided.NestedDataprovidersTest)",
        "test_list_dataprovider_['первый тест', 'второй тест'] (dataprovided.NestedDataprovidersTest)",
        "test_namedtuple_dataprovider_(NamedTuple(one='первый тест', two='второй тест'),) (dataprovided.NestedDataprovidersTest)",
        "test_tuple_dataprovider_('первый тест', 'второй тест') (dataprovided.NestedDataprovidersTest)",
    ]


class BaseDataproviderTest(unittest.TestCase):
    path = os.path.dirname(os.path.realpath(__file__)) + "/data/dataprovided/dataprovided.py"
    test = "test_raw_dataprovider_with_dataset_1"
    test_case = "DataproviderTest"
    test_full_name = "%s:%s.%s" % (path, test_case, test)
    ran_1_test = "Ran 1 test"
    no_such_test = "ValueError: No such test"

    def cleanup(self):
        del sys.modules["dataprovided"]
        self.argv = []

    def setUp(self):
        self.addCleanup(self.cleanup)
        self.config = Config()
        self.config.plugins = PluginManager()
        self.config.plugins.addPlugin(Dataprovider())
        self.argv = []
        # 0 is always should be program name
        self.argv.append("lode_runner")
        self.config.configure(self.argv)


class DataproviderTest(BaseDataproviderTest):
    def test_all_tests_discovered(self):
        stream = StringIO()
        tests = TestLoader(config=self.config).loadTestsFromName(self.path)
        result = LodeTestResult(stream, None, 0)
        tests.run(result)
        self.assertTrue(result.wasSuccessful(), result.errors + result.failures)
        self.assertEqual(19, result.testsRun)

    def test_dataprovider_names(self):
        tests = TestLoader(config=self.config).loadTestsFromName(self.path)
        extracted_tests = list()
        for suite in tests:
            for test in suite:
                extracted_tests.append(test)
        self.assertEqual([
            "test_class_dataprovider_with_dataset_0 (dataprovided.ClassDataproviderTest)",
            "test_class_dataprovider_with_dataset_1 (dataprovided.ClassDataproviderTest)",
            "test_class_dataprovider_with_dataset_2 (dataprovided.ClassDataproviderTest)",
            "test_function_dataprovider_with_dataset_0 (dataprovided.DataproviderTest)",
            "test_function_dataprovider_with_dataset_1 (dataprovided.DataproviderTest)",
            "test_function_dataprovider_with_dataset_2 (dataprovided.DataproviderTest)",
            "test_method_dataprovider_with_dataset_0 (dataprovided.DataproviderTest)",
            "test_method_dataprovider_with_dataset_1 (dataprovided.DataproviderTest)",
            "test_method_dataprovider_with_dataset_2 (dataprovided.DataproviderTest)",
            "test_raw_dataprovider_with_dataset_0 (dataprovided.DataproviderTest)",
            "test_raw_dataprovider_with_dataset_1 (dataprovided.DataproviderTest)",
            "test_raw_dataprovider_with_dataset_2 (dataprovided.DataproviderTest)",
            "test_single_dataprovider_with_dataset_0 (dataprovided.DataproviderTest)",
            "test_unicode_string_dataprovider_with_dataset_0 (dataprovided.DataproviderTest)",
            "test_unicode_string_dataprovider_with_dataset_1 (dataprovided.DataproviderTest)",
            "test_dict_dataprovider_with_dataset_0 (dataprovided.NestedDataprovidersTest)",
            "test_list_dataprovider_with_dataset_0 (dataprovided.NestedDataprovidersTest)",
            "test_namedtuple_dataprovider_with_dataset_0 (dataprovided.NestedDataprovidersTest)",
            "test_tuple_dataprovider_with_dataset_0 (dataprovided.NestedDataprovidersTest)",
        ], [str(test) for test in extracted_tests])

    def test_dataprovider_verbose_names(self):
        self.argv.append("--dataproviders-verbose")
        self.config.configure(self.argv)
        tests = TestLoader(config=self.config).loadTestsFromName(self.path)
        extracted_tests = list()
        for suite in tests:
            for test in suite:
                extracted_tests.append(test)
        self.assertEqual(verbose_test_names, [str(test) for test in extracted_tests])


class DiscoverWithDataprovidersFirstTest(BaseDataproviderTest):
    def setUp(self):
        super(DiscoverWithDataprovidersFirstTest, self).setUp()
        self.argv.append("--dataproviders-first")
        self.config.configure(self.argv)

    def test_discover_dataprovided_test_by_regexp(self):
        stream = StringIO()
        self.argv.append("-m")
        self.argv.append(self.test)
        self.config.configure(self.argv)
        tests = TestLoader(config=self.config).loadTestsFromName(self.path)
        result = LodeTestResult(stream, None, 0)
        tests.run(result)
        self.assertTrue(result.wasSuccessful(), result.errors + result.failures)
        self.assertEqual(1, result.testsRun)

    def test_success_discover_dataprovided_test_by_name(self):
        stream = StringIO()
        tests = TestLoader(config=self.config).loadTestsFromName(self.test_full_name)
        result = LodeTestResult(stream, None, 0)
        tests.run(result)
        self.assertEqual(1, result.testsRun)
        self.assertEqual([], result.errors)
        self.assertTrue(result.wasSuccessful())


class DiscoverWithoutDataprovidersFirstTest(BaseDataproviderTest):
    def test_fail_discover_dataprovided_test_by_name(self):
        stream = StringIO()
        tests = TestLoader(config=self.config).loadTestsFromName(self.test_full_name)
        result = LodeTestResult(stream, None, 0)
        tests.run(result)
        self.assertEqual(1, result.testsRun)
        self.assertEqual(1, len(result.errors))
        failure = result.errors[0][0]
        self.assertIsInstance(failure.test, Failure)
        self.assertEqual("Failure: ValueError (No such test %s.%s)" % (self.test_case, self.test), str(failure))
        self.assertFalse(result.wasSuccessful())
