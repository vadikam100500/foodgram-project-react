from functools import update_wrapper

from django.utils.decorators import _multi_decorate


def multi_method_decorator(decorator, names):

    def _dec(obj):
        for name in names:
            method = getattr(obj, name)
            _wrapper = _multi_decorate(decorator, method)
            setattr(obj, name, _wrapper)
        return obj

    if not hasattr(decorator, '__iter__'):
        update_wrapper(_dec, decorator)
    obj = decorator if hasattr(decorator, '__name__') else decorator.__class__
    _dec.__name__ = 'method_decorator(%s)' % obj.__name__
    return _dec
