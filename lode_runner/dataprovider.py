import logging
import os
import inspect

from nose.plugins import Plugin
log = logging.getLogger('nose.plugins.dataprovider')


class Dataprovider(Plugin):
    name = 'dataprovider'

    def options(self, parser, env=os.environ):
        super(Dataprovider, self).options(parser, env=env)

    def configure(self, options, conf):
        super(Dataprovider, self).configure(options, conf)
        self.enabled = True
        if not self.enabled:
            return

    def makeTest(self, obj, parent):
        tests = []
        if isinstance(obj, list):
            tests = map(parent, obj)
        elif inspect.ismethod(obj):
            tests = [parent(obj.__name__)]

        _tests = []
        for test in tests:
            _tests += _make_dataprovided_tests(test, parent)

        tests = _tests
        _tests = []
        for test in tests:
            _tests += _make_property_provided_tests(test, parent)

        tests = _tests
        if len(tests) > 0:
            return tests


def _data_set_safe_name(data_set):
    try:
        return str(data_set)
    except UnicodeEncodeError:
        return unicode(data_set).encode(encoding='utf-8')


def _make_dataprovided_tests(test, parent):
    testMethod = _get_test_method(test)
    if hasattr(testMethod, '_data_provided'):
        data = testMethod._data_provided
        del testMethod._data_provided
        _data = _prepare_data(data, test)

        dataprovided_tests = []
        for data_set in _data:
            name = testMethod.__name__ + "_" + _data_set_safe_name(data_set)
            new_test_func = _make_func(testMethod, name, data_set)
            setattr(parent, new_test_func.__name__, new_test_func)
            new_test = parent(new_test_func.__name__)
            dataprovided_tests.append(new_test)

        return dataprovided_tests
    else:
        return [test]


def _make_property_provided_tests(test, parent):
    testMethod = _get_test_method(test)
    if hasattr(testMethod, '_property_provided'):
        property_name, data = testMethod._property_provided
        del testMethod._property_provided
        _data = _prepare_data(data, test)

        property_provided_tests = []
        for data_set in _data:
            new_parent = type(parent.__name__ + "_" + _data_set_safe_name(data_set), (parent,), {})
            setattr(new_parent, property_name, data_set)
            name = testMethod.__name__ + "_" + _data_set_safe_name(data_set)
            new_test_func = _make_func(testMethod, name)
            setattr(new_parent, new_test_func.__name__, new_test_func)
            new_test = new_parent(new_test_func.__name__)
            property_provided_tests.append(new_test)

        return property_provided_tests
    else:
        return [test]


def _get_test_method(test):
    return getattr(test, test._testMethodName).__func__


def _make_data(data):
    new_data = data
    return new_data


def _make_func(func, name, data_set=None):
    if not isinstance(data_set, tuple) and data_set:
        data_set = (data_set, )

    if data_set:
        standalone_func = lambda *args: func(*(args + data_set))
    else:
        standalone_func = lambda *args: func(*args)
    standalone_func.__dict__.update(func.__dict__)
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


def property_provider(property_name, data):
    def wrapper(func):
        if inspect.isclass(func):
            for method_name, method in inspect.getmembers(func, predicate=inspect.ismethod):
                method.__func__._property_provided = (property_name, data)
        else:
            func._property_provided = (property_name, data)
        return func
    return wrapper