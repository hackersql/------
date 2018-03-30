#!/usr/bin/env python
#coding=utf-8
"""
Copyright (c) 2006-2017 sqlmap developers (http://sqlmap.org/)
See the file 'doc/COPYING' for copying permission
"""

from lib.core.data import logger
from lib.core.exception import SqlmapUnsupportedFeatureException
from plugins.generic.enumeration import Enumeration as GenericEnumeration

class Enumeration(GenericEnumeration):
    def __init__(self):
        GenericEnumeration.__init__(self)

    def getCurrentUser(self):
        warnMsg = u"在SQLite上，无法枚举当前用户。"
        logger.warn(warnMsg)

    def getCurrentDb(self):
        warnMsg = u"在SQLite上，不能获取当前数据库的名称。"
        logger.warn(warnMsg)

    def isDba(self):
        warnMsg = u"在SQLite上，当前用户拥有所有权限。"
        logger.warn(warnMsg)

    def getUsers(self):
        warnMsg = u"在SQLite上，无法枚举用户。"
        logger.warn(warnMsg)

        return []

    def getPasswordHashes(self):
        warnMsg = u"在SQLite上，不能枚举用户密码散列（hash）值。"
        logger.warn(warnMsg)

        return {}

    def getPrivileges(self, *args):
        warnMsg = u"在SQLite上，不能枚举用户权限。"
        logger.warn(warnMsg)

        return {}

    def getDbs(self):
        warnMsg = u"在SQLite上，不能枚举数据库(只能使用“--tables”选项)"
        logger.warn(warnMsg)

        return []

    def searchDb(self):
        warnMsg = u"在SQLite上，无法搜索数据库。"
        logger.warn(warnMsg)

        return []

    def searchColumn(self):
        errMsg = u"在SQLite上，无法搜索列。"
        raise SqlmapUnsupportedFeatureException(errMsg)

    def getHostname(self):
        warnMsg = u"在SQLite上，不能枚举主机名。"
        logger.warn(warnMsg)
