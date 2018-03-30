#!/usr/bin/env python

"""
Copyright (c) 2006-2017 sqlmap developers (http://sqlmap.org/)
See the file 'doc/COPYING' for copying permission
"""

import re

from lib.core.data import kb
from lib.core.enums import PRIORITY

__priority__ = PRIORITY.NORMAL

def dependencies():
    pass

def tamper(payload, **kwargs):
    """
    将小写SQL语句关键字替换为大写

     经测试：
         * Microsoft SQL Server 2005
         * MySQL 4，5.0和5.5
         * Oracle 10g
         * PostgreSQL 8.3,8.4,9.0

     笔记：
         *有助于绕过非常弱的和定制的Web应用程序防火墙
          这是一个写得很差的正则表达式
         *这个篡改脚本可以应对所有(?)数据库

    >>> tamper('insert')
    'INSERT'
    """

    retVal = payload

    if payload:
        for match in re.finditer(r"[A-Za-z_]+", retVal):
            word = match.group()

            if word.upper() in kb.keywords:
                retVal = retVal.replace(word, word.upper())

    return retVal
