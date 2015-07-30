# coding: utf-8

from nose.pyversion import force_unicode


def force_unicode_decorator(func):
    def wrapper(*args, **kwargs):
        return force_unicode(func(*args, **kwargs))
    return wrapper
