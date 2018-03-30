#!/usr/bin/env python
#coding=utf-8

"""
Copyright (c) 2006-2017 sqlmap developers (http://sqlmap.org/)
See the file 'doc/COPYING' for copying permission
"""

from lib.core.datatype import AttribDict
from lib.core.log import LOGGER

# sqlmap路径
paths = AttribDict()

# 存储原始命令行选项
cmdLineOptions = AttribDict()

# 存储合并选项的对象（命令行，配置文件和默认选项）
mergedOptions = AttribDict()

# 要在函数和类中共享的对象命令行选项和设置
conf = AttribDict()

# 要在函数和类结果中共享的对象
kb = AttribDict()

# 查询每个数据库管理系统的具体对象
queries = {}

# logger
logger = LOGGER
