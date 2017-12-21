#!/usr/bin/env python
#coding=utf-8
"""
Copyright (c) 2006-2017 sqlmap developers (http://sqlmap.org/)
See the file 'doc/COPYING' for copying permission
"""

from lib.core.data import logger
from plugins.generic.enumeration import Enumeration as GenericEnumeration

class Enumeration(GenericEnumeration):
    def __init__(self):
        GenericEnumeration.__init__(self)

    def getBanner(self):
        warnMsg = "在Microsoft Access上，无法获取服务器主机版本信息"
        logger.warn(warnMsg)

        return None

    def getCurrentUser(self):
        warnMsg = "在Microsoft Access上，无法枚举当前用户"
        logger.warn(warnMsg)

    def getCurrentDb(self):
        warnMsg = "在Microsoft Access上，无法获取当前数据库的名称"
        logger.warn(warnMsg)

    def isDba(self):
        warnMsg = "在Microsoft Access上，无法测试当前用户是否为DBA"
        logger.warn(warnMsg)

    def getUsers(self):
        warnMsg = "在Microsoft Access上，无法枚举用户"
        logger.warn(warnMsg)

        return []

    def getPasswordHashes(self):
        warnMsg = "在Microsoft Access上，无法枚举用户密码hash"
        logger.warn(warnMsg)

        return {}

    def getPrivileges(self, *args):
        warnMsg = "在Microsoft Access上，无法枚举用户权限"
        logger.warn(warnMsg)

        return {}

    def getDbs(self):
        warnMsg = "在Microsoft Access上，无法枚举数据库(仅使用 '--tables')"
        logger.warn(warnMsg)

        return []

    def searchDb(self):
        warnMsg = "在Microsoft Access上无法搜索数据库"
        logger.warn(warnMsg)

        return []

    def searchTable(self):
        warnMsg = "在Microsoft Access上，无法搜索表"
        logger.warn(warnMsg)

        return []

    def searchColumn(self):
        warnMsg = "在Microsoft Access上无法搜索列"
        logger.warn(warnMsg)

        return []

    def search(self):
        warnMsg = "在Microsoft Access搜索选项不可用"
        logger.warn(warnMsg)

    def getHostname(self):
        warnMsg = "在Microsoft Access上，无法枚举主机名"
        logger.warn(warnMsg)
