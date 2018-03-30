#!/usr/bin/env python
#coding=utf-8
"""
Copyright (c) 2006-2017 sqlmap developers (http://sqlmap.org/)
See the file 'doc/COPYING' for copying permission
"""

import binascii
import cookielib
import glob
import inspect
import logging
import httplib
import os
import random
import re
import socket
import string
import sys
import tempfile
import threading
import time
import urllib2
import urlparse

import lib.controller.checks
import lib.core.common
import lib.core.threads
import lib.core.convert
import lib.request.connect
import lib.utils.search

from lib.controller.checks import checkConnection
from lib.core.common import Backend
from lib.core.common import boldifyMessage
from lib.core.common import checkFile
from lib.core.common import dataToStdout
from lib.core.common import getPublicTypeMembers
from lib.core.common import getSafeExString
from lib.core.common import extractRegexResult
from lib.core.common import filterStringValue
from lib.core.common import findLocalPort
from lib.core.common import findPageForms
from lib.core.common import getConsoleWidth
from lib.core.common import getFileItems
from lib.core.common import getFileType
from lib.core.common import getUnicode
from lib.core.common import normalizePath
from lib.core.common import ntToPosixSlashes
from lib.core.common import openFile
from lib.core.common import parseTargetDirect
from lib.core.common import parseTargetUrl
from lib.core.common import paths
from lib.core.common import randomStr
from lib.core.common import readCachedFileContent
from lib.core.common import readInput
from lib.core.common import resetCookieJar
from lib.core.common import runningAsAdmin
from lib.core.common import safeExpandUser
from lib.core.common import saveConfig
from lib.core.common import setOptimize
from lib.core.common import setPaths
from lib.core.common import singleTimeWarnMessage
from lib.core.common import urldecode
from lib.core.data import conf
from lib.core.data import kb
from lib.core.data import logger
from lib.core.data import mergedOptions
from lib.core.data import queries
from lib.core.datatype import AttribDict
from lib.core.datatype import InjectionDict
from lib.core.defaults import defaults
from lib.core.dicts import DBMS_DICT
from lib.core.dicts import DUMP_REPLACEMENTS
from lib.core.enums import ADJUST_TIME_DELAY
from lib.core.enums import AUTH_TYPE
from lib.core.enums import CUSTOM_LOGGING
from lib.core.enums import DUMP_FORMAT
from lib.core.enums import HTTP_HEADER
from lib.core.enums import HTTPMETHOD
from lib.core.enums import MOBILES
from lib.core.enums import OPTION_TYPE
from lib.core.enums import PAYLOAD
from lib.core.enums import PRIORITY
from lib.core.enums import PROXY_TYPE
from lib.core.enums import REFLECTIVE_COUNTER
from lib.core.enums import WIZARD
from lib.core.exception import SqlmapConnectionException
from lib.core.exception import SqlmapFilePathException
from lib.core.exception import SqlmapGenericException
from lib.core.exception import SqlmapInstallationException
from lib.core.exception import SqlmapMissingDependence
from lib.core.exception import SqlmapMissingMandatoryOptionException
from lib.core.exception import SqlmapMissingPrivileges
from lib.core.exception import SqlmapNoneDataException
from lib.core.exception import SqlmapSilentQuitException
from lib.core.exception import SqlmapSyntaxException
from lib.core.exception import SqlmapSystemException
from lib.core.exception import SqlmapUnsupportedDBMSException
from lib.core.exception import SqlmapUserQuitException
from lib.core.log import FORMATTER
from lib.core.optiondict import optDict
from lib.core.settings import BURP_REQUEST_REGEX
from lib.core.settings import BURP_XML_HISTORY_REGEX
from lib.core.settings import CODECS_LIST_PAGE
from lib.core.settings import CRAWL_EXCLUDE_EXTENSIONS
from lib.core.settings import CUSTOM_INJECTION_MARK_CHAR
from lib.core.settings import DBMS_ALIASES
from lib.core.settings import DEFAULT_PAGE_ENCODING
from lib.core.settings import DEFAULT_TOR_HTTP_PORTS
from lib.core.settings import DEFAULT_TOR_SOCKS_PORTS
from lib.core.settings import DUMMY_URL
from lib.core.settings import INJECT_HERE_REGEX
from lib.core.settings import IS_WIN
from lib.core.settings import KB_CHARS_BOUNDARY_CHAR
from lib.core.settings import KB_CHARS_LOW_FREQUENCY_ALPHABET
from lib.core.settings import LOCALHOST
from lib.core.settings import MAX_CONNECT_RETRIES
from lib.core.settings import MAX_NUMBER_OF_THREADS
from lib.core.settings import NULL
from lib.core.settings import PARAMETER_SPLITTING_REGEX
from lib.core.settings import PRECONNECT_CANDIDATE_TIMEOUT
from lib.core.settings import PROBLEMATIC_CUSTOM_INJECTION_PATTERNS
from lib.core.settings import SITE
from lib.core.settings import SOCKET_PRE_CONNECT_QUEUE_SIZE
from lib.core.settings import SQLMAP_ENVIRONMENT_PREFIX
from lib.core.settings import SUPPORTED_DBMS
from lib.core.settings import SUPPORTED_OS
from lib.core.settings import TIME_DELAY_CANDIDATES
from lib.core.settings import UNICODE_ENCODING
from lib.core.settings import UNION_CHAR_REGEX
from lib.core.settings import UNKNOWN_DBMS_VERSION
from lib.core.settings import URI_INJECTABLE_REGEX
from lib.core.settings import VERSION_STRING
from lib.core.settings import WEBSCARAB_SPLITTER
from lib.core.settings import DEFAULT_SQLMAP_HTTP_USER_AGENT # 修改sqlmap默认的user_agent为iPhone6
from lib.core.threads import getCurrentThreadData
from lib.core.threads import setDaemon
from lib.core.update import update
from lib.parse.configfile import configFileParser
from lib.parse.payloads import loadBoundaries
from lib.parse.payloads import loadPayloads
from lib.parse.sitemap import parseSitemap
from lib.request.basic import checkCharEncoding
from lib.request.connect import Connect as Request
from lib.request.dns import DNSServer
from lib.request.basicauthhandler import SmartHTTPBasicAuthHandler
from lib.request.httpshandler import HTTPSHandler
from lib.request.pkihandler import HTTPSPKIAuthHandler
from lib.request.rangehandler import HTTPRangeHandler
from lib.request.redirecthandler import SmartRedirectHandler
from lib.request.templates import getPageTemplate
from lib.utils.har import HTTPCollectorFactory
from lib.utils.crawler import crawl
from lib.utils.deps import checkDependencies
from lib.utils.search import search
from lib.utils.purge import purge
from thirdparty.keepalive import keepalive
from thirdparty.multipart import multipartpost
from thirdparty.oset.pyoset import oset
from thirdparty.socks import socks
from xml.etree.ElementTree import ElementTree

authHandler = urllib2.BaseHandler()
httpsHandler = HTTPSHandler()
keepAliveHandler = keepalive.HTTPHandler()
proxyHandler = urllib2.ProxyHandler()
redirectHandler = SmartRedirectHandler()
rangeHandler = HTTPRangeHandler()
multipartPostHandler = multipartpost.MultipartPostHandler()

# Reference: https://mail.python.org/pipermail/python-list/2009-November/558615.html
try:
    WindowsError
except NameError:
    WindowsError = None

def _feedTargetsDict(reqFile, addedTargetUrls):
    """
    解析web scarab和burp日志，并将结果添加到目标URL列表中
    """

    def _parseWebScarabLog(content):
        """
        解析web scarab日志（不支持POST方法）
        """

        reqResList = content.split(WEBSCARAB_SPLITTER)

        for request in reqResList:
            url = extractRegexResult(r"URL: (?P<result>.+?)\n", request, re.I)
            method = extractRegexResult(r"METHOD: (?P<result>.+?)\n", request, re.I)
            cookie = extractRegexResult(r"COOKIE: (?P<result>.+?)\n", request, re.I)

            if not method or not url:
                logger.debug(u"不是有效的WebScarab日志数据")
                continue

            if method.upper() == HTTPMETHOD.POST:
                warnMsg = u"不支持来自WebScarab日志的POST请求，因为它们的主体内容存储在单独的文件中。不过您可以使用-r参数单独加载它们。"
                logger.warning(warnMsg)
                continue

            if not(conf.scope and not re.search(conf.scope, url, re.I)):
                if not kb.targets or url not in addedTargetUrls:
                    kb.targets.add((url, method, None, cookie, None))
                    addedTargetUrls.add(url)

    def _parseBurpLog(content):
        """
        解析burp日志
        """

        if not re.search(BURP_REQUEST_REGEX, content, re.I | re.S):
            if re.search(BURP_XML_HISTORY_REGEX, content, re.I | re.S):
                reqResList = []
                for match in re.finditer(BURP_XML_HISTORY_REGEX, content, re.I | re.S):
                    port, request = match.groups()
                    try:
                        request = request.decode("base64")
                    except binascii.Error:
                        continue
                    _ = re.search(r"%s:.+" % re.escape(HTTP_HEADER.HOST), request)
                    if _:
                        host = _.group(0).strip()
                        if not re.search(r":\d+\Z", host):
                            request = request.replace(host, "%s:%d" % (host, int(port)))
                    reqResList.append(request)
            else:
                reqResList = [content]
        else:
            reqResList = re.finditer(BURP_REQUEST_REGEX, content, re.I | re.S)

        for match in reqResList:
            request = match if isinstance(match, basestring) else match.group(0)
            request = re.sub(r"\A[^\w]+", "", request)

            schemePort = re.search(r"(http[\w]*)\:\/\/.*?\:([\d]+).+?={10,}", request, re.I | re.S)

            if schemePort:
                scheme = schemePort.group(1)
                port = schemePort.group(2)
                request = re.sub(r"\n=+\Z", "", request.split(schemePort.group(0))[-1].lstrip())
            else:
                scheme, port = None, None

            if not re.search(r"^[\n]*(%s).*?\sHTTP\/" % "|".join(getPublicTypeMembers(HTTPMETHOD, True)), request, re.I | re.M):
                continue

            if re.search(r"^[\n]*%s.*?\.(%s)\sHTTP\/" % (HTTPMETHOD.GET, "|".join(CRAWL_EXCLUDE_EXTENSIONS)), request, re.I | re.M):
                continue

            getPostReq = False
            url = None
            host = None
            method = None
            data = None
            cookie = None
            params = False
            newline = None
            lines = request.split('\n')
            headers = []

            for index in xrange(len(lines)):
                line = lines[index]

                if not line.strip() and index == len(lines) - 1:
                    break

                newline = "\r\n" if line.endswith('\r') else '\n'
                line = line.strip('\r')
                match = re.search(r"\A(%s) (.+) HTTP/[\d.]+\Z" % "|".join(getPublicTypeMembers(HTTPMETHOD, True)), line) if not method else None

                if len(line.strip()) == 0 and method and method != HTTPMETHOD.GET and data is None:
                    data = ""
                    params = True

                elif match:
                    method = match.group(1)
                    url = match.group(2)

                    if any(_ in line for _ in ('?', '=', kb.customInjectionMark)):
                        params = True

                    getPostReq = True

                # POST parameters
                elif data is not None and params:
                    data += "%s%s" % (line, newline)

                # GET parameters
                elif "?" in line and "=" in line and ": " not in line:
                    params = True

                # Headers
                elif re.search(r"\A\S+:", line):
                    key, value = line.split(":", 1)
                    value = value.strip().replace("\r", "").replace("\n", "")

                    # Cookie and Host headers
                    if key.upper() == HTTP_HEADER.COOKIE.upper():
                        cookie = value
                    elif key.upper() == HTTP_HEADER.HOST.upper():
                        if '://' in value:
                            scheme, value = value.split('://')[:2]
                        splitValue = value.split(":")
                        host = splitValue[0]

                        if len(splitValue) > 1:
                            port = filterStringValue(splitValue[1], "[0-9]")

                    # 避免向header添加静态内容长度header，并将以下行作为POSTed数据
                    if key.upper() == HTTP_HEADER.CONTENT_LENGTH.upper():
                        params = True

                    # 避免代理和连接类型相关的headers
                    elif key not in (HTTP_HEADER.PROXY_CONNECTION, HTTP_HEADER.CONNECTION):
                        headers.append((getUnicode(key), getUnicode(value)))

                    if kb.customInjectionMark in re.sub(PROBLEMATIC_CUSTOM_INJECTION_PATTERNS, "", value or ""):
                        params = True

            data = data.rstrip("\r\n") if data else data

            if getPostReq and (params or cookie):
                if not port and isinstance(scheme, basestring) and scheme.lower() == "https":
                    port = "443"
                elif not scheme and port == "443":
                    scheme = "https"

                if conf.forceSSL:
                    scheme = "https"
                    port = port or "443"

                if not host:
                    errMsg = u"请求文件格式无效"
                    raise SqlmapSyntaxException, errMsg

                if not url.startswith("http"):
                    url = "%s://%s:%s%s" % (scheme or "http", host, port or "80", url)
                    scheme = None
                    port = None

                if not(conf.scope and not re.search(conf.scope, url, re.I)):
                    if not kb.targets or url not in addedTargetUrls:
                        kb.targets.add((url, conf.method or method, data, cookie, tuple(headers)))
                        addedTargetUrls.add(url)

    checkFile(reqFile)
    try:
        with openFile(reqFile, "rb") as f:
            content = f.read()
    except (IOError, OSError, MemoryError), ex:
        errMsg = u"在尝试读取文件'%s'的内容时出现错误('%s')" % (reqFile, getSafeExString(ex))
        raise SqlmapSystemException(errMsg)

    if conf.scope:
        logger.info(u"使用正则表达式'%s'来过滤目标" % conf.scope)

    _parseBurpLog(content)
    _parseWebScarabLog(content)

    if not addedTargetUrls:
        errMsg = u"无法在提供的文件('%s')中找到可用的请求" % reqFile
        raise SqlmapGenericException(errMsg)

def _loadQueries():
    """
    从“xml/queries.xml”文件加载查询.
    """

    def iterate(node, retVal=None):
        class DictObject(object):
            def __init__(self):
                self.__dict__ = {}

            def __contains__(self, name):
                return name in self.__dict__

        if retVal is None:
            retVal = DictObject()

        for child in node.findall("*"):
            instance = DictObject()
            retVal.__dict__[child.tag] = instance
            if child.attrib:
                instance.__dict__.update(child.attrib)
            else:
                iterate(child, instance)

        return retVal

    tree = ElementTree()
    try:
        tree.parse(paths.QUERIES_XML)
    except Exception, ex:
        errMsg = u"文件'%s'('%s')似乎有问题。" % (paths.QUERIES_XML, getSafeExString(ex))
        errMsg += u"请确保您没有进行任何更改!"
        raise SqlmapInstallationException, errMsg

    for node in tree.findall("*"):
        queries[node.attrib['value']] = iterate(node)

def _setMultipleTargets():
    """
    如果我们以多目标模式运行，则定义一个配置参数.
    """

    initialTargetsCount = len(kb.targets)
    addedTargetUrls = set()

    if not conf.logFile:
        return

    debugMsg = u"从'%s'解析目标列表" % conf.logFile
    logger.debug(debugMsg)

    if not os.path.exists(conf.logFile):
        errMsg = u"指定的目标列表不存在"
        raise SqlmapFilePathException(errMsg)

    if os.path.isfile(conf.logFile):
        _feedTargetsDict(conf.logFile, addedTargetUrls)

    elif os.path.isdir(conf.logFile):
        files = os.listdir(conf.logFile)
        files.sort()

        for reqFile in files:
            if not re.search("([\d]+)\-request", reqFile):
                continue

            _feedTargetsDict(os.path.join(conf.logFile, reqFile), addedTargetUrls)

    else:
        errMsg = u"指定的目标列表不是文件，也不是目录。"
        raise SqlmapFilePathException(errMsg)

    updatedTargetsCount = len(kb.targets)

    if updatedTargetsCount > initialTargetsCount:
        infoMsg = u"sqlmap从准备好的目标列表中分析了%d个请求, 进行测试 " % (updatedTargetsCount - initialTargetsCount)
        logger.info(infoMsg)

def _adjustLoggingFormatter():
    """
    解决由重复记录消息引起的行删除问题，并在推理模式下检索数据信息
    """

    if hasattr(FORMATTER, '_format'):
        return

    def format(record):
        message = FORMATTER._format(record)
        message = boldifyMessage(message)
        if kb.get("prependFlag"):
            message = "\n%s" % message
            kb.prependFlag = False
        return message

    FORMATTER._format = FORMATTER.format
    FORMATTER.format = format

def _setRequestFromFile():
    """
    此功能检查是否通过提供的文本文件进行HTTP请求的方式，解析并将信息保存到知识库中.
    """

    if not conf.requestFile:
        return

    addedTargetUrls = set()

    conf.requestFile = safeExpandUser(conf.requestFile)

    if not os.path.isfile(conf.requestFile):
        errMsg = u"指定的HTTP请求文件'%s'不存在" % conf.requestFile
        raise SqlmapFilePathException(errMsg)

    infoMsg = u"从'%s'解析HTTP请求" % conf.requestFile
    logger.info(infoMsg)

    _feedTargetsDict(conf.requestFile, addedTargetUrls)

def _setCrawler():
    if not conf.crawlDepth:
        return

    if not any((conf.bulkFile, conf.sitemapUrl)):
        crawl(conf.url)
    else:
        if conf.bulkFile:
            targets = getFileItems(conf.bulkFile)
        else:
            targets = parseSitemap(conf.sitemapUrl)
        for i in xrange(len(targets)):
            try:
                target = targets[i]
                crawl(target)

                if conf.verbose in (1, 2):
                    status = u"%d/%d链接访问(%d%%)" % (i + 1, len(targets), round(100.0 * (i + 1) / len(targets)))
                    dataToStdout(u"\r[%s] [信息] %s" % (time.strftime("%X"), status), True)
            except Exception, ex:
                errMsg = u"在'%s'('%s')抓取时发生问题" % (target, getSafeExString(ex))
                logger.error(errMsg)

def _doSearch():
    """
    此功能执行搜索结果，解析结果并将可测试主机保存到知识库中.
    """

    if not conf.googleDork:
        return

    kb.data.onlyGETs = None

    def retrieve():
        links = search(conf.googleDork)

        if not links:
            errMsg = u"在GoogleDork搜索结果中没有找到与之匹配的网页"
            raise SqlmapGenericException(errMsg)

        for link in links:
            link = urldecode(link)
            if re.search(r"(.*?)\?(.+)", link):
                kb.targets.add((link, conf.method, conf.data, conf.cookie, None))
            elif re.search(URI_INJECTABLE_REGEX, link, re.I):
                if kb.data.onlyGETs is None and conf.data is None and not conf.googleDork:
                    message = u"您只想扫描包含GET参数的结果? [Y/n] "
                    kb.data.onlyGETs = readInput(message, default='Y', boolean=True)
                if not kb.data.onlyGETs or conf.googleDork:
                    kb.targets.add((link, conf.method, conf.data, conf.cookie, None))

        return links

    while True:
        links = retrieve()

        if kb.targets:
            infoMsg = u"sqlmap获得%d个Google dork表达式的结果," % len(links)

            if len(links) == len(kb.targets):
                infoMsg += "所有这些都是可测试的目标"
            else:
                infoMsg += "其中%d个是可测试的目标" % len(kb.targets)

            logger.info(infoMsg)
            break

        else:
            message = "sqlmap获取了用于搜索dork表达式的%d个结果，但没有一个具有GET参数来测试SQL注入，你想跳到下一个结果页面吗? [Y/n]" % len(links)

            if not readInput(message, default='Y', boolean=True):
                raise SqlmapSilentQuitException #raise显式地引发异常，后面的语句将不再执行。
            else:
                conf.googlePage += 1

def _setBulkMultipleTargets():
    if not conf.bulkFile:
        return

    conf.bulkFile = safeExpandUser(conf.bulkFile)

    infoMsg = u"从'%s'解析多个目标列表" % conf.bulkFile
    logger.info(infoMsg)

    if not os.path.isfile(conf.bulkFile):
        errMsg = u"指定的批量文件不存在"
        raise SqlmapFilePathException(errMsg)

    found = False
    for line in getFileItems(conf.bulkFile):
        if re.match(r"[^ ]+\?(.+)", line, re.I) or kb.customInjectionMark in line:
            found = True
            kb.targets.add((line.strip(), conf.method, conf.data, conf.cookie, None))

    if not found and not conf.forms and not conf.crawlDepth:
        warnMsg = u"找不到可用的链接（使用GET参数）"
        logger.warn(warnMsg)

def _setSitemapTargets():
    if not conf.sitemapUrl:
        return

    infoMsg = u"解析sitemap '%s'" % conf.sitemapUrl
    logger.info(infoMsg)

    found = False
    for item in parseSitemap(conf.sitemapUrl):
        if re.match(r"[^ ]+\?(.+)", item, re.I):
            found = True
            kb.targets.add((item.strip(), None, None, None, None))

    if not found and not conf.forms and not conf.crawlDepth:
        warnMsg = u"找不到可用的链接(使用GET参数)"
        logger.warn(warnMsg)

def _findPageForms():
    if not conf.forms or conf.crawlDepth:
        return

    if conf.url and not checkConnection():
        return

    infoMsg = u"搜索表单"
    logger.info(infoMsg)

    if not any((conf.bulkFile, conf.googleDork, conf.sitemapUrl)):
        page, _, _ = Request.queryPage(content=True)
        findPageForms(page, conf.url, True, True)
    else:
        if conf.bulkFile:
            targets = getFileItems(conf.bulkFile)
        elif conf.sitemapUrl:
            targets = parseSitemap(conf.sitemapUrl)
        elif conf.googleDork:
            targets = [_[0] for _ in kb.targets]
            kb.targets.clear()
        for i in xrange(len(targets)):
            try:
                target = targets[i]
                page, _, _ = Request.getPage(url=target.strip(), crawling=True, raise404=False)
                findPageForms(page, target, False, True)

                if conf.verbose in (1, 2):
                    status = u'%d/%d访问过的链接 (%d%%)' % (i + 1, len(targets), round(100.0 * (i + 1) / len(targets)))
                    dataToStdout("\r[%s] [INFO] %s" % (time.strftime("%X"), status), True)
            except KeyboardInterrupt:
                break
            except Exception, ex:
                errMsg = u"在'%s'('%s')搜索表单时出现问题" % (target, getSafeExString(ex))
                logger.error(errMsg)

def _setDBMSAuthentication():
    """
    检查并设置DBMS身份验证凭据作为其他用户而不是会话用户运行语句
    """

    if not conf.dbmsCred:
        return

    debugMsg = u"设置DBMS身份验证凭据"
    logger.debug(debugMsg)

    match = re.search("^(.+?):(.*?)$", conf.dbmsCred)

    if not match:
        errMsg = u"DBMS认证凭据值必须格式为username：password"
        raise SqlmapSyntaxException(errMsg)

    conf.dbmsUsername = match.group(1)
    conf.dbmsPassword = match.group(2)

def _setMetasploit():
    if not conf.osPwn and not conf.osSmb and not conf.osBof:
        return

    debugMsg = "setting the takeover out-of-band functionality"
    logger.debug(debugMsg)

    msfEnvPathExists = False

    if IS_WIN:
        try:
            import win32file
        except ImportError:
            errMsg = u"sqlmap需要第三方模块“pywin32”才能在Windows上使用Metasploit功能,"
            errMsg += u"您可以从“http://sourceforge.net/projects/pywin32/files/pywin32/”下载。"
            raise SqlmapMissingDependence(errMsg)

        if not conf.msfPath:
            def _(key, value):
                retVal = None

                try:
                    from  _winreg import ConnectRegistry, OpenKey, QueryValueEx, HKEY_LOCAL_MACHINE
                    _ = ConnectRegistry(None, HKEY_LOCAL_MACHINE)
                    _ = OpenKey(_, key)
                    retVal = QueryValueEx(_, value)[0]
                except:
                    logger.debug(u"无法通过注册表项识别Metasploit安装路径")

                return retVal

            conf.msfPath = _(r"SOFTWARE\Rapid7\Metasploit", "Location")
            if conf.msfPath:
                conf.msfPath = os.path.join(conf.msfPath, "msf3")

    if conf.osSmb:
        isAdmin = runningAsAdmin()

        if not isAdmin:
            errMsg = u"如果要执行SMB中继攻击，则需要以管理员身份运行sqlmap，因为它需要在用户指定的SMB TCP端口上尝试监听传入的连接"
            raise SqlmapMissingPrivileges(errMsg)

    if conf.msfPath:
        for path in (conf.msfPath, os.path.join(conf.msfPath, "bin")):
            if any(os.path.exists(normalizePath(os.path.join(path, _))) for _ in ("msfcli", "msfconsole")):
                msfEnvPathExists = True
                if all(os.path.exists(normalizePath(os.path.join(path, _))) for _ in ("msfvenom",)):
                    kb.oldMsf = False
                elif all(os.path.exists(normalizePath(os.path.join(path, _))) for _ in ("msfencode", "msfpayload")):
                    kb.oldMsf = True
                else:
                    msfEnvPathExists = False

                conf.msfPath = path
                break

        if msfEnvPathExists:
            debugMsg = "提供的Metasploit框架路径 '%s' 是有效的" % conf.msfPath
            logger.debug(debugMsg)
        else:
            warnMsg = "提供的Metasploit Framework路径 '%s' 无效的，" % conf.msfPath
            warnMsg += " 原因可能是路径不存在，"
            warnMsg += "或者msfcli，msfconsole，msfencode和msfpayload中的一个或多个所需的Metasploit可执行文件不存在"
            logger.warn(warnMsg)
    else:
        warnMsg = "您没有提供安装Metasploit Framework的本地路径"
        logger.warn(warnMsg)

    if not msfEnvPathExists:
        warnMsg = "sqlmap将在环境中查找Metasploit Framework安装路径"
        logger.warn(warnMsg)

        envPaths = os.environ.get("PATH", "").split(";" if IS_WIN else ":")

        for envPath in envPaths:
            envPath = envPath.replace(";", "")

            if any(os.path.exists(normalizePath(os.path.join(envPath, _))) for _ in ("msfcli", "msfconsole")):
                msfEnvPathExists = True
                if all(os.path.exists(normalizePath(os.path.join(envPath, _))) for _ in ("msfvenom",)):
                    kb.oldMsf = False
                elif all(os.path.exists(normalizePath(os.path.join(envPath, _))) for _ in ("msfencode", "msfpayload")):
                    kb.oldMsf = True
                else:
                    msfEnvPathExists = False

                if msfEnvPathExists:
                    infoMsg = "Metasploit Framework已经安装在 '%s' 路径中" % envPath
                    logger.info(infoMsg)

                    conf.msfPath = envPath

                    break

    if not msfEnvPathExists:
        errMsg = "无法找到Metasploit Framework，你可能没有安装. "
        errMsg += "你可以在“http://www.metasploit.com/download/”上找到它"
        raise SqlmapFilePathException(errMsg)

def _setWriteFile():
    if not conf.wFile:
        return

    debugMsg = "设置写入文件功能"
    logger.debug(debugMsg)

    if not os.path.exists(conf.wFile):
        errMsg = "所提供的本地文件 '%s' 不存在" % conf.wFile
        raise SqlmapFilePathException(errMsg)

    if not conf.dFile:
        errMsg = "您没有提供后端DBMS绝对路径，您要写入本地文件 '%s'" % conf.wFile
        raise SqlmapMissingMandatoryOptionException(errMsg)

    conf.wFileType = getFileType(conf.wFile)

def _setOS():
    """
    强制后端DBMS操作系统选项
    """

    if not conf.os:
        return

    if conf.os.lower() not in SUPPORTED_OS:
        errMsg = "您提供了不支持的后端DBMS操作系统，"
        errMsg += "用于操作系统和文件系统访问的支持的DBMS操作系统是 %s. " % ', '.join([o.capitalize() for o in SUPPORTED_OS])
        errMsg += "如果您不知道后端DBMS底层操作系统，请不要提供它，sqlmap会自动识别系统指纹。"
        raise SqlmapUnsupportedDBMSException(errMsg)

    debugMsg = "将后端DBMS操作系统强制为用户提供的参数值 '%s'" % conf.os
    logger.debug(debugMsg)

    Backend.setOs(conf.os)

def _setTechnique():
    validTechniques = sorted(getPublicTypeMembers(PAYLOAD.TECHNIQUE), key=lambda x: x[1])
    validLetters = [_[0][0].upper() for _ in validTechniques]

    if conf.tech and isinstance(conf.tech, basestring):
        _ = []

        for letter in conf.tech.upper():
            if letter not in validLetters:
                errMsg = "--technique的值必须是由字母%s组成的字符串，有关详细信息，请参阅 " % "用户手册。".join(validLetters)
                raise SqlmapSyntaxException(errMsg)

            for validTech, validInt in validTechniques:
                if letter == validTech[0]:
                    _.append(validInt)
                    break

        conf.tech = _

def _setDBMS():
    """
    强制后端DBMS选项.
    """

    if not conf.dbms:
        return

    debugMsg = "将后端DBMS强制为用户定义的值"
    logger.debug(debugMsg)

    conf.dbms = conf.dbms.lower()
    regex = re.search("%s ([\d\.]+)" % ("(%s)" % "|".join([alias for alias in SUPPORTED_DBMS])), conf.dbms, re.I)

    if regex:
        conf.dbms = regex.group(1)
        Backend.setVersion(regex.group(2))

    if conf.dbms not in SUPPORTED_DBMS:
        errMsg = "您提供了不受支持的后端数据库管理系统。 "
        errMsg += "支持的DBMS如下: %s. " % ', '.join(sorted(_ for _ in DBMS_DICT))
        errMsg += "如果您不知道后端DBMS，请不要提供它，sqlmap将自动为您识别DBMS指纹。"
        raise SqlmapUnsupportedDBMSException(errMsg)

    for dbms, aliases in DBMS_ALIASES:
        if conf.dbms in aliases:
            conf.dbms = dbms

            break

def _setTamperingFunctions():
    """
    从给定的脚本加载篡改功能
    """

    if conf.tamper:
        last_priority = PRIORITY.HIGHEST
        check_priority = True
        resolve_priorities = False
        priorities = []

        # 可用于在提供的命令行中分割参数值的字符（例如，在--tamper中）
        # PARAMETER_SPLITTING_REGEX = r"[,|;]"
        for script in re.split(PARAMETER_SPLITTING_REGEX, conf.tamper):
            found = False

            path = paths.SQLMAP_TAMPER_PATH.encode(sys.getfilesystemencoding() or UNICODE_ENCODING)
            script = script.strip().encode(sys.getfilesystemencoding() or UNICODE_ENCODING)

            try:
                if not script:
                    continue

                elif os.path.exists(os.path.join(path, script if script.endswith(".py") else "%s.py" % script)):
                    script = os.path.join(path, script if script.endswith(".py") else "%s.py" % script)

                elif not os.path.exists(script):
                    errMsg = "篡改脚本 '%s' 不存在" % script
                    raise SqlmapFilePathException(errMsg)

                elif not script.endswith(".py"):
                    errMsg = "篡改脚本 '%s' 应该有一个扩展名'.py'" % script
                    raise SqlmapSyntaxException(errMsg)
            except UnicodeDecodeError:
                errMsg = "在--tamper选项中提供的是无效字符"
                raise SqlmapSyntaxException(errMsg)

            dirname, filename = os.path.split(script)
            dirname = os.path.abspath(dirname)

            infoMsg = "加载篡改脚本 '%s'" % filename[:-3]
            logger.info(infoMsg)

            if not os.path.exists(os.path.join(dirname, "__init__.py")):
                errMsg = "确保在篡改脚本目录'%s'内有一个空文件 '__init__.py'" % dirname
                raise SqlmapGenericException(errMsg)

            if dirname not in sys.path:
                sys.path.insert(0, dirname)

            try:
                module = __import__(filename[:-3].encode(sys.getfilesystemencoding() or UNICODE_ENCODING))
            except (ImportError, SyntaxError), ex:
                raise SqlmapSyntaxException("无法导入篡改脚本 '%s' (%s)" % (filename[:-3], getSafeExString(ex)))

            priority = PRIORITY.NORMAL if not hasattr(module, "__priority__") else module.__priority__

            for name, function in inspect.getmembers(module, inspect.isfunction):
                if name == "tamper" and inspect.getargspec(function).args and inspect.getargspec(function).keywords == "kwargs":
                    found = True
                    kb.tamperFunctions.append(function)
                    function.func_name = module.__name__

                    if check_priority and priority > last_priority:
                        message = "看来你可能混合了篡改脚本的顺序. "
                        message += "要自动解决这个问题吗? [Y/n/q] "
                        choice = readInput(message, default='Y').upper()

                        if choice == 'N':
                            resolve_priorities = False
                        elif choice == 'Q':
                            raise SqlmapUserQuitException
                        else:
                            resolve_priorities = True

                        check_priority = False

                    priorities.append((priority, function))
                    last_priority = priority

                    break
                elif name == "dependencies":
                    function()

            if not found:
                errMsg = "missing function 'tamper(payload, **kwargs)' "
                errMsg += "in tamper script '%s'" % script
                raise SqlmapGenericException(errMsg)

        if kb.tamperFunctions and len(kb.tamperFunctions) > 3:
            warnMsg = "使用太多的篡改脚本通常不是一个好主意"
            logger.warning(warnMsg)

        if resolve_priorities and priorities:
            priorities.sort(reverse=True)
            kb.tamperFunctions = []

            for _, function in priorities:
                kb.tamperFunctions.append(function)

def _setWafFunctions():
    """
    从脚本加载WAF/IPS/IDS检测功能
    """

    if conf.identifyWaf:
        for found in glob.glob(os.path.join(paths.SQLMAP_WAF_PATH, "*.py")):
            dirname, filename = os.path.split(found)
            dirname = os.path.abspath(dirname)

            if filename == "__init__.py":
                continue

            debugMsg = "加载WAF脚本 '%s'" % filename[:-3]
            logger.debug(debugMsg)

            if dirname not in sys.path:
                sys.path.insert(0, dirname)

            try:
                if filename[:-3] in sys.modules:
                    del sys.modules[filename[:-3]]
                module = __import__(filename[:-3].encode(sys.getfilesystemencoding() or UNICODE_ENCODING))
            except ImportError, msg:
                raise SqlmapSyntaxException("无法导入WAF脚本'%s'(%s)" % (filename[:-3], msg))

            _ = dict(inspect.getmembers(module))
            if "detect" not in _:
                errMsg = "WAF脚本 '%s'中缺少函数'detect(get_page)'" % found
                raise SqlmapGenericException(errMsg)
            else:
                kb.wafFunctions.append((_["detect"], _.get("__product__", filename[:-3])))

        kb.wafFunctions = sorted(kb.wafFunctions, key=lambda _: "generic" in _[1].lower())

def _setThreads():
    if not isinstance(conf.threads, int) or conf.threads <= 0:
        conf.threads = 1

def _setDNSCache():
    """
    创建一个缓存版本的socket._getaddrinfo以避免后续的DNS请求.
    """

    def _getaddrinfo(*args, **kwargs):
        if args in kb.cache.addrinfo:
            return kb.cache.addrinfo[args]

        else:
            kb.cache.addrinfo[args] = socket._getaddrinfo(*args, **kwargs)
            return kb.cache.addrinfo[args]

    if not hasattr(socket, "_getaddrinfo"):
        socket._getaddrinfo = socket.getaddrinfo
        socket.getaddrinfo = _getaddrinfo

def _setSocketPreConnect():
    """
    做一个预连接版本的socket.connect
    """

    if conf.disablePrecon:
        return

    def _():
        while kb.get("threadContinue") and not conf.get("disablePrecon"):
            try:
                for key in socket._ready:
                    # socket预连接的最大数量
                    # SOCKET_PRE_CONNECT_QUEUE_SIZE = 3
                    if len(socket._ready[key]) < SOCKET_PRE_CONNECT_QUEUE_SIZE:
                        family, type, proto, address = key
                        s = socket.socket(family, type, proto)
                        s._connect(address)
                        with kb.locks.socket:
                            socket._ready[key].append((s._sock, time.time()))
            except KeyboardInterrupt:
                break
            except:
                pass
            finally:
                time.sleep(0.01)

    def connect(self, address):
        found = False

        key = (self.family, self.type, self.proto, address)
        with kb.locks.socket:
            if key not in socket._ready:
                socket._ready[key] = []
            while len(socket._ready[key]) > 0:
                candidate, created = socket._ready[key].pop(0)
                if (time.time() - created) < PRECONNECT_CANDIDATE_TIMEOUT:
                    self._sock = candidate
                    found = True
                    break
                else:
                    try:
                        candidate.close()
                    except socket.error:
                        pass

        if not found:
            self._connect(address)

    if not hasattr(socket.socket, "_connect"):
        socket._ready = {}
        socket.socket._connect = socket.socket.connect
        socket.socket.connect = connect

        thread = threading.Thread(target=_)
        setDaemon(thread)
        thread.start()

def _setHTTPHandlers():
    """
    检查并设置所有HTTP请求的HTTP/SOCKS代理.
    """
    global proxyHandler

    for _ in ("http", "https"):
        if hasattr(proxyHandler, "%s_open" % _):
            delattr(proxyHandler, "%s_open" % _)

    if conf.proxyList is not None:
        if not conf.proxyList:
            errMsg = "可用的代理服务器的列表已用尽"
            raise SqlmapNoneDataException(errMsg)

        conf.proxy = conf.proxyList[0]
        conf.proxyList = conf.proxyList[1:]

        infoMsg = "从提供的代理列表文件中加载代理 '%s'" % conf.proxy
        logger.info(infoMsg)

    elif not conf.proxy:
        if conf.hostname in ("localhost", "127.0.0.1") or conf.ignoreProxy:
            proxyHandler.proxies = {}

    if conf.proxy:
        debugMsg = "为所有HTTP请求设置HTTP/SOCKS代理"
        logger.debug(debugMsg)

        try:
            _ = urlparse.urlsplit(conf.proxy)
        except Exception, ex:
            errMsg = "无效的代理地址 '%s' ('%s')" % (conf.proxy, getSafeExString(ex))
            raise SqlmapSyntaxException, errMsg

        hostnamePort = _.netloc.split(":")

        scheme = _.scheme.upper()
        hostname = hostnamePort[0]
        port = None
        username = None
        password = None

        if len(hostnamePort) == 2:
            try:
                port = int(hostnamePort[1])
            except:
                pass  # drops into the next check block

        if not all((scheme, hasattr(PROXY_TYPE, scheme), hostname, port)):
            errMsg = u"代理地址格式必须为：%s://address:port" % "|".join(_[0].lower() for _ in getPublicTypeMembers(PROXY_TYPE))
            raise SqlmapSyntaxException(errMsg)

        if conf.proxyCred:
            _ = re.search("^(.*?):(.*?)$", conf.proxyCred)
            if not _:
                errMsg = u"代理身份验证凭据值必须格式为username：password"
                raise SqlmapSyntaxException(errMsg)
            else:
                username = _.group(1)
                password = _.group(2)

        if scheme in (PROXY_TYPE.SOCKS4, PROXY_TYPE.SOCKS5):
            proxyHandler.proxies = {}

            socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5 if scheme == PROXY_TYPE.SOCKS5 else socks.PROXY_TYPE_SOCKS4, hostname, port, username=username, password=password)
            socks.wrapmodule(urllib2)
        else:
            socks.unwrapmodule(urllib2)

            if conf.proxyCred:
                # Reference: http://stackoverflow.com/questions/34079/how-to-specify-an-authenticated-proxy-for-a-python-http-connection
                proxyString = "%s@" % conf.proxyCred
            else:
                proxyString = ""

            proxyString += "%s:%d" % (hostname, port)
            proxyHandler.proxies = {"http": proxyString, "https": proxyString}

        proxyHandler.__init__(proxyHandler.proxies)

    debugMsg = u"创建HTTP请求opener对象"
    logger.debug(debugMsg)

    handlers = filter(None, [multipartPostHandler, proxyHandler if proxyHandler.proxies else None, authHandler, redirectHandler, rangeHandler, httpsHandler])

    if not conf.dropSetCookie:
        if not conf.loadCookies:
            conf.cj = cookielib.CookieJar()
        else:
            conf.cj = cookielib.MozillaCookieJar()
            resetCookieJar(conf.cj)

        handlers.append(urllib2.HTTPCookieProcessor(conf.cj))

    # Reference: http://www.w3.org/Protocols/rfc2616/rfc2616-sec8.html
    if conf.keepAlive:
        warnMsg = u"持久的HTTP(s)连接(Keep-Alive)由于不兼容而被禁用 "

        if conf.proxy:
            warnMsg += u"使用HTTP(s)代理"
            logger.warn(warnMsg)
        elif conf.authType:
            warnMsg += u"认证方式"
            logger.warn(warnMsg)
        else:
            handlers.append(keepAliveHandler)

    opener = urllib2.build_opener(*handlers)
    urllib2.install_opener(opener)

def _setSafeVisit():
    """
    检查并设置安全访问选项.
    """
    if not any((conf.safeUrl, conf.safeReqFile)):
        return

    if conf.safeReqFile:
        checkFile(conf.safeReqFile)

        raw = readCachedFileContent(conf.safeReqFile)
        match = re.search(r"\A([A-Z]+) ([^ ]+) HTTP/[0-9.]+\Z", raw[:raw.find('\n')])

        if match:
            kb.safeReq.method = match.group(1)
            kb.safeReq.url = match.group(2)
            kb.safeReq.headers = {}

            for line in raw[raw.find('\n') + 1:].split('\n'):
                line = line.strip()
                if line and ':' in line:
                    key, value = line.split(':', 1)
                    value = value.strip()
                    kb.safeReq.headers[key] = value
                    if key == HTTP_HEADER.HOST:
                        if not value.startswith("http"):
                            scheme = "http"
                            if value.endswith(":443"):
                                scheme = "https"
                            value = "%s://%s" % (scheme, value)
                        kb.safeReq.url = urlparse.urljoin(value, kb.safeReq.url)
                else:
                    break

            post = None

            if '\r\n\r\n' in raw:
                post = raw[raw.find('\r\n\r\n') + 4:]
            elif '\n\n' in raw:
                post = raw[raw.find('\n\n') + 2:]

            if post and post.strip():
                kb.safeReq.post = post
            else:
                kb.safeReq.post = None
        else:
            errMsg = u"无效格式的安全请求文件"
            raise SqlmapSyntaxException, errMsg
    else:
        if not re.search("^http[s]*://", conf.safeUrl):
            if ":443/" in conf.safeUrl:
                conf.safeUrl = "https://" + conf.safeUrl
            else:
                conf.safeUrl = "http://" + conf.safeUrl

    if conf.safeFreq <= 0:
        errMsg = u"请使用安全访问功能，为安全频率（--safe-freq）提供有效值（ > 0）"
        raise SqlmapSyntaxException(errMsg)

def _setPrefixSuffix():
    if conf.prefix is not None and conf.suffix is not None:
        # 为用户提供的前缀和后缀创建自定义边界对象
        boundary = AttribDict()

        boundary.level = 1
        boundary.clause = [0]
        boundary.where = [1, 2, 3]
        boundary.prefix = conf.prefix
        boundary.suffix = conf.suffix

        if " like" in boundary.suffix.lower():
            if "'" in boundary.suffix.lower():
                boundary.ptype = 3
            elif '"' in boundary.suffix.lower():
                boundary.ptype = 5
        elif "'" in boundary.suffix:
            boundary.ptype = 2
        elif '"' in boundary.suffix:
            boundary.ptype = 4
        else:
            boundary.ptype = 1

        # 提供前缀、后缀的用户不希望测试其他边界
        conf.boundaries = [boundary]

def _setAuthCred():
    """
    将当前目标的身份验证凭据（如果有）添加到密码管理器（由连接处理程序使用）
    """

    if kb.passwordMgr and all(_ is not None for _ in (conf.scheme, conf.hostname, conf.port, conf.authUsername, conf.authPassword)):
        kb.passwordMgr.add_password(None, "%s://%s:%d" % (conf.scheme, conf.hostname, conf.port), conf.authUsername, conf.authPassword)

def _setHTTPAuthentication():
    """
    检查并设置HTTP(s)身份验证方法（Basic，Digest，NTLM或PKI）
    前三种方法是用的用户名和密码，PKI认证是用的PEM私钥文件
    """

    global authHandler

    if not conf.authType and not conf.authCred and not conf.authFile:
        return

    if conf.authFile and not conf.authType:
        conf.authType = AUTH_TYPE.PKI

    elif conf.authType and not conf.authCred and not conf.authFile:
        errMsg = u"您指定了HTTP身份验证类型，但没有提供凭据u。"
        raise SqlmapSyntaxException(errMsg)

    elif not conf.authType and conf.authCred:
        errMsg = u"您指定了HTTP身份验证凭据，但没有提供类型。"
        raise SqlmapSyntaxException(errMsg)

    elif (conf.authType or "").lower() not in (AUTH_TYPE.BASIC, AUTH_TYPE.DIGEST, AUTH_TYPE.NTLM, AUTH_TYPE.PKI):
        errMsg = u"HTTP认证类型值必须为Basic，Digest，NTLM或PKI。"
        raise SqlmapSyntaxException(errMsg)

    if not conf.authFile:
        debugMsg = u"设置HTTP验证类型和凭据"
        logger.debug(debugMsg)

        authType = conf.authType.lower()

        if authType in (AUTH_TYPE.BASIC, AUTH_TYPE.DIGEST):
            regExp = "^(.*?):(.*?)$"
            errMsg = u"HTTP %s认证凭据值必须使用格式为“username：password” " % authType
        elif authType == AUTH_TYPE.NTLM:
            regExp = "^(.*\\\\.*):(.*?)$"
            errMsg = "HTTP NTLM身份验证凭据值必须格式为'DOMAIN\username:password'"
        elif authType == AUTH_TYPE.PKI:
            errMsg = u"HTTP PKI认证需要使用选项`--auth-pki`"
            raise SqlmapSyntaxException(errMsg)

        aCredRegExp = re.search(regExp, conf.authCred)

        if not aCredRegExp:
            raise SqlmapSyntaxException(errMsg)

        conf.authUsername = aCredRegExp.group(1)
        conf.authPassword = aCredRegExp.group(2)

        kb.passwordMgr = urllib2.HTTPPasswordMgrWithDefaultRealm()

        _setAuthCred()

        if authType == AUTH_TYPE.BASIC:
            authHandler = SmartHTTPBasicAuthHandler(kb.passwordMgr)

        elif authType == AUTH_TYPE.DIGEST:
            authHandler = urllib2.HTTPDigestAuthHandler(kb.passwordMgr)

        elif authType == AUTH_TYPE.NTLM:
            try:
                from ntlm import HTTPNtlmAuthHandler
            except ImportError:
                errMsg = u"sqlmap需要Python NTLM第三方库才能通过NTLM http://code.google.com/p/python-ntlm/进行身份验证"
                raise SqlmapMissingDependence(errMsg)

            authHandler = HTTPNtlmAuthHandler.HTTPNtlmAuthHandler(kb.passwordMgr)
    else:
        debugMsg = u"设置HTTP(s)认证PEM私钥"
        logger.debug(debugMsg)

        _ = safeExpandUser(conf.authFile)
        checkFile(_)
        authHandler = HTTPSPKIAuthHandler(_)

def _setHTTPExtraHeaders():
    if conf.headers:
        debugMsg = u"设置额外的HTTP标头"
        logger.debug(debugMsg)

        conf.headers = conf.headers.split("\n") if "\n" in conf.headers else conf.headers.split("\\n")

        for headerValue in conf.headers:
            if not headerValue.strip():
                continue

            if headerValue.count(':') >= 1:
                header, value = (_.lstrip() for _ in headerValue.split(":", 1))

                if header and value:
                    conf.httpHeaders.append((header, value))
            else:
                errMsg = u"无效标头值: %s,有效的标题格式是'name:value'" % repr(headerValue).lstrip('u')
                raise SqlmapSyntaxException(errMsg)

    elif not conf.requestFile and len(conf.httpHeaders or []) < 2:
        if conf.charset:
            conf.httpHeaders.append((HTTP_HEADER.ACCEPT_CHARSET, "%s;q=0.7,*;q=0.1" % conf.charset))

        # Invalidating any caching mechanism in between
        # Reference: http://stackoverflow.com/a/1383359
        conf.httpHeaders.append((HTTP_HEADER.CACHE_CONTROL, "no-cache"))

def _defaultHTTPUserAgent():
    """
    @return: 默认的sqlmap HTTP User-Agent头
    @rtype: C{str}
    """

    # return "%s (%s)" % (VERSION_STRING, SITE)
    return "%s" % (DEFAULT_SQLMAP_HTTP_USER_AGENT)

def _setHTTPUserAgent():
    """
    Set the HTTP User-Agent header.
    取决于用户的选项:

        * 默认的sqlmap字符串
        * A default value read as user option
        * A random value read from a list of User-Agent headers from a
          file choosed as user option
    """

    if conf.mobile:
        message = u"sqlmap可以通过变换HTTP User-Agent header伪装成智能手机访问网页\n"
        items = sorted(getPublicTypeMembers(MOBILES, True))

        for count in xrange(len(items)):
            item = items[count]
            message += "[%d] %s%s\n" % (count + 1, item[0], " (default)" if item == MOBILES.IPHONE else "")

        test = readInput(message.rstrip('\n'), default=items.index(MOBILES.IPHONE) + 1)

        try:
            item = items[int(test) - 1]
        except:
            item = MOBILES.IPHONE

        conf.httpHeaders.append((HTTP_HEADER.USER_AGENT, item[1]))

    elif conf.agent:
        debugMsg = u"设置HTTP User-Agent header"
        logger.debug(debugMsg)

        conf.httpHeaders.append((HTTP_HEADER.USER_AGENT, conf.agent))

    elif not conf.randomAgent:
        _ = True

        for header, _ in conf.httpHeaders:
            if header == HTTP_HEADER.USER_AGENT:
                _ = False
                break

        if _:
            conf.httpHeaders.append((HTTP_HEADER.USER_AGENT, _defaultHTTPUserAgent()))

    else:
        if not kb.userAgents:
            debugMsg = u"从'%s'文件加载随机HTTP User-Agent header" % paths.USER_AGENTS
            logger.debug(debugMsg)

            try:
                kb.userAgents = getFileItems(paths.USER_AGENTS)
            except IOError:
                warnMsg = u"无法读取HTTP User-Agent header文件('%s')" % paths.USER_AGENTS
                logger.warn(warnMsg)

                conf.httpHeaders.append((HTTP_HEADER.USER_AGENT, _defaultHTTPUserAgent()))
                return

        userAgent = random.sample(kb.userAgents or [_defaultHTTPUserAgent()], 1)[0]

        infoMsg = u"从'%s'文件中获取随机HTTP User-Agent header: '%s'" % (paths.USER_AGENTS, userAgent)
        logger.info(infoMsg)

        conf.httpHeaders.append((HTTP_HEADER.USER_AGENT, userAgent))

def _setHTTPReferer():
    """
    Set the HTTP Referer
    """

    if conf.referer:
        debugMsg = u"设置HTTP Referer header"
        logger.debug(debugMsg)

        conf.httpHeaders.append((HTTP_HEADER.REFERER, conf.referer))

def _setHTTPHost():
    """
    设置HTTP主机
    """

    if conf.host:
        debugMsg = u"设置HTTP Host header"
        logger.debug(debugMsg)

        conf.httpHeaders.append((HTTP_HEADER.HOST, conf.host))

def _setHTTPCookies():
    """
    设置HTTP Cookie头
    """

    if conf.cookie:
        debugMsg = u"设置HTTP Cookie header"
        logger.debug(debugMsg)

        conf.httpHeaders.append((HTTP_HEADER.COOKIE, conf.cookie))

def _setHTTPTimeout():
    """
    设置HTTP超时
    """

    if conf.timeout:
        debugMsg = u"设置HTTP超时"
        logger.debug(debugMsg)

        conf.timeout = float(conf.timeout)

        if conf.timeout < 3.0:
            warnMsg = u"最短HTTP超时为3秒，sqlmap将重置它"
            logger.warn(warnMsg)

            conf.timeout = 3.0
    else:
        conf.timeout = 30.0

    socket.setdefaulttimeout(conf.timeout)

def _checkDependencies():
    """
    检查缺少的依赖关系.
    """

    if conf.dependencies:
        checkDependencies()

def _createTemporaryDirectory():
    """
    创建此运行的临时目录.
    """

    if conf.tmpDir:
        try:
            if not os.path.isdir(conf.tmpDir):
                os.makedirs(conf.tmpDir)

            _ = os.path.join(conf.tmpDir, randomStr())

            open(_, "w+b").close()
            os.remove(_)

            tempfile.tempdir = conf.tmpDir

            warnMsg = u"使用 '%s' 作为临时目录" % conf.tmpDir
            logger.warn(warnMsg)
        except (OSError, IOError), ex:
            errMsg = u"访问临时目录位置('%s')时出现问题" % getSafeExString(ex)
            raise SqlmapSystemException, errMsg
    else:
        try:
            if not os.path.isdir(tempfile.gettempdir()):
                os.makedirs(tempfile.gettempdir())
        except (OSError, IOError, WindowsError), ex:
            warnMsg = u"访问系统的临时目录位置('%s')时出现问题。" % getSafeExString(ex)
            warnMsg += u"请确保剩下足够的磁盘空间，"
            warnMsg += u"如果问题仍然存在，请尝试将环境变量'TEMP'设置为当前用户可写的位置。"
            logger.warn(warnMsg)

    if "sqlmap" not in (tempfile.tempdir or "") or conf.tmpDir and tempfile.tempdir == conf.tmpDir:
        try:
            tempfile.tempdir = tempfile.mkdtemp(prefix="sqlmap", suffix=str(os.getpid()))
        except (OSError, IOError, WindowsError):
            tempfile.tempdir = os.path.join(paths.SQLMAP_HOME_PATH, "tmp", "sqlmap%s%d" % (randomStr(6), os.getpid()))

    kb.tempDir = tempfile.tempdir

    if not os.path.isdir(tempfile.tempdir):
        try:
            os.makedirs(tempfile.tempdir)
        except (OSError, IOError, WindowsError), ex:
            errMsg = u"在设置临时目录位置('%s')时出现问题" % getSafeExString(ex)
            raise SqlmapSystemException, errMsg

def _cleanupOptions():
    """
    清除配置属性。
    """

    debugMsg = "清除配置参数"
    logger.debug(debugMsg)

    width = getConsoleWidth()

    if conf.eta:
        conf.progressWidth = width - 26
    else:
        conf.progressWidth = width - 46

    # 遍历conf中的参数
    for key, value in conf.items():
        if value and any(key.endswith(_) for _ in ("Path", "File", "Dir")):
            conf[key] = safeExpandUser(value)

    if conf.testParameter:
        conf.testParameter = urldecode(conf.testParameter)
        conf.testParameter = conf.testParameter.replace(" ", "")
        conf.testParameter = re.split(PARAMETER_SPLITTING_REGEX, conf.testParameter)
    else:
        conf.testParameter = []

    if conf.agent:
        conf.agent = re.sub(r"[\r\n]", "", conf.agent)

    if conf.user:
        conf.user = conf.user.replace(" ", "")

    if conf.rParam:
        conf.rParam = conf.rParam.replace(" ", "")
        conf.rParam = re.split(PARAMETER_SPLITTING_REGEX, conf.rParam)
    else:
        conf.rParam = []

    if conf.paramDel and '\\' in conf.paramDel:
        conf.paramDel = conf.paramDel.decode("string_escape")

    if conf.skip:
        conf.skip = conf.skip.replace(" ", "")
        conf.skip = re.split(PARAMETER_SPLITTING_REGEX, conf.skip)
    else:
        conf.skip = []

    if conf.cookie:
        conf.cookie = re.sub(r"[\r\n]", "", conf.cookie)

    if conf.delay:
        conf.delay = float(conf.delay)

    if conf.rFile:
        conf.rFile = ntToPosixSlashes(normalizePath(conf.rFile))

    if conf.wFile:
        conf.wFile = ntToPosixSlashes(normalizePath(conf.wFile))

    if conf.dFile:
        conf.dFile = ntToPosixSlashes(normalizePath(conf.dFile))

    if conf.sitemapUrl and not conf.sitemapUrl.lower().startswith("http"):
        conf.sitemapUrl = "http%s://%s" % ('s' if conf.forceSSL else '', conf.sitemapUrl)

    if conf.msfPath:
        conf.msfPath = ntToPosixSlashes(normalizePath(conf.msfPath))

    if conf.tmpPath:
        conf.tmpPath = ntToPosixSlashes(normalizePath(conf.tmpPath))

    if any((conf.googleDork, conf.logFile, conf.bulkFile, conf.sitemapUrl, conf.forms, conf.crawlDepth)):
        conf.multipleTargets = True

    if conf.optimize:
        setOptimize()

    match = re.search(INJECT_HERE_REGEX, conf.data or "")
    if match:
        kb.customInjectionMark = match.group(0)

    match = re.search(INJECT_HERE_REGEX, conf.url or "")
    if match:
        kb.customInjectionMark = match.group(0)

    if conf.os:
        conf.os = conf.os.capitalize()

    if conf.dbms:
        conf.dbms = conf.dbms.capitalize()

    if conf.testFilter:
        conf.testFilter = conf.testFilter.strip('*+')
        conf.testFilter = re.sub(r"([^.])([*+])", "\g<1>.\g<2>", conf.testFilter)

        try:
            re.compile(conf.testFilter)
        except re.error:
            conf.testFilter = re.escape(conf.testFilter)

    if conf.testSkip:
        conf.testSkip = conf.testSkip.strip('*+')
        conf.testSkip = re.sub(r"([^.])([*+])", "\g<1>.\g<2>", conf.testSkip)

        try:
            re.compile(conf.testSkip)
        except re.error:
            conf.testSkip = re.escape(conf.testSkip)

    if "timeSec" not in kb.explicitSettings:
        if conf.tor:
            conf.timeSec = 2 * conf.timeSec
            kb.adjustTimeDelay = ADJUST_TIME_DELAY.DISABLE

            warnMsg = u"将选项'--time-sec'的默认值增加到 %d ，因为提供了'--tor'" % conf.timeSec
            logger.warn(warnMsg)
    else:
        kb.adjustTimeDelay = ADJUST_TIME_DELAY.DISABLE

    if conf.retries:
        conf.retries = min(conf.retries, MAX_CONNECT_RETRIES)

    if conf.code:
        conf.code = int(conf.code)

    if conf.csvDel:
        conf.csvDel = conf.csvDel.decode("string_escape")  # e.g. '\\t' -> '\t'

    if conf.torPort and isinstance(conf.torPort, basestring) and conf.torPort.isdigit():
        conf.torPort = int(conf.torPort)

    if conf.torType:
        conf.torType = conf.torType.upper()

    if conf.outputDir:
        paths.SQLMAP_OUTPUT_PATH = os.path.realpath(os.path.expanduser(conf.outputDir))
        setPaths(paths.SQLMAP_ROOT_PATH)

    if conf.string:
        try:
            conf.string = conf.string.decode("unicode_escape")
        except:
            charset = string.whitespace.replace(" ", "")
            for _ in charset:
                conf.string = conf.string.replace(_.encode("string_escape"), _)

    if conf.getAll:
        map(lambda x: conf.__setitem__(x, True), WIZARD.ALL)

    if conf.noCast:
        for _ in DUMP_REPLACEMENTS.keys():
            del DUMP_REPLACEMENTS[_]

    if conf.dumpFormat:
        conf.dumpFormat = conf.dumpFormat.upper()

    if conf.torType:
        conf.torType = conf.torType.upper()

    if conf.col:
        conf.col = re.sub(r"\s*,\s*", ',', conf.col)

    if conf.excludeCol:
        conf.excludeCol = re.sub(r"\s*,\s*", ',', conf.excludeCol)

    if conf.binaryFields:
        conf.binaryFields = re.sub(r"\s*,\s*", ',', conf.binaryFields)

    if any((conf.proxy, conf.proxyFile, conf.tor)):
        conf.disablePrecon = True

    threadData = getCurrentThreadData()
    threadData.reset()

def _cleanupEnvironment():
    """
    清理环境（例如，在执行--sqlmap-shell之后的操作记录）。
    """

    if issubclass(urllib2.socket.socket, socks.socksocket):
        socks.unwrapmodule(urllib2)

    if hasattr(socket, "_ready"):
        socket._ready.clear()

def _dirtyPatches():
    """
    Place for "dirty" Python related patches
    """

    httplib._MAXLINE = 1 * 1024 * 1024                          
    # 接受过长的结果行（例如，SQLi导致HTTP标头响应）

    if IS_WIN:
        from thirdparty.wininetpton import win_inet_pton
        # 在Windows操作系统上添加对inet_pton()的支持

def _purgeOutput():
    """
    安全删除（清除）输出目录。
    """

    if conf.purgeOutput:
        purge(paths.SQLMAP_OUTPUT_PATH)

def _setConfAttributes():
    """
    此函数将一些所需属性设置为配置单例.
    """

    debugMsg = "初始化配置"
    logger.debug(debugMsg)

    conf.authUsername = None
    conf.authPassword = None
    conf.boundaries = []
    conf.cj = None
    conf.dbmsConnector = None
    conf.dbmsHandler = None
    conf.dnsServer = None
    conf.dumpPath = None
    conf.hashDB = None
    conf.hashDBFile = None
    conf.httpCollector = None
    conf.httpHeaders = []
    conf.hostname = None
    conf.ipv6 = False
    conf.multipleTargets = False
    conf.outputPath = None
    conf.paramDict = {}
    conf.parameters = {}
    conf.path = None
    conf.port = None
    conf.proxyList = None
    conf.resultsFilename = None
    conf.resultsFP = None
    conf.scheme = None
    conf.tests = []
    conf.trafficFP = None
    conf.HARCollectorFactory = None
    conf.wFileType = None

def _setKnowledgeBaseAttributes(flushAll=True):
    """
    该功能将一些所需属性设置到知识库单例中
    kb = KnowledgeBase知识库
    """

    debugMsg = "初始化知识库"
    logger.debug(debugMsg)

    kb.absFilePaths = set()
    kb.adjustTimeDelay = None
    kb.alerted = False
    kb.alwaysRefresh = None
    kb.arch = None
    kb.authHeader = None
    kb.bannerFp = AttribDict()
    kb.binaryField = False
    kb.browserVerification = None

    kb.brute = AttribDict({"tables": [], "columns": []})
    kb.bruteMode = False

    kb.cache = AttribDict()
    kb.cache.addrinfo = {}
    kb.cache.content = {}
    kb.cache.encoding = {}
    kb.cache.intBoundaries = None
    kb.cache.parsedDbms = {}
    kb.cache.regex = {}
    kb.cache.stdev = {}

    kb.captchaDetected = None

    kb.chars = AttribDict()
    kb.chars.delimiter = randomStr(length=6, lowercase=True)
    kb.chars.start = "%s%s%s" % (KB_CHARS_BOUNDARY_CHAR, randomStr(length=3, alphabet=KB_CHARS_LOW_FREQUENCY_ALPHABET), KB_CHARS_BOUNDARY_CHAR)
    kb.chars.stop = "%s%s%s" % (KB_CHARS_BOUNDARY_CHAR, randomStr(length=3, alphabet=KB_CHARS_LOW_FREQUENCY_ALPHABET), KB_CHARS_BOUNDARY_CHAR)
    kb.chars.at, kb.chars.space, kb.chars.dollar, kb.chars.hash_ = ("%s%s%s" % (KB_CHARS_BOUNDARY_CHAR, _, KB_CHARS_BOUNDARY_CHAR) for _ in randomStr(length=4, lowercase=True))

    kb.columnExistsChoice = None
    kb.commonOutputs = None
    kb.connErrorChoice = None
    kb.connErrorCounter = 0
    kb.cookieEncodeChoice = None
    kb.counters = {}
    kb.customInjectionMark = CUSTOM_INJECTION_MARK_CHAR
    kb.data = AttribDict()
    kb.dataOutputFlag = False

    # Active back-end DBMS fingerprint
    kb.dbms = None
    kb.dbmsVersion = [UNKNOWN_DBMS_VERSION]

    kb.delayCandidates = TIME_DELAY_CANDIDATES * [0]
    kb.dep = None
    kb.dnsMode = False
    kb.dnsTest = None
    kb.docRoot = None
    kb.droppingRequests = False
    kb.dumpColumns = None
    kb.dumpTable = None
    kb.dumpKeyboardInterrupt = False
    kb.dynamicMarkings = []
    kb.dynamicParameter = False
    kb.endDetection = False
    kb.explicitSettings = set()
    kb.extendTests = None
    kb.errorChunkLength = None
    kb.errorIsNone = True
    kb.falsePositives = []
    kb.fileReadMode = False
    kb.followSitemapRecursion = None
    kb.forcedDbms = None
    kb.forcePartialUnion = False
    kb.forceWhere = None
    kb.futileUnion = None
    kb.headersFp = {}
    kb.heuristicDbms = None
    kb.heuristicExtendedDbms = None
    kb.heuristicMode = False
    kb.heuristicPage = False
    kb.heuristicTest = None
    kb.hintValue = None
    kb.htmlFp = []
    kb.httpErrorCodes = {}
    kb.inferenceMode = False
    kb.ignoreCasted = None
    kb.ignoreNotFound = False
    kb.ignoreTimeout = False
    kb.injection = InjectionDict()
    kb.injections = []
    kb.laggingChecked = False
    kb.lastParserStatus = None

    kb.locks = AttribDict()
    for _ in ("cache", "connError", "count", "index", "io", "limit", "log", "socket", "redirect", "request", "value"):
        kb.locks[_] = threading.Lock()

    kb.matchRatio = None
    kb.maxConnectionsFlag = False
    kb.mergeCookies = None
    kb.multiThreadMode = False
    kb.negativeLogic = False
    kb.nullConnection = None # 检测空连接
    kb.oldMsf = None
    kb.orderByColumns = None
    kb.originalCode = None
    kb.originalPage = None
    kb.originalPageTime = None
    kb.originalTimeDelay = None
    kb.originalUrls = dict()

    # 后台DBMS底层操作系统指纹通过banner（-b）解析
    kb.os = None
    kb.osVersion = None
    kb.osSP = None

    kb.pageCompress = True
    kb.pageTemplate = None
    kb.pageTemplates = dict()
    kb.pageEncoding = DEFAULT_PAGE_ENCODING
    kb.pageStable = None
    kb.partRun = None
    kb.permissionFlag = False
    kb.postHint = None
    kb.postSpaceToPlus = False
    kb.postUrlEncode = True
    kb.prependFlag = False
    kb.processResponseCounter = 0
    kb.previousMethod = None
    kb.processUserMarks = None
    kb.proxyAuthHeader = None
    kb.queryCounter = 0
    kb.redirectChoice = None
    kb.reflectiveMechanism = True
    kb.reflectiveCounters = {REFLECTIVE_COUNTER.MISS: 0, REFLECTIVE_COUNTER.HIT: 0}
    kb.requestCounter = 0
    kb.resendPostOnRedirect = None
    kb.resolutionDbms = None
    kb.responseTimes = {}
    kb.responseTimeMode = None
    kb.responseTimePayload = None
    kb.resumeValues = True
    kb.rowXmlMode = False
    kb.safeCharEncode = False
    kb.safeReq = AttribDict()
    kb.singleLogFlags = set()
    kb.skipSeqMatcher = False
    kb.reduceTests = None
    kb.tlsSNI = {}
    kb.stickyDBMS = False
    kb.stickyLevel = None
    kb.storeCrawlingChoice = None
    kb.storeHashesChoice = None
    kb.suppressResumeInfo = False
    kb.tableFrom = None
    kb.technique = None
    kb.tempDir = None
    kb.testMode = False
    kb.testOnlyCustom = False
    kb.testQueryCount = 0
    kb.testType = None
    kb.threadContinue = True
    kb.threadException = False
    kb.tableExistsChoice = None
    kb.uChar = NULL
    kb.unionDuplicates = False
    kb.xpCmdshellAvailable = False

    if flushAll:
        kb.headerPaths = {}
        kb.keywords = set(getFileItems(paths.SQL_KEYWORDS))
        kb.passwordMgr = None
        kb.skipVulnHost = None
        kb.tamperFunctions = []
        kb.targets = oset()
        kb.testedParams = set()
        kb.userAgents = None
        kb.vainRun = True
        kb.vulnHosts = set()
        kb.wafFunctions = []
        kb.wordlists = None

def _useWizardInterface():
    """
    为初学者提供简单的向导界面
    """

    if not conf.wizard:
        return

    logger.info(u"启动向导界面")

    while not conf.url:
        message = u"请输入完整的目标网址（-u）: "
        conf.url = readInput(message, default=None)

    message = "%s data (--data) [Enter for None]: " % ((conf.method if conf.method != HTTPMETHOD.GET else conf.method) or HTTPMETHOD.POST)
    conf.data = readInput(message, default=None)

    if not (filter(lambda _: '=' in unicode(_), (conf.url, conf.data)) or '*' in conf.url):
        warnMsg = u"没有找到用于测试的GET和 %s 参数" % ((conf.method if conf.method != HTTPMETHOD.GET else conf.method) or HTTPMETHOD.POST)
        warnMsg += u"(例如'http://www.site.com/vuln.php?id=1'中的GET参数“id”). "
        if not conf.crawlDepth and not conf.forms:
            warnMsg += u"将搜索表单"
            conf.forms = True
        logger.warn(warnMsg)

    choice = None

    while choice is None or choice not in ("", "1", "2", "3"):
        message = u"注入困难 (--程度/--风险). 请选择:\n"
        message += u"[1] 正常 (默认选项)\n[2] 中等\n[3] 困难"
        choice = readInput(message, default='1')

        if choice == '2':
            conf.risk = 2
            conf.level = 3
        elif choice == '3':
            conf.risk = 3
            conf.level = 5
        else:
            conf.risk = 1
            conf.level = 1

    if not conf.getAll:
        choice = None

        while choice is None or choice not in ("", "1", "2", "3"):
            message = u"枚举 (--banner/--current-user/etc). 请选择:\n"
            message += u"[1] 基本 (默认)\n[2] 中级\n[3] 全部"
            choice = readInput(message, default='1')

            if choice == '2':
                map(lambda x: conf.__setitem__(x, True), WIZARD.INTERMEDIATE)
            elif choice == '3':
                map(lambda x: conf.__setitem__(x, True), WIZARD.ALL)
            else:
                map(lambda x: conf.__setitem__(x, True), WIZARD.BASIC)

    logger.debug("muting sqlmap.. it will do the magic for you")
    conf.verbose = 0

    conf.batch = True
    conf.threads = 4

    dataToStdout(u"\nsqlmap正在运行，请稍候..\n\n")

def _saveConfig():
    """
    将命令行选项保存到sqlmap配置INI文件格式.
    """

    if not conf.saveConfig:
        return

    debugMsg = u"将命令行选项保存到sqlmap配置INI文件"
    logger.debug(debugMsg)

    saveConfig(conf, conf.saveConfig)

    infoMsg = u"保存命令行选项到配置文件'%s'" % conf.saveConfig
    logger.info(infoMsg)

def setVerbosity():
    """
    此函数设置sqlmap输出消息的详细程度.
    """

    if conf.verbose is None:
        conf.verbose = 1

    conf.verbose = int(conf.verbose)

    if conf.verbose == 0:
        logger.setLevel(logging.ERROR)
    elif conf.verbose == 1:
        logger.setLevel(logging.INFO)
    elif conf.verbose > 2 and conf.eta:
        conf.verbose = 2
        logger.setLevel(logging.DEBUG)
    elif conf.verbose == 2:
        logger.setLevel(logging.DEBUG)
    elif conf.verbose == 3:
        logger.setLevel(CUSTOM_LOGGING.PAYLOAD)
    elif conf.verbose == 4:
        logger.setLevel(CUSTOM_LOGGING.TRAFFIC_OUT)
    elif conf.verbose >= 5:
        logger.setLevel(CUSTOM_LOGGING.TRAFFIC_IN)

def _normalizeOptions(inputOptions):
    """
    设置适当的选项类型
    """

    types_ = {}
    for group in optDict.keys():
        types_.update(optDict[group])

    for key in inputOptions:
        if key in types_:
            value = inputOptions[key]
            if value is None:
                continue

            type_ = types_[key]
            if type_ and isinstance(type_, tuple):
                type_ = type_[0]

            if type_ == OPTION_TYPE.BOOLEAN:
                try:
                    value = bool(value)
                except (TypeError, ValueError):
                    value = False
            elif type_ == OPTION_TYPE.INTEGER:
                try:
                    value = int(value)
                except (TypeError, ValueError):
                    value = 0
            elif type_ == OPTION_TYPE.FLOAT:
                try:
                    value = float(value)
                except (TypeError, ValueError):
                    value = 0.0

            inputOptions[key] = value

def _mergeOptions(inputOptions, overrideOptions):
    """
    合并具有配置文件和默认选项的命令行选项。.

    @param inputOptions: 具有命令行选项的optparse对象.
    @type inputOptions: C{instance}
    """

    if inputOptions.configFile:
        configFileParser(inputOptions.configFile)

    if hasattr(inputOptions, "items"):
        inputOptionsItems = inputOptions.items()
    else:
        inputOptionsItems = inputOptions.__dict__.items()

    for key, value in inputOptionsItems:
        if key not in conf or value not in (None, False) or overrideOptions:
            conf[key] = value

    if not conf.api:
        for key, value in conf.items():
            if value is not None:
                kb.explicitSettings.add(key)

    for key, value in defaults.items():
        if hasattr(conf, key) and conf[key] is None:
            conf[key] = value

    lut = {}
    for group in optDict.keys():
        lut.update((_.upper(), _) for _ in optDict[group])

    envOptions = {}
    for key, value in os.environ.items():
        if key.upper().startswith(SQLMAP_ENVIRONMENT_PREFIX):
            _ = key[len(SQLMAP_ENVIRONMENT_PREFIX):].upper()
            if _ in lut:
                envOptions[lut[_]] = value

    if envOptions:
        _normalizeOptions(envOptions)
        for key, value in envOptions.items():
            conf[key] = value

    mergedOptions.update(conf)

def _setTrafficOutputFP():
    if conf.trafficFile:
        infoMsg = "设置用于记录HTTP流量的文件"
        logger.info(infoMsg)

        conf.trafficFP = openFile(conf.trafficFile, "w+")

def _setupHTTPCollector():
    if not conf.harFile:
        return

    conf.httpCollector = HTTPCollectorFactory(conf.harFile).create()

def _setDNSServer():
    if not conf.dnsDomain:
        return

    infoMsg = "设置DNS服务器实例"
    logger.info(infoMsg)

    isAdmin = runningAsAdmin()

    if isAdmin:
        try:
            conf.dnsServer = DNSServer()
            conf.dnsServer.run()
        except socket.error, msg:
            errMsg = "设置DNS服务器实例时出现错误 ('%s')" % msg
            raise SqlmapGenericException(errMsg)
    else:
        errMsg = "如果要执行DNS数据exfiltration攻击， "
        errMsg += "您需要以管理员身份运行sqlmap，"
        errMsg += "因为它需要监听特权UDP端口53才能对传入的地址尝试进行解析"
        raise SqlmapMissingPrivileges(errMsg)

def _setProxyList():
    if not conf.proxyFile:
        return

    conf.proxyList = []
    for match in re.finditer(r"(?i)((http[^:]*|socks[^:]*)://)?([\w\-.]+):(\d+)", readCachedFileContent(conf.proxyFile)):
        _, type_, address, port = match.groups()
        conf.proxyList.append("%s://%s:%s" % (type_ or "http", address, port))

def _setTorProxySettings():
    if not conf.tor:
        return

    if conf.torType == PROXY_TYPE.HTTP:
        _setTorHttpProxySettings()
    else:
        _setTorSocksProxySettings()

def _setTorHttpProxySettings():
    infoMsg = "设置Tor HTTP代理"
    logger.info(infoMsg)

    port = findLocalPort(DEFAULT_TOR_HTTP_PORTS if not conf.torPort else (conf.torPort,))

    if port:
        conf.proxy = "http://%s:%d" % (LOCALHOST, port)
    else:
        errMsg = "不能与Tor HTTP代理建立连接。. "
        errMsg += "请确保您已安装Tor，以便您能够成功地使用“--tor”选项。"

        raise SqlmapConnectionException(errMsg)

    if not conf.checkTor:
        warnMsg = "在访问Tor匿名网络时，"
        warnMsg += "使用选项 '--check-tor' 是因为各种“bundles”的默认设置 "
        warnMsg += "（例如Vidalia）的已知问题"
        logger.warn(warnMsg)

def _setTorSocksProxySettings():
    infoMsg = "设置Tor SOCKS代理设置"
    logger.info(infoMsg)

    port = findLocalPort(DEFAULT_TOR_SOCKS_PORTS if not conf.torPort else (conf.torPort,))

    if not port:
        errMsg = "不能与Tor SOCKS代理建立连接. "
        errMsg += "请确保您已安装Tor服务并进行设置，以便您能够成功地使用“--tor”"

        raise SqlmapConnectionException(errMsg)

    # SOCKS5 to prevent DNS leaks (http://en.wikipedia.org/wiki/Tor_%28anonymity_network%29)
    socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5 if conf.torType == PROXY_TYPE.SOCKS5 else socks.PROXY_TYPE_SOCKS4, LOCALHOST, port)
    socks.wrapmodule(urllib2)

def _checkWebSocket():
    if conf.url and (conf.url.startswith("ws:/") or conf.url.startswith("wss:/")):
        try:
            from websocket import ABNF
        except ImportError:
            errMsg = "sqlmap需要第三方模块“websocket-client”才能使用WebSocket功能"
            raise SqlmapMissingDependence(errMsg)

def _checkTor():
    if not conf.checkTor:
        return

    infoMsg = "检查Tor连接"
    logger.info(infoMsg)

    try:
        page, _, _ = Request.getPage(url="https://check.torproject.org/", raise404=False)
    except SqlmapConnectionException:
        page = None

    if not page or 'Congratulations' not in page:
        errMsg = "看来Tor没有正确设置。 请尝试使用选项 '--tor-type' 和 '--tor-port'"
        raise SqlmapConnectionException(errMsg)
    else:
        infoMsg = "Tor正在被使用"
        logger.info(infoMsg)

def _basicOptionValidation():
    if conf.limitStart is not None and not (isinstance(conf.limitStart, int) and conf.limitStart > 0):
        errMsg = "选项'--start'（limitStart）的值必须是大于零（> 0）的整数值"
        raise SqlmapSyntaxException(errMsg)

    if conf.limitStop is not None and not (isinstance(conf.limitStop, int) and conf.limitStop > 0):
        errMsg = "选项'-stop'（limitStop）的值必须是大于零（> 0）的整数值"
        raise SqlmapSyntaxException(errMsg)

    if conf.level is not None and not (isinstance(conf.level, int) and conf.level >= 1 and conf.level <= 5):
        errMsg = "选项'--level'的值必须是范围[1，5]中的整数值"
        raise SqlmapSyntaxException(errMsg)

    if conf.risk is not None and not (isinstance(conf.risk, int) and conf.risk >= 1 and conf.risk <= 3):
        errMsg = "选项'--risk'的值必须是范围[1，3]中的整数值"
        raise SqlmapSyntaxException(errMsg)

    if isinstance(conf.limitStart, int) and conf.limitStart > 0 and \
       isinstance(conf.limitStop, int) and conf.limitStop < conf.limitStart:
        errMsg = "选项'--start'（limitStart）的值必须小于或等于-stop（limit Stop）选项的值"
        raise SqlmapSyntaxException(errMsg)

    if isinstance(conf.firstChar, int) and conf.firstChar > 0 and \
       isinstance(conf.lastChar, int) and conf.lastChar < conf.firstChar:
        errMsg = "选项“--first”（firstChar）的值必须小于或等于--last（lastChar）选项的值"
        raise SqlmapSyntaxException(errMsg)

    if conf.textOnly and conf.nullConnection:
        errMsg = "选项 '--text-only'与 '--null-connection'不兼容"
        raise SqlmapSyntaxException(errMsg)

    if conf.eta and conf.verbose > defaults.verbose:
        errMsg = "选项 '-eta'与选项'-v'不兼容"
        raise SqlmapSyntaxException(errMsg)

    if conf.direct and conf.url:
        errMsg = "选项 '-d'与选项'-u'（'--url'）不兼容"
        raise SqlmapSyntaxException(errMsg)

    if conf.identifyWaf and conf.skipWaf:
        errMsg = "选项 '--identify-waf'与'--skip-waf'不兼容"
        raise SqlmapSyntaxException(errMsg)

    if conf.titles and conf.nullConnection:
        errMsg = "选项 '--titles' 与 '--null-connection'不兼容"
        raise SqlmapSyntaxException(errMsg)

    if conf.dumpTable and conf.search:
        errMsg = "选项 '--dump' 与 '--search'不兼容"
        raise SqlmapSyntaxException(errMsg)

    if conf.api and not conf.configFile:
        errMsg = "switch '--api' 需要使用选项 '-c'"
        raise SqlmapSyntaxException(errMsg)

    if conf.data and conf.nullConnection:
        errMsg = "选项'--data'与'--null-connection'不兼容"
        raise SqlmapSyntaxException(errMsg)

    if conf.string and conf.nullConnection:
        errMsg = "选项'--string'与“--null-connection”不兼容"
        raise SqlmapSyntaxException(errMsg)

    if conf.notString and conf.nullConnection:
        errMsg = "选项'--not-string'与--null-connection'不兼容"
        raise SqlmapSyntaxException(errMsg)

    if conf.noCast and conf.hexConvert:
        errMsg = "选项 '--no-cast' 与 '--hex'不兼容"
        raise SqlmapSyntaxException(errMsg)

    if conf.dumpAll and conf.search:
        errMsg = "选项 '--dump-all' 与 '--search'不兼容"
        raise SqlmapSyntaxException(errMsg)

    if conf.string and conf.notString:
        errMsg = "选项 '--string' 与 '--not-string'不兼容"
        raise SqlmapSyntaxException(errMsg)

    if conf.regexp and conf.nullConnection:
        errMsg = "选项 '--regexp' 与 '--null-connection'不兼容"
        raise SqlmapSyntaxException(errMsg)

    if conf.regexp:
        try:
            re.compile(conf.regexp)
        except Exception, ex:
            errMsg = u"无效的正则表达式'%s' ('%s')" % (conf.regexp, getSafeExString(ex))
            raise SqlmapSyntaxException(errMsg)

    if conf.crawlExclude:
        try:
            re.compile(conf.crawlExclude)
        except Exception, ex:
            errMsg = u"无效的正则表达式'%s' ('%s')" % (conf.crawlExclude, getSafeExString(ex))
            raise SqlmapSyntaxException(errMsg)

    if conf.dumpTable and conf.dumpAll:
        errMsg = u"选项'--dump'与'--dump-all'不兼容"
        raise SqlmapSyntaxException(errMsg)

    if conf.predictOutput and (conf.threads > 1 or conf.optimize):
        errMsg = u"选项'--predict-output'与选项'--threads'和选项 '-o'不兼容"
        raise SqlmapSyntaxException(errMsg)

    if conf.threads > MAX_NUMBER_OF_THREADS and not conf.get("skipThreadCheck"):
        errMsg = u"最大使用线程数为%d，避免潜在的连接问题" % MAX_NUMBER_OF_THREADS
        raise SqlmapSyntaxException(errMsg)

    if conf.forms and not any((conf.url, conf.googleDork, conf.bulkFile, conf.sitemapUrl)):
        errMsg = u"选项'--forms'请求的语法选项'-u' ('--url'), '-g', '-m' 或者 '-x'"
        raise SqlmapSyntaxException(errMsg)

    if conf.crawlExclude and not conf.crawlDepth:
        errMsg = u"选项'--crawl-exclude'需要使用选项 '--crawl'"
        raise SqlmapSyntaxException(errMsg)

    if conf.safePost and not conf.safeUrl:
        errMsg = u"选项'--safe-post'请求的语法选项'--safe-url'"
        raise SqlmapSyntaxException(errMsg)

    if conf.safeFreq and not any((conf.safeUrl, conf.safeReqFile)):
        errMsg = u"选项'--safe-freq'请求的语法选项'--safe-url' or '--safe-req'"
        raise SqlmapSyntaxException(errMsg)

    if conf.safeReqFile and any((conf.safeUrl, conf.safePost)):
        errMsg = u"选项'--safe-req'与'--safe-url'和选项'--safe-post'不兼容"
        raise SqlmapSyntaxException(errMsg)

    if conf.csrfUrl and not conf.csrfToken:
        errMsg = u"选项'--csrf-url'需要使用选项'--csrf-token'"
        raise SqlmapSyntaxException(errMsg)

    if conf.csrfToken and conf.threads > 1:
        errMsg = u"选项'--csrf-url'与选项'--threads'不兼容"
        raise SqlmapSyntaxException(errMsg)

    if conf.requestFile and conf.url and conf.url != DUMMY_URL:
        errMsg = u"选项'-r'与选项'-u' ('--url')不兼容"
        raise SqlmapSyntaxException(errMsg)

    if conf.direct and conf.proxy:
        errMsg = u"选项'-d'与选项'--proxy'不兼容"
        raise SqlmapSyntaxException(errMsg)

    if conf.direct and conf.tor:
        errMsg = u"选项'-d'与选项'--tor'不兼容"
        raise SqlmapSyntaxException(errMsg)

    if not conf.tech:
        errMsg = u"选项'--technique'不能是空的"
        raise SqlmapSyntaxException(errMsg)

    if conf.tor and conf.ignoreProxy:
        errMsg = u"选项'--tor'与'--ignore-proxy'不兼容"
        raise SqlmapSyntaxException(errMsg)

    if conf.tor and conf.proxy:
        errMsg = u"选项'--tor'与选项'--proxy'不兼容"
        raise SqlmapSyntaxException(errMsg)

    if conf.proxy and conf.proxyFile:
        errMsg = u"选项'--proxy'与选项'--proxy-file'不兼容"
        raise SqlmapSyntaxException(errMsg)

    if conf.checkTor and not any((conf.tor, conf.proxy)):
        errMsg = u"选项'--check-tor'需要使用选项'--tor'(或选项'--proxy'使用Tor的HTTP代理地址)"
        raise SqlmapSyntaxException(errMsg)

    if conf.torPort is not None and not (isinstance(conf.torPort, int) and conf.torPort >= 0 and conf.torPort <= 65535):
        errMsg = u"选项'--tor-port'的值必须在0-65535的范围内"
        raise SqlmapSyntaxException(errMsg)

    if conf.torType not in getPublicTypeMembers(PROXY_TYPE, True):
        errMsg = u"选项'--tor-type'接受以下值之一：%s" % ", ".join(getPublicTypeMembers(PROXY_TYPE, True))
        raise SqlmapSyntaxException(errMsg)

    if conf.dumpFormat not in getPublicTypeMembers(DUMP_FORMAT, True):
        errMsg = u"选项'--dump-format'接受以下值之一: %s" % ", ".join(getPublicTypeMembers(DUMP_FORMAT, True))
        raise SqlmapSyntaxException(errMsg)

    if conf.skip and conf.testParameter:
        errMsg = u"选项'--skip'与'-p'不兼容"
        raise SqlmapSyntaxException(errMsg)

    if conf.mobile and conf.agent:
        errMsg = u"选项'--mobile'与'--user-agent'不兼容"
        raise SqlmapSyntaxException(errMsg)

    if conf.proxy and conf.ignoreProxy:
        errMsg = u"选项'--proxy' 与'--ignore-proxy'不兼容"
        raise SqlmapSyntaxException(errMsg)

    if conf.timeSec < 1:
        errMsg = u"选项'--time-sec'的值必须是正整数"
        raise SqlmapSyntaxException(errMsg)

    # 描述可能的union char值的正则表达式（例如在-union-char中使用）
    # UNION_CHAR_REGEX = r"\A\w+\Z"
    # \Z仅匹配字符串末尾    abc\Z  ---->   abc
    # \A仅匹配字符串开头    \Aabc  ---->   abc
    # \w+ 匹配包括下划线的任何单词字符,等价于'[A-Za-z0-9_]'。(+匹配一次或多次)
    if conf.uChar and not re.match(UNION_CHAR_REGEX, conf.uChar):
        errMsg = u"选项'--union-char'的值必须是字母数字值(例如 1)"
        raise SqlmapSyntaxException(errMsg)

    if isinstance(conf.uCols, basestring):
        if not conf.uCols.isdigit() and ("-" not in conf.uCols or len(conf.uCols.split("-")) != 2):
            errMsg = u"选项“--union-cold”的值必须是连字符(例如 1-10)或整数值(例如 5)的范围"
            raise SqlmapSyntaxException(errMsg)

    if conf.dbmsCred and ':' not in conf.dbmsCred:
        errMsg = u"选项'--dbms-cred'的值格式必须为<username>:<password> (例如 \"root:pass\")"
        raise SqlmapSyntaxException(errMsg)

    if conf.charset:
        _ = checkCharEncoding(conf.charset, False)
        if _ is None:
            errMsg = u"未知字符集'%s'，" % conf.charset
            errMsg += u"请访问'%s'以获取支持的字符集的完整列表 " % CODECS_LIST_PAGE
            raise SqlmapSyntaxException(errMsg)
        else:
            conf.charset = _

    if conf.loadCookies:
        if not os.path.exists(conf.loadCookies):
            errMsg = u"Cookie文件'%s'不存在" % conf.loadCookies
            raise SqlmapFilePathException(errMsg)

def _resolveCrossReferences():
    lib.core.threads.readInput = readInput
    lib.core.common.getPageTemplate = getPageTemplate
    lib.core.convert.singleTimeWarnMessage = singleTimeWarnMessage
    lib.request.connect.setHTTPHandlers = _setHTTPHandlers
    lib.utils.search.setHTTPHandlers = _setHTTPHandlers
    lib.controller.checks.setVerbosity = setVerbosity
    lib.controller.checks.setWafFunctions = _setWafFunctions

def initOptions(inputOptions=AttribDict(), overrideOptions=False):
    _setConfAttributes()
    _setKnowledgeBaseAttributes()
    _mergeOptions(inputOptions, overrideOptions)

def init():
    """
    根据命令行和配置文件选项将属性设置为配置和知识库单个。
    """

    _useWizardInterface()
    setVerbosity()
    _saveConfig()
    _setRequestFromFile()
    _cleanupOptions()
    _cleanupEnvironment()
    _dirtyPatches()
    _purgeOutput()
    _checkDependencies()
    _createTemporaryDirectory()
    _basicOptionValidation()
    _setProxyList()
    _setTorProxySettings()
    _setDNSServer()
    _adjustLoggingFormatter()
    _setMultipleTargets()
    _setTamperingFunctions()
    _setWafFunctions()
    _setTrafficOutputFP()
    _setupHTTPCollector()
    _resolveCrossReferences()
    _checkWebSocket()

    parseTargetUrl()
    parseTargetDirect()

    if any((conf.url, conf.logFile, conf.bulkFile, conf.sitemapUrl, conf.requestFile, conf.googleDork, conf.liveTest)):
        _setHTTPTimeout()
        _setHTTPExtraHeaders()
        _setHTTPCookies()
        _setHTTPReferer()
        _setHTTPHost()
        _setHTTPUserAgent()
        _setHTTPAuthentication()
        _setHTTPHandlers()
        _setDNSCache()
        _setSocketPreConnect()
        _setSafeVisit()
        _doSearch()
        _setBulkMultipleTargets()
        _setSitemapTargets()
        _checkTor()
        _setCrawler()
        _findPageForms()
        _setDBMS()
        _setTechnique()

    _setThreads()
    _setOS()
    _setWriteFile()
    _setMetasploit()
    _setDBMSAuthentication()
    loadBoundaries()
    loadPayloads()
    _setPrefixSuffix()
    update()
    _loadQueries()
