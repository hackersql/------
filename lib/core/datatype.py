#!/usr/bin/env python
#coding=utf-8

"""
Copyright (c) 2006-2017 sqlmap developers (http://sqlmap.org/)
See the file 'doc/COPYING' for copying permission
"""

import copy
import types

class AttribDict(dict):
    """
    这个类定义了sqlmap对象，它继承了Python数据类型字典。

    >>> foo = AttribDict()
    >>> foo.bar = 1
    >>> foo.bar
    1
    """

    def __init__(self, indict=None, attribute=None):
        if indict is None:
            indict = {}     # 初始化一个空字典{}

        # 在此处设置任何属性-在初始之前将它们保留为正常属性
        self.attribute = attribute
        dict.__init__(self, indict)
        self.__initialised = True

        # 初始化后，设置属性attribute与设置item相同

    def __getattr__(self, item):
        """
        __getattr__ 在访问对象访问类中不存在的成员时会自动调用

        """

        try:
            return self.__getitem__(item)
        except KeyError:
            raise AttributeError("无法访问'%s'item成员，可能是类或对象中没有定义" % item)

    def __setattr__(self, item, value):
        """
        只有在初始化时才将属性映射到值
        __setattr__ 方法用于在初始化对象成员的时候调用，
        即在设置__dict__的item时就会调用__setattr__方法。
        """

        # 此测试允许在__init__方法中设置属性
        if "_AttribDict__initialised" not in self.__dict__:
            return dict.__setattr__(self, item, value)

        # 正常属性正常处理
        elif item in self.__dict__:
            dict.__setattr__(self, item, value)

        else:
            self.__setitem__(item, value)

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, dict):
        self.__dict__ = dict

    def __deepcopy__(self, memo):
        retVal = self.__class__()
        memo[id(self)] = retVal

        for attr in dir(self):
            if not attr.startswith('_'):
                value = getattr(self, attr)
                if not isinstance(value, (types.BuiltinFunctionType, types.FunctionType, types.MethodType)):
                    setattr(retVal, attr, copy.deepcopy(value, memo))

        for key, value in self.items():
            retVal.__setitem__(key, copy.deepcopy(value, memo))

        return retVal

class InjectionDict(AttribDict):
    def __init__(self):
        AttribDict.__init__(self)

        self.place = None
        self.parameter = None
        self.ptype = None
        self.prefix = None
        self.suffix = None
        self.clause = None
        self.notes = []  # Note: https://github.com/sqlmapproject/sqlmap/issues/1888

        # data是一个具有各种类型的dict，每个都是一个dict，所有的信息特定于该类型
        self.data = AttribDict()

        # conf是一个存储当前快照的dict
        # 检测期间使用的选项
        # conf是一个dict，用于存储检测期间使用的重要选项的当前快照
        self.conf = AttribDict()

        self.dbms = None
        self.dbms_version = None
        self.os = None
