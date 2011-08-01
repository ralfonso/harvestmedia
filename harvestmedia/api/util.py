# -*- coding: utf-8 -*-

class DictObj(object):
    """
    a dict-like object that provides dot-notation access to its values
    """

    def __getattr__(self, attr):
        return self.__dict__.get(attr)
