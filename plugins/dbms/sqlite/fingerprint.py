#!/usr/bin/env python
#coding=utf-8
"""
Copyright (c) 2006-2017 sqlmap developers (http://sqlmap.org/)
See the file 'doc/COPYING' for copying permission
"""

from lib.core.common import Backend
from lib.core.common import Format
from lib.core.data import conf
from lib.core.data import kb
from lib.core.data import logger
from lib.core.enums import DBMS
from lib.core.session import setDbms
from lib.core.settings import METADB_SUFFIX
from lib.core.settings import SQLITE_ALIASES
from lib.request import inject
from plugins.generic.fingerprint import Fingerprint as GenericFingerprint

class Fingerprint(GenericFingerprint):
    def __init__(self):
        GenericFingerprint.__init__(self, DBMS.SQLITE)

    def getFingerprint(self):
        value = ""
        wsOsFp = Format.getOs("web server", kb.headersFp)

        if wsOsFp:
            value += "%s\n" % wsOsFp

        if kb.data.banner:
            dbmsOsFp = Format.getOs("back-end DBMS", kb.bannerFp)

            if dbmsOsFp:
                value += "%s\n" % dbmsOsFp

        value += u"后端DBMS是:"

        if not conf.extensiveFp:
            value += DBMS.SQLITE
            return value

        actVer = Format.getDbms()
        blank = " " * 15
        value += "active fingerprint: %s" % actVer

        if kb.bannerFp:
            banVer = kb.bannerFp["dbmsVersion"]
            banVer = Format.getDbms([banVer])
            value += "\n%sbanner parsing fingerprint: %s" % (blank, banVer)

        htmlErrorFp = Format.getErrorParsedDBMSes()

        if htmlErrorFp:
            value += "\n%shtml error message fingerprint: %s" % (blank, htmlErrorFp)

        return value

    def checkDbms(self):
        """
        References for fingerprint:

        * http://www.sqlite.org/lang_corefunc.html
        * http://www.sqlite.org/cvstrac/wiki?p=LoadableExtensions
        """

        if not conf.extensiveFp and Backend.isDbmsWithin(SQLITE_ALIASES):
            setDbms(DBMS.SQLITE)

            self.getBanner()

            return True

        infoMsg = u"测试%s" % DBMS.SQLITE
        logger.info(infoMsg)

        result = inject.checkBooleanExpression("LAST_INSERT_ROWID()=LAST_INSERT_ROWID()")

        if result:
            infoMsg = u"确认后端数据库是%s" % DBMS.SQLITE
            logger.info(infoMsg)

            result = inject.checkBooleanExpression("SQLITE_VERSION()=SQLITE_VERSION()")

            if not result:
                warnMsg = u"后端DBMS不是%s" % DBMS.SQLITE
                logger.warn(warnMsg)

                return False
            else:
                infoMsg = u"主动指纹识别为%s" % DBMS.SQLITE
                logger.info(infoMsg)

                result = inject.checkBooleanExpression("RANDOMBLOB(-1)>0")
                version = '3' if result else '2'
                Backend.setVersion(version)

            setDbms(DBMS.SQLITE)

            self.getBanner()

            return True
        else:
            warnMsg = u"后端DBMS不是%s" % DBMS.SQLITE
            logger.warn(warnMsg)

            return False

    def forceDbmsEnum(self):
        conf.db = "%s%s" % (DBMS.SQLITE, METADB_SUFFIX)
