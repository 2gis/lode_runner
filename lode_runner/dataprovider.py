import logging
import os

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

        _tests = []
        for test in tests:
            testMethod = getattr(test, test._testMethodName)
            if hasattr(testMethod, '_data_provided'):
                data = testMethod._data_provided

                _data = prepare_data(data)

                dataprovided_tests = []
                for data_set in _data:
                    name = testMethod.__name__ + "_" + str(data_set)
                    new_test_func = make_func(testMethod, name, data_set)
                    setattr(parent, new_test_func.__name__, new_test_func)
                    new_test = parent(new_test_func.__name__)
                    dataprovided_tests.append(new_test)

                _tests += dataprovided_tests
            else:
                _tests += [test]

        tests = _tests

        if len(tests) > 0:
            return tests


def make_func(func, name, data_set):
    if not isinstance(data_set, tuple):
        data_set = (data_set, )

    standalone_func = lambda *a: func(*(data_set))
    standalone_func.__name__ = name
    return standalone_func


def prepare_data(data):
    if callable(data):
        _data = data()
    elif isinstance(data, staticmethod):
        _data = data.__func__()
    else:
        _data = data
    if not isinstance(_data, list):
        raise TypeError("make data iterable using list []")

    return _data


def dataprovider(data):
    def decorator(func):
        func._data_provided = data
        return func
    return decorator