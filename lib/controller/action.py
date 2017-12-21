#!/usr/bin/env python
#coding=utf-8
"""
Copyright (c) 2006-2017 sqlmap developers (http://sqlmap.org/)
See the file 'doc/COPYING' for copying permission
"""

from lib.controller.handler import setHandler
from lib.core.common import Backend
from lib.core.common import Format
from lib.core.data import conf
from lib.core.data import kb
from lib.core.data import logger
from lib.core.data import paths
from lib.core.enums import CONTENT_TYPE
from lib.core.exception import SqlmapNoneDataException
from lib.core.exception import SqlmapUnsupportedDBMSException
from lib.core.settings import SUPPORTED_DBMS
from lib.utils.brute import columnExists
from lib.utils.brute import tableExists

def action():
    """
    此函数利用受影响URL参数上的SQL注入，并在可能的情况下从后端数据库管理系统或操作系统中提取请求的数据。
    """

    # 首先，我们必须确定后端数据库管理系统能够进行注入
    setHandler()

    if not Backend.getDbms() or not conf.dbmsHandler:
        htmlParsed = Format.getErrorParsedDBMSes()

        errMsg = u"sqlmap无法对后端数据库管理系统进行指纹识别 "

        if htmlParsed:
            errMsg += u", 但是从HTML错误页面可以确定后端DBMS是 %s" % htmlParsed

        if htmlParsed and htmlParsed.lower() in SUPPORTED_DBMS:
            errMsg += u". 不要手动指定后端DBMS,sqlmap将为您指定DBMS "
        elif kb.nullConnection:
            errMsg += u". 您可以尝试重新运行而不使用优化 "
            errMsg += "switch '%s'" % ("-o" if conf.optimize else "--null-connection")

        raise SqlmapUnsupportedDBMSException(errMsg)

    conf.dumper.singleString(conf.dbmsHandler.getFingerprint())

    # Enumeration options
    # 获取服务器主机的版本信息Windows/linux
    if conf.getBanner:
        conf.dumper.banner(conf.dbmsHandler.getBanner())
    # 获取当前用户
    if conf.getCurrentUser:
        conf.dumper.currentUser(conf.dbmsHandler.getCurrentUser())
    # 获取当前数据库
    if conf.getCurrentDb:
        conf.dumper.currentDb(conf.dbmsHandler.getCurrentDb())
    # 获取主机名
    if conf.getHostname:
        conf.dumper.hostname(conf.dbmsHandler.getHostname())
    # 判断当前用户是否是DBA用户
    if conf.isDba:
        conf.dumper.dba(conf.dbmsHandler.isDba())
    # 获取数据库用户
    if conf.getUsers:
        conf.dumper.users(conf.dbmsHandler.getUsers())
    # 获取数据库用户密码哈希
    if conf.getPasswordHashes:
        try:
            conf.dumper.userSettings(u"数据库管理系统用户密码哈希", conf.dbmsHandler.getPasswordHashes(), u"密码哈希", CONTENT_TYPE.PASSWORDS)
        except SqlmapNoneDataException, ex:
            logger.critical(ex)
        except:
            raise
    # 获取数据库用户权限
    if conf.getPrivileges:
        try:
            conf.dumper.userSettings(u"数据库管理系统用户权限", conf.dbmsHandler.getPrivileges(), u"权限", CONTENT_TYPE.PRIVILEGES)
        except SqlmapNoneDataException, ex:
            logger.critical(ex)
        except:
            raise
    # 获取数据库管理系统用户角色
    if conf.getRoles:
        try:
            conf.dumper.userSettings(u"数据库管理系统用户角色", conf.dbmsHandler.getRoles(), u"角色", CONTENT_TYPE.ROLES)
        except SqlmapNoneDataException, ex:
            logger.critical(ex)
        except:
            raise
    # 获取所有数据库
    if conf.getDbs:
        conf.dumper.dbs(conf.dbmsHandler.getDbs())

    if conf.getTables:
        conf.dumper.dbTables(conf.dbmsHandler.getTables())

    if conf.commonTables:
        conf.dumper.dbTables(tableExists(paths.COMMON_TABLES))
    # 获取数据库管理系统架构
    if conf.getSchema:
        conf.dumper.dbTableColumns(conf.dbmsHandler.getSchema(), CONTENT_TYPE.SCHEMA)
    # 获取列
    if conf.getColumns:
        conf.dumper.dbTableColumns(conf.dbmsHandler.getColumns(), CONTENT_TYPE.COLUMNS)
    # 获取数据库中有多少表or表中有多少条记录
    if conf.getCount:
        conf.dumper.dbTablesCount(conf.dbmsHandler.getCount())

    if conf.commonColumns:
        conf.dumper.dbTableColumns(columnExists(paths.COMMON_COLUMNS))
    # 获取表的数量有多少条
    if conf.dumpTable:
        conf.dbmsHandler.dumpTable()

    if conf.dumpAll:
        conf.dbmsHandler.dumpAll()

    if conf.search:
        conf.dbmsHandler.search()

    if conf.query:
        conf.dumper.query(conf.query, conf.dbmsHandler.sqlQuery(conf.query))

    if conf.sqlShell:
        conf.dbmsHandler.sqlShell()
    # 载入一个sql文件进行查询
    if conf.sqlFile:
        conf.dbmsHandler.sqlFile()

    # 用户定义的功能选项
    if conf.udfInject:
        conf.dbmsHandler.udfInjectCustom()

    # 文件系统选项
    if conf.rFile:
        conf.dumper.rFile(conf.dbmsHandler.readFile(conf.rFile))

    if conf.wFile:
        conf.dbmsHandler.writeFile(conf.wFile, conf.dFile, conf.wFileType)

    # 操作系统选项
    if conf.osCmd:
        conf.dbmsHandler.osCmd()

    if conf.osShell:
        conf.dbmsHandler.osShell()

    if conf.osPwn:
        conf.dbmsHandler.osPwn()

    if conf.osSmb:
        conf.dbmsHandler.osSmb()

    if conf.osBof:
        conf.dbmsHandler.osBof()

    # Windows注册表选项
    if conf.regRead:
        conf.dumper.registerValue(conf.dbmsHandler.regRead())

    if conf.regAdd:
        conf.dbmsHandler.regAdd()

    if conf.regDel:
        conf.dbmsHandler.regDel()

    # 杂项
    if conf.cleanup:
        conf.dbmsHandler.cleanup()

    if conf.direct:
        conf.dbmsConnector.close()
