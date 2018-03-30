#!/usr/bin/env python
#coding=utf-8

class AttribDict(dict):

    def __init__(self, indict=None, attribute=None):
        if indict is None:
            indict = {}

        #在这里设置任何属性 - 在初始化之前
        #这些仍然是正常的属性
        self.attribute = attribute
        dict.__init__(self, indict)
        self.__initialised = True

        #初始化后，设置属性
        #与设置项相同

    def __getattr__(self, item):
        """
        Maps values to attributes
        Only called if there *is NOT* an attribute with this name
        将值映射到属性仅在*不是*具有此名称的属性时调用

        """

        try:
            return self.__getitem__(item)
        except KeyError:
            raise AttributeError("无法访问'%s'项" % item)

    def __setattr__(self, item, value):
        """
        仅当我们被初始化时将属性映射到值

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

        #conf是一个存储当前快照的dict
        #检测期间使用的选项
        self.conf = AttribDict()

        self.dbms = None
        self.dbms_version = None
        self.os = None
