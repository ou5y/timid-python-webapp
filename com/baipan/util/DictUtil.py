# !C:\Python27\python.exe
# -*- coding: UTF-8 -*-

__author__ = '5y'
'''自定义字典类'''


class Dict(dict):
    def __init__(self, names=(), values=(), **kw):
        super(Dict, self).__init__(**kw)
        for k, v in zip(names, values):  # 为了弥补dict中没有Dict(('a', 'b', 'c'), (1, 2, 3))这类初始化方式的缺陷
            self[k] = v

    def __getattr__(self, key):
        try:
            return self[key]  # 为了弥补dict中只能dict['name']，不能直接dict.name的缺陷
        except KeyError:
            raise AttributeError(r"'Dict' object has no attribute '%s'" % key)

    def __setattr__(self, key, value):
        self[key] = value
