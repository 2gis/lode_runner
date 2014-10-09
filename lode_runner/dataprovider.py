import logging
import os
import inspect
import copy
import collections
import re
import sys
import unittest

from nose.plugins import Plugin
log = logging.getLogger('nose.plugins.dataprovider')


class CustomString(object):
    def __init__(self, string):
        self.string = string

    def __repr__(self):
        _tmp = repr(self.string)
        string = _to_str(self.string)
        new_repr = re.sub("'.+'", "'" + string + "'", _tmp)
        return new_repr

    def __str__(self):
        return self.string

    def __radd__(self, other):
        return other + self.__repr__()


class Dataprovider(Plugin):
    name = 'dataprovider'

    def options(self, parser, env):
        """Sets additional command line options."""
        Plugin.options(self, parser, env)
        parser.add_option('--dataproviders-first', action="store_true",
                          default=env.get('DATAPROVIDERS_FIRST', False),
                          dest="dataproviders_first",
                          help="If set, will call dataproviders, "
                               "when before finding tests."
                               "[DATAPROVIDERS_FIRST]")

    def configure(self, options, conf):
        super(Dataprovider, self).configure(options, conf)
        f = bool(options.dataproviders_first)
        conf.dataproviders_first = f
        self.enabled = True
        if not self.enabled:
            return

    def _build_dataprovided_tests_in_module(self, module):
        if not self.conf.dataproviders_first:
            return

        _is_test = re.compile(self.conf.testMatchPat)
        for name, obj in inspect.getmembers(module):
            if isinstance(obj, type):
                if not unittest.TestCase in obj.__bases__:
                    continue

                test_case = obj
                methods = [method for method in dir(test_case) if
                           hasattr(getattr(test_case, method), "__call__")
                           and not method.startswith("_")]
                methods = [method for method in methods if _is_test.match(method)]
                tests = [method for method in methods if
                         hasattr(getattr(test_case(method), test_case(method)._testMethodName), '__func__')]

                if tests:
                    self.makeTest(tests, test_case)

    def loadTestsFromName(self, name, module=None, discovered=False):
        """ Overrided to call dataproviders
        """
        if module is None:
            return None

        self._build_dataprovided_tests_in_module(module)
        return None

    def loadTestsFromModule(self, module, path=None, discovered=False):
        self._build_dataprovided_tests_in_module(module)
        return None

    def makeTest(self, obj, parent):
        tests = []
        if isinstance(obj, list):
            tests = map(parent, obj)
        elif inspect.ismethod(obj):
            tests = [parent(obj.__name__)]

        _tests = []
        while tests:
            test = tests.pop(0)
            _test = _make_property_provided_tests(test)
            if _test == [test]:
                _tests += _test
            else:
                tests += _test

        tests = _tests

        _tests = []
        for test in tests:
            _tests += _make_dataprovided_tests(test)

        tests = _tests
        if len(tests) > 0:
            return tests


def _to_str(value, custom=False):
    if custom:
        return CustomString(value)
    else:
        try:
            return str(value)
        except UnicodeEncodeError:
            return value.encode(encoding='utf-8')


def _convert(data):
    if isinstance(data, basestring):
        return _to_str(data, True)
    elif isinstance(data, tuple) and hasattr(data, '_asdict'):  # Handle namedtuple
        return dict(map(_convert, data._asdict().iteritems()))
    elif isinstance(data, collections.Mapping):
        return dict(map(_convert, data.iteritems()))
    elif isinstance(data, collections.Iterable):
        return type(data)(map(_convert, data))
    else:
        return data


def _data_set_safe_name(data_set):
    if hasattr(data_set, "__iter__"):
        data_set = _convert(data_set)
    result = _to_str(data_set)
    result = result.replace("/", "<slash>").replace("\\", "<backslash>").replace(".", "<dot>").replace(":", "<colon>")
    return result


def _make_dataprovided_tests(test):
    parent = test.__class__
    testMethod = _get_test_method(test)
    if hasattr(testMethod, '_data_provided'):
        data = testMethod._data_provided
        del testMethod._data_provided
        _data = _prepare_data(data, test)

        dataprovided_tests = []
        for i, data_set in enumerate(_data):
            safe_name = _data_set_safe_name(data_set)
            # name = testMethod.__name__ + "_" + str(i)
            name = testMethod.__name__ + "_" + safe_name
            new_test_func = _make_func(testMethod, name, data_set)
            setattr(parent, new_test_func.__name__, new_test_func)
            new_test = parent(new_test_func.__name__)
            dataprovided_tests.append(new_test)

        delattr(parent, testMethod.__name__)

        return dataprovided_tests
    else:
        return [test]


def _make_property_provided_tests(test):
    parent = test.__class__
    testMethod = _get_test_method(test)
    if hasattr(testMethod, '_property_provided'):
        property_name, data = testMethod._property_provided.pop(0)
        _data = _prepare_data(data, test)

        property_provided_tests = []
        for data_set in _data:
            new_parent_name = parent.__name__ + "_" + _data_set_safe_name(data_set)
            if hasattr(sys.modules[parent.__module__], new_parent_name):
                new_parent = getattr(sys.modules[parent.__module__], new_parent_name)
            else:
                new_parent = type(new_parent_name, (parent,), {'__module__': parent.__module__})
                setattr(sys.modules[new_parent.__module__], new_parent_name, new_parent)

            name = testMethod.__name__ + "_" + _data_set_safe_name(data_set)
            setattr(new_parent, property_name, data_set)

            new_test_func = _make_func(testMethod, name)
            if new_test_func._property_provided == []:
                del new_test_func._property_provided
            setattr(new_parent, new_test_func.__name__, new_test_func)
            new_test = new_parent(new_test_func.__name__)
            property_provided_tests.append(new_test)

        delattr(parent, testMethod.__name__)
        delattr(sys.modules[parent.__module__], parent.__name__)

        return property_provided_tests
    else:
        return [test]


def _get_test_method(test):
    return getattr(test, test._testMethodName).__func__


def _make_data(data):
    new_data = data
    return new_data


def _make_func(func, name, data_set=None):
    if data_set and not isinstance(data_set, tuple):
        data_set = (data_set, )

    if data_set:
        standalone_func = lambda *args: func(*(args + data_set))
    else:
        standalone_func = lambda *args: func(*args)
    standalone_func.__dict__.update(copy.deepcopy(func.__dict__))
    standalone_func.__name__ = name
    return standalone_func


def _prepare_data(data, test):
    if callable(data):
        if len(inspect.getargspec(data).args):
            _data = data(test)
        else:
            _data = data()
    elif isinstance(data, staticmethod):
        _data = data.__func__()
    else:
        _data = data
    if not isinstance(_data, list):
        raise TypeError("make data iterable using list []")

    return _data


def dataprovider(data):
    def wrapper(func):
        if inspect.isclass(func):
            for method_name, method in inspect.getmembers(func, predicate=inspect.ismethod):
                method.__func__._data_provided = data
        else:
            func._data_provided = data
        return func
    return wrapper


def _add_property(func, property_name, data):
    if hasattr(func, '_property_provided'):
        func._property_provided += [(property_name, data)]
    else:
        func._property_provided = [(property_name, data)]


def property_provider(property_name, data):
    def wrapper(func):
        if inspect.isclass(func):
            for method_name, method in inspect.getmembers(func, predicate=inspect.ismethod):
                _add_property(method.__func__, property_name, data)
        else:
            _add_property(func, property_name, data)
        return func
    return wrapper