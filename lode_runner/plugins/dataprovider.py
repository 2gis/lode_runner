import logging
import inspect
import types
import collections
import re
import sys
import unittest

from functools import update_wrapper, wraps
from lode_runner.plugins import force_unicode_decorator
from nose.pyversion import ismethod, unbound_method
from nose.plugins import Plugin

log = logging.getLogger('lode.plugins.dataprovider')

if sys.version_info[:2] < (3, 0):
    def isstring(s):
        return isinstance(s, basestring)
else:
    def isstring(s):
        return isinstance(s, str)


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
                          help="Call dataproviders before tests collecting."
                               "[DATAPROVIDERS_FIRST]")
        parser.add_option('--dataproviders-verbose', action="store_true",
                          default=env.get('DATAPROVIDERS_VERBOSE', False),
                          dest="dataproviders_verbose",
                          help="Show dataproviders data by inserting it into test names"
                               "[DATAPROVIDERS_VERBOSE]")
        parser.add_option('--log-test-arguments', action="store_true",
                          default=env.get('LOG_TEST_ARGUMENTS', False),
                          dest="log_test_arguments",
                          help="Enable logging arguments passed in test"
                               "[LOG_TEST_ARGUMENTS]")

    def configure(self, options, conf):
        super(Dataprovider, self).configure(options, conf)
        conf.dataproviders_first = bool(options.dataproviders_first)
        conf.dataproviders_verbose = bool(options.dataproviders_verbose)
        conf.log_test_arguments = bool(options.log_test_arguments)
        self.enabled = True
        if not self.enabled:
            return
        self.is_test = re.compile(self.conf.testMatchPat)

    def prepareTestLoader(self, test_loader):
        self.importer = test_loader.importer

    def beforeImport(self, filename, module_name):
        try:
            module = self.importer.importFromPath(
                filename, module_name)
        except:
            module = None
        if module:
            self.loadTestsFromModule(module)

    def loadTestsFromName(self, name, module=None, discovered=False):
        if module is None:
            return None

        self.loadTestsFromModule(module)

    def loadTestsFromModule(self, module, path=None, discovered=False):
        if not self.conf.dataproviders_first:
            return

        for name, obj in inspect.getmembers(module):
            if isinstance(obj, type):
                if not _has_parent(obj, unittest.TestCase):
                    continue

                self.loadTestsFromTestCase(obj)

    def loadTestsFromTestCase(self, test_case):
        methods = [method for method in dir(test_case) if
                   callable(getattr(test_case, method)) and self.is_test.match(method)]

        self._expand_tests(methods, test_case)

    def makeTest(self, obj, parent):
        tests = self._expand_tests(obj, parent)

        _tests = []
        if tests:
            for test in tests:
                _test = parent(test)
                _test.id = force_unicode_decorator(_test.id)
                _tests.append(_test)

            return _tests

    def _expand_tests(self, obj, parent):
        if inspect.isfunction(obj) and parent and not isinstance(parent, types.ModuleType):
            # This is a Python 3.x 'unbound method'.  Wrap it with its
            #  associated class..
            obj = unbound_method(parent, obj)

        tests = []
        if isinstance(obj, list):
            tests = obj
        elif ismethod(obj):
            tests = [obj.__name__]

        _tests = []
        for test in tests:
            _tests += self._make_dataprovided_tests(parent, test)

        return _tests

    def _make_dataprovided_tests(self, parent, test):
        testMethod = _get_test_method(parent, test)
        if self.conf.log_test_arguments:
            testMethod = _log_test_arguments(testMethod)
        if hasattr(testMethod, '_data_provided'):
            data = testMethod._data_provided
            del testMethod._data_provided
            _data = _prepare_data(data, parent)

            dataprovided_tests = []
            for num, data_set in enumerate(_data):
                if self.conf.dataproviders_verbose:
                    safe_name = _data_set_safe_name(data_set)
                else:
                    safe_name = "with_dataset_%s" % num
                name = testMethod.__name__ + "_" + safe_name
                new_test_func = _make_func(testMethod, name, data_set)
                setattr(parent, new_test_func.__name__, new_test_func)
                dataprovided_tests.append(name)

            delattr(parent, testMethod.__name__)

            return dataprovided_tests
        else:
            return [test]


def _log_test_arguments(test):
    @wraps(test)
    def wrapper(*args, **kwargs):
        names = inspect.getargspec(test).args
        arguments = ['%s=%s' % (name, arg) for (name, arg) in zip(names, args) if name != 'self']
        log.info('Test arguments: ' + ', '.join(arguments))
        return test(*args, **kwargs)
    return wrapper


def _has_parent(obj, parent):
    if parent in obj.__bases__:
        return True

    for base in obj.__bases__:
        return _has_parent(base, parent)

    return False


def _to_str(value, custom=False):
    if custom:
        return CustomString(value)
    else:
        try:
            return str(value)
        except UnicodeEncodeError:
            return value.encode(encoding='utf-8')


def _convert(data):
    if isstring(data):
        return _to_str(data, True)
    elif isinstance(data, tuple) and hasattr(data, '_asdict'):  # Handle namedtuple
        items = iter(data._asdict().values())
        return type(data)(*map(_convert, items))
    elif isinstance(data, collections.Mapping):
        items = iter(data.items())
        return type(data)(map(_convert, items))
    elif isinstance(data, collections.Iterable):
        return type(data)(map(_convert, data))
    else:
        return data


def _data_set_safe_name(data_set):
    if hasattr(data_set, "__iter__"):
        data_set = _convert(data_set)
    result = _to_str(data_set)
    result = result. \
        replace("/", "<slash>"). \
        replace("\\", "<backslash>"). \
        replace(".", "<dot>"). \
        replace(":", "<colon>")
    return result


def _get_test_method(parent, test):
    test_method = getattr(parent, test)
    if not inspect.isfunction(test_method):
        test_method = test_method.__func__
    return test_method


def _make_data(data):
    new_data = data
    return new_data


def _make_func(func, name, data_set=None):
    if data_set and not isinstance(data_set, tuple):
        data_set = (data_set,)

    if data_set:
        standalone_func = lambda *args: func(*(args + data_set))
    else:
        standalone_func = lambda *args: func(*args)
    update_wrapper(standalone_func, func)
    standalone_func.__name__ = name
    return standalone_func


def _prepare_data(data, parent):
    if callable(data):
        _data = data()
    elif isinstance(data, staticmethod):
        _data = data.__func__()
    elif isinstance(data, classmethod):
        _data = data.__func__(parent)
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
            for method_name, method in inspect.getmembers(func, predicate=inspect.isfunction):
                method._data_provided = data
        else:
            func._data_provided = data
        return func

    return wrapper
