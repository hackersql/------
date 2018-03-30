#!/usr/bin/env python
#coding=utf-8
"""
Copyright (c) 2006-2017 sqlmap developers (http://sqlmap.org/)
See the file 'doc/COPYING' for copying permission
"""

import codecs
import functools
import os
import re
import subprocess
import sys
import tempfile
import time
import urlparse

from lib.core.common import Backend
from lib.core.common import getSafeExString
from lib.core.common import getUnicode
from lib.core.common import hashDBRetrieve
from lib.core.common import intersect
from lib.core.common import isNumPosStrValue
from lib.core.common import normalizeUnicode
from lib.core.common import openFile
from lib.core.common import paramToDict
from lib.core.common import randomStr
from lib.core.common import readInput
from lib.core.common import resetCookieJar
from lib.core.common import urldecode
from lib.core.data import conf
from lib.core.data import kb
from lib.core.data import logger
from lib.core.data import mergedOptions
from lib.core.data import paths
from lib.core.datatype import InjectionDict
from lib.core.dicts import DBMS_DICT
from lib.core.dump import dumper
from lib.core.enums import HASHDB_KEYS
from lib.core.enums import HTTP_HEADER
from lib.core.enums import HTTPMETHOD
from lib.core.enums import MKSTEMP_PREFIX
from lib.core.enums import PLACE
from lib.core.enums import POST_HINT
from lib.core.exception import SqlmapFilePathException
from lib.core.exception import SqlmapGenericException
from lib.core.exception import SqlmapMissingPrivileges
from lib.core.exception import SqlmapSystemException
from lib.core.exception import SqlmapUserQuitException
from lib.core.option import _setDBMS
from lib.core.option import _setKnowledgeBaseAttributes
from lib.core.option import _setAuthCred
from lib.core.settings import ASTERISK_MARKER
from lib.core.settings import CSRF_TOKEN_PARAMETER_INFIXES
from lib.core.settings import DEFAULT_GET_POST_DELIMITER
from lib.core.settings import HOST_ALIASES
from lib.core.settings import ARRAY_LIKE_RECOGNITION_REGEX
from lib.core.settings import JSON_RECOGNITION_REGEX
from lib.core.settings import JSON_LIKE_RECOGNITION_REGEX
from lib.core.settings import MULTIPART_RECOGNITION_REGEX
from lib.core.settings import PROBLEMATIC_CUSTOM_INJECTION_PATTERNS
from lib.core.settings import REFERER_ALIASES
from lib.core.settings import RESTORE_MERGED_OPTIONS
from lib.core.settings import RESULTS_FILE_FORMAT
from lib.core.settings import SUPPORTED_DBMS
from lib.core.settings import UNENCODED_ORIGINAL_VALUE
from lib.core.settings import UNICODE_ENCODING
from lib.core.settings import UNKNOWN_DBMS_VERSION
from lib.core.settings import URI_INJECTABLE_REGEX
from lib.core.settings import USER_AGENT_ALIASES
from lib.core.settings import XML_RECOGNITION_REGEX
from lib.utils.hashdb import HashDB
from thirdparty.odict.odict import OrderedDict

def _setRequestParams():
    """
    执行对参数的检查,其中parameters就是get的参数，conf.data则是post的参数
    """
    # 第一步判断参数中是否存在-d参数，直接连接数据库。
    if conf.direct:
        conf.parameters[None] = "direct connection"
        return

    testableParameters = False # 可测试的参数

    # 执行GET参数检查
    if conf.parameters.get(PLACE.GET):
        parameters = conf.parameters[PLACE.GET]
        paramDict = paramToDict(PLACE.GET, parameters)

        if paramDict:
            conf.paramDict[PLACE.GET] = paramDict
            testableParameters = True

    # 执行POST参数检查
    if conf.method == HTTPMETHOD.POST and conf.data is None:
        logger.warn("检测到POST内容是空的！")
        conf.data = ""

    if conf.data is not None:
        conf.method = HTTPMETHOD.POST if not conf.method or conf.method == HTTPMETHOD.GET else conf.method
        hintNames = []
        #判断是不是存在注入标志位
        #在sqlmap中 * 号是为手动标志的注入位置，这里的CUSTOM_INJECTION_MARK就是星号
        def process(match, repl):
            # 先取出整个字符串
            retVal = match.group(0)
            # 如果没有指定注入参数
            if not (conf.testParameter and match.group("name") not in conf.testParameter):
                retVal = repl
                while True:
                    _ = re.search(r"\\g<([^>]+)>", retVal)
                    if _:
                        retVal = retVal.replace(_.group(0), match.group(int(_.group(1)) if _.group(1).isdigit() else _.group(1)))
                    else:
                        break
                # 如果参数中有注入标记符
                if kb.customInjectionMark in retVal:
                    hintNames.append((retVal.split(kb.customInjectionMark)[0], match.group("name")))
            return retVal

        # 如果data中有注入标记符(这里默认的就是*星号，可以用来指定注入位置)
        if kb.processUserMarks is None and kb.customInjectionMark in conf.data:
            message = "在选项--data中找到自定义注入标记 ('%s') " % kb.customInjectionMark
            message += "你想处理它吗? [Y/n/q] "
            choice = readInput(message, default='Y')

            if choice == 'Q':
                raise SqlmapUserQuitException
            else:
                kb.processUserMarks = choice == 'Y'

                if kb.processUserMarks:
                    kb.testOnlyCustom = True
        #JSON数据处理
        if re.search(JSON_RECOGNITION_REGEX, conf.data):
            message = "在 %s 数据中找到JSON数据. " % conf.method
            message += "你想处理它吗? [Y/n/q] "
            choice = readInput(message, default='Y')

            if choice == 'Q':
                raise SqlmapUserQuitException
            elif choice == 'Y':
                if not (kb.processUserMarks and kb.customInjectionMark in conf.data):
                    conf.data = getattr(conf.data, UNENCODED_ORIGINAL_VALUE, conf.data)
                    conf.data = conf.data.replace(kb.customInjectionMark, ASTERISK_MARKER)
                    conf.data = re.sub(r'("(?P<name>[^"]+)"\s*:\s*"[^"]+)"', functools.partial(process, repl=r'\g<1>%s"' % kb.customInjectionMark), conf.data)
                    conf.data = re.sub(r'("(?P<name>[^"]+)"\s*:\s*)(-?\d[\d\.]*\b)', functools.partial(process, repl=r'\g<0>%s' % kb.customInjectionMark), conf.data)
                    match = re.search(r'(?P<name>[^"]+)"\s*:\s*\[([^\]]+)\]', conf.data)
                    if match and not (conf.testParameter and match.group("name") not in conf.testParameter):
                        _ = match.group(2)
                        _ = re.sub(r'("[^"]+)"', '\g<1>%s"' % kb.customInjectionMark, _)
                        _ = re.sub(r'(\A|,|\s+)(-?\d[\d\.]*\b)', '\g<0>%s' % kb.customInjectionMark, _)
                        conf.data = conf.data.replace(match.group(0), match.group(0).replace(match.group(2), _))

                kb.postHint = POST_HINT.JSON

        elif re.search(JSON_LIKE_RECOGNITION_REGEX, conf.data):
            message = "在 %s 数据中找到类似JSON的数据. " % conf.method
            message += "你想处理它吗? [Y/n/q] "
            choice = readInput(message, default='Y').upper()

            if choice == 'Q':
                raise SqlmapUserQuitException
            elif choice == 'Y':
                if not (kb.processUserMarks and kb.customInjectionMark in conf.data):
                    conf.data = getattr(conf.data, UNENCODED_ORIGINAL_VALUE, conf.data)
                    conf.data = conf.data.replace(kb.customInjectionMark, ASTERISK_MARKER)
                    conf.data = re.sub(r"('(?P<name>[^']+)'\s*:\s*'[^']+)'", functools.partial(process, repl=r"\g<1>%s'" % kb.customInjectionMark), conf.data)
                    conf.data = re.sub(r"('(?P<name>[^']+)'\s*:\s*)(-?\d[\d\.]*\b)", functools.partial(process, repl=r"\g<0>%s" % kb.customInjectionMark), conf.data)

                kb.postHint = POST_HINT.JSON_LIKE

        elif re.search(ARRAY_LIKE_RECOGNITION_REGEX, conf.data):
            message = "在 %s 数据中找到类似数组的数据. " % conf.method
            message += "你想处理它吗? [Y/n/q] "
            choice = readInput(message, default='Y').upper()

            if choice == 'Q':
                raise SqlmapUserQuitException
            elif choice == 'Y':
                if not (kb.processUserMarks and kb.customInjectionMark in conf.data):
                    conf.data = conf.data.replace(kb.customInjectionMark, ASTERISK_MARKER)
                    conf.data = re.sub(r"(=[^%s]+)" % DEFAULT_GET_POST_DELIMITER, r"\g<1>%s" % kb.customInjectionMark, conf.data)

                kb.postHint = POST_HINT.ARRAY_LIKE

        elif re.search(XML_RECOGNITION_REGEX, conf.data):
            message = "在 %s 数据中找到SOAP/XML数据. " % conf.method
            message += "你想处理它吗? [Y/n/q] "
            choice = readInput(message, default='Y').upper()

            if choice == 'Q':
                raise SqlmapUserQuitException
            elif choice == 'Y':
                if not (kb.processUserMarks and kb.customInjectionMark in conf.data):
                    conf.data = getattr(conf.data, UNENCODED_ORIGINAL_VALUE, conf.data)
                    conf.data = conf.data.replace(kb.customInjectionMark, ASTERISK_MARKER)
                    conf.data = re.sub(r"(<(?P<name>[^>]+)( [^<]*)?>)([^<]+)(</\2)", functools.partial(process, repl=r"\g<1>\g<4>%s\g<5>" % kb.customInjectionMark), conf.data)

                kb.postHint = POST_HINT.SOAP if "soap" in conf.data.lower() else POST_HINT.XML

        elif re.search(MULTIPART_RECOGNITION_REGEX, conf.data):
            message = "在 %s 的数据中发现多类数据. " % conf.method
            message += "你想处理它吗? [Y/n/q] "
            choice = readInput(message, default='Y').upper()

            if choice == 'Q':
                raise SqlmapUserQuitException
            elif choice == 'Y':
                if not (kb.processUserMarks and kb.customInjectionMark in conf.data):
                    conf.data = getattr(conf.data, UNENCODED_ORIGINAL_VALUE, conf.data)
                    conf.data = conf.data.replace(kb.customInjectionMark, ASTERISK_MARKER)
                    conf.data = re.sub(r"(?si)((Content-Disposition[^\n]+?name\s*=\s*[\"'](?P<name>[^\n]+?)[\"']).+?)(((\r)?\n)+--)", functools.partial(process, repl=r"\g<1>%s\g<4>" % kb.customInjectionMark), conf.data)

                kb.postHint = POST_HINT.MULTIPART

        if not kb.postHint:
            if kb.customInjectionMark in conf.data:  # later processed
                pass
            else:
                place = PLACE.POST

                conf.parameters[place] = conf.data
                paramDict = paramToDict(place, conf.data)

                if paramDict:
                    conf.paramDict[place] = paramDict
                    testableParameters = True
        else:
            if kb.customInjectionMark not in conf.data:  # in case that no usable parameter values has been found
                conf.parameters[PLACE.POST] = conf.data

    kb.processUserMarks = True if (kb.postHint and kb.customInjectionMark in conf.data) else kb.processUserMarks

    if re.search(URI_INJECTABLE_REGEX, conf.url, re.I) and not any(place in conf.parameters for place in (PLACE.GET, PLACE.POST)) and not kb.postHint and not kb.customInjectionMark in (conf.data or "") and conf.url.startswith("http"):
        warnMsg = "您提供了没有任何GET参数（例如“http://www.site.com/article.php?id=1”）的目标网址，并且不通过选项“--data”提供任何POST参数"
        logger.warn(warnMsg)

        message = "您是否想要在目标网址本身中尝试URI注入? [Y/n/q] "
        choice = readInput(message, default='Y').upper()
        _resumeHashDBValues()
        if choice == 'Q':
            raise SqlmapUserQuitException
        elif choice == 'Y':
            conf.url = "%s%s" % (conf.url, kb.customInjectionMark)
            kb.processUserMarks = True

    for place, value in ((PLACE.URI, conf.url), (PLACE.CUSTOM_POST, conf.data), (PLACE.CUSTOM_HEADER, str(conf.httpHeaders))):
        _ = re.sub(PROBLEMATIC_CUSTOM_INJECTION_PATTERNS, "", value or "") if place == PLACE.CUSTOM_HEADER else value or ""
        if kb.customInjectionMark in _:
            if kb.processUserMarks is None:
                lut = {PLACE.URI: '-u', PLACE.CUSTOM_POST: '--data', PLACE.CUSTOM_HEADER: '--headers/--user-agent/--referer/--cookie'}
                message = "在选项中找到自定义注入标记 ('%s') " % kb.customInjectionMark
                message += "'%s'. 你想处理它吗? [Y/n/q] " % lut[place]
                choice = readInput(message, default='Y').upper()

                if choice == 'Q':
                    raise SqlmapUserQuitException
                else:
                    kb.processUserMarks = choice == 'Y'

                    if kb.processUserMarks:
                        kb.testOnlyCustom = True

                        if "=%s" % kb.customInjectionMark in _:
                            warnMsg = "您似乎提供了空参数值进行测试，请始终只使用有效的参数值，以便sqlmap能够正常运行 "
                            logger.warn(warnMsg)

            if not kb.processUserMarks:
                if place == PLACE.URI:
                    query = urlparse.urlsplit(value).query
                    if query:
                        parameters = conf.parameters[PLACE.GET] = query
                        paramDict = paramToDict(PLACE.GET, parameters)

                        if paramDict:
                            conf.url = conf.url.split('?')[0]
                            conf.paramDict[PLACE.GET] = paramDict
                            testableParameters = True
                elif place == PLACE.CUSTOM_POST:
                    conf.parameters[PLACE.POST] = conf.data
                    paramDict = paramToDict(PLACE.POST, conf.data)

                    if paramDict:
                        conf.paramDict[PLACE.POST] = paramDict
                        testableParameters = True

            else:
                conf.parameters[place] = value
                conf.paramDict[place] = OrderedDict()

                if place == PLACE.CUSTOM_HEADER:
                    for index in xrange(len(conf.httpHeaders)):
                        header, value = conf.httpHeaders[index]
                        if kb.customInjectionMark in re.sub(PROBLEMATIC_CUSTOM_INJECTION_PATTERNS, "", value):
                            parts = value.split(kb.customInjectionMark)
                            for i in xrange(len(parts) - 1):
                                conf.paramDict[place]["%s #%d%s" % (header, i + 1, kb.customInjectionMark)] = "%s,%s" % (header, "".join("%s%s" % (parts[j], kb.customInjectionMark if i == j else "") for j in xrange(len(parts))))
                            conf.httpHeaders[index] = (header, value.replace(kb.customInjectionMark, ""))
                else:
                    parts = value.split(kb.customInjectionMark)

                    for i in xrange(len(parts) - 1):
                        name = None
                        if kb.postHint:
                            for ending, _ in hintNames:
                                if parts[i].endswith(ending):
                                    name = "%s %s" % (kb.postHint, _)
                                    break
                        if name is None:
                            name = "%s#%s%s" % (("%s " % kb.postHint) if kb.postHint else "", i + 1, kb.customInjectionMark)
                        conf.paramDict[place][name] = "".join("%s%s" % (parts[j], kb.customInjectionMark if i == j else "") for j in xrange(len(parts)))

                    if place == PLACE.URI and PLACE.GET in conf.paramDict:
                        del conf.paramDict[PLACE.GET]
                    elif place == PLACE.CUSTOM_POST and PLACE.POST in conf.paramDict:
                        del conf.paramDict[PLACE.POST]

                testableParameters = True

    if kb.processUserMarks:
        for item in ("url", "data", "agent", "referer", "cookie"):
            if conf.get(item):
                conf[item] = conf[item].replace(kb.customInjectionMark, "")

    # 执行Cookie参数检查
    if conf.cookie:
        conf.parameters[PLACE.COOKIE] = conf.cookie
        paramDict = paramToDict(PLACE.COOKIE, conf.cookie)

        if paramDict:
            conf.paramDict[PLACE.COOKIE] = paramDict
            testableParameters = True

    # 对header值执行检查
    if conf.httpHeaders:
        for httpHeader, headerValue in list(conf.httpHeaders):
            # 应该避免url编码的header值
            # Reference: http://stackoverflow.com/questions/5085904/is-ok-to-urlencode-the-value-in-headerlocation-value

            if httpHeader.title() == HTTP_HEADER.USER_AGENT:
                conf.parameters[PLACE.USER_AGENT] = urldecode(headerValue)

                condition = any((not conf.testParameter, intersect(conf.testParameter, USER_AGENT_ALIASES, True)))

                if condition:
                    conf.paramDict[PLACE.USER_AGENT] = {PLACE.USER_AGENT: headerValue}
                    testableParameters = True

            elif httpHeader.title() == HTTP_HEADER.REFERER:
                conf.parameters[PLACE.REFERER] = urldecode(headerValue)

                condition = any((not conf.testParameter, intersect(conf.testParameter, REFERER_ALIASES, True)))

                if condition:
                    conf.paramDict[PLACE.REFERER] = {PLACE.REFERER: headerValue}
                    testableParameters = True

            elif httpHeader.title() == HTTP_HEADER.HOST:
                conf.parameters[PLACE.HOST] = urldecode(headerValue)

                condition = any((not conf.testParameter, intersect(conf.testParameter, HOST_ALIASES, True)))

                if condition:
                    conf.paramDict[PLACE.HOST] = {PLACE.HOST: headerValue}
                    testableParameters = True

            else:
                condition = intersect(conf.testParameter, [httpHeader], True)

                if condition:
                    conf.parameters[PLACE.CUSTOM_HEADER] = str(conf.httpHeaders)
                    conf.paramDict[PLACE.CUSTOM_HEADER] = {httpHeader: "%s,%s%s" % (httpHeader, headerValue, kb.customInjectionMark)}
                    conf.httpHeaders = [(header, value.replace(kb.customInjectionMark, "")) for header, value in conf.httpHeaders]
                    testableParameters = True

    if not conf.parameters:
        errMsg = u"您没有提供任何GET，POST和Cookie参数，也不提供User-Agent，Referer或Host header值 "
        raise SqlmapGenericException(errMsg)

    elif not testableParameters:
        errMsg = u"您提供的所有可测试参数不在给定的请求数据中 "
        raise SqlmapGenericException(errMsg)

    if conf.csrfToken:
        if not any(conf.csrfToken in _ for _ in (conf.paramDict.get(PLACE.GET, {}), conf.paramDict.get(PLACE.POST, {}))) and not re.search(r"\b%s\b" % re.escape(conf.csrfToken), conf.data or "") and not conf.csrfToken in set(_[0].lower() for _ in conf.httpHeaders) and not conf.csrfToken in conf.paramDict.get(PLACE.COOKIE, {}):
            errMsg = u"在GET，POST，Cookie或header值中找到没有找到防范anti-CSRF token参数 '%s' " % conf.csrfToken
            raise SqlmapGenericException(errMsg)
    else:
        for place in (PLACE.GET, PLACE.POST, PLACE.COOKIE):
            for parameter in conf.paramDict.get(place, {}):
                if any(parameter.lower().count(_) for _ in CSRF_TOKEN_PARAMETER_INFIXES):
                    message = u"%s参数'%s'似乎持有 anti-CSRF token，" % (place, parameter)
                    message += u"你想要sqlmap在进一步的请求中自动更新它吗? [y/N] "

                    if readInput(message, default='N', boolean=True):
                        conf.csrfToken = getUnicode(parameter)
                    break

def _setHashDB():
    """
    检查并设置HashDB SQLite文件以进行查询恢复功能。
    """

    if not conf.hashDBFile:
        conf.hashDBFile = conf.sessionFile or os.path.join(conf.outputPath, "session.sqlite")

    if os.path.exists(conf.hashDBFile):
        if conf.flushSession:
            try:
                os.remove(conf.hashDBFile)
                logger.info("刷新会话文件")
            except OSError, msg:
                errMsg = "无法刷新会话文件 (%s)" % msg
                raise SqlmapFilePathException(errMsg)

    conf.hashDB = HashDB(conf.hashDBFile)

def _resumeHashDBValues():
    """
    从HashDB恢复存储的数据值
    """
    #文件绝对路径
    kb.absFilePaths = hashDBRetrieve(HASHDB_KEYS.KB_ABS_FILE_PATHS, True) or kb.absFilePaths
    # 爆破表名
    kb.brute.tables = hashDBRetrieve(HASHDB_KEYS.KB_BRUTE_TABLES, True) or kb.brute.tables
    # 爆破列名
    kb.brute.columns = hashDBRetrieve(HASHDB_KEYS.KB_BRUTE_COLUMNS, True) or kb.brute.columns
    # 访问参数和参数值
    kb.chars = hashDBRetrieve(HASHDB_KEYS.KB_CHARS, True) or kb.chars
    # 测试level
    kb.dynamicMarkings = hashDBRetrieve(HASHDB_KEYS.KB_DYNAMIC_MARKINGS, True) or kb.dynamicMarkings
    # 是否可以执行cmdshell
    kb.xpCmdshellAvailable = hashDBRetrieve(HASHDB_KEYS.KB_XP_CMDSHELL_AVAILABLE) or kb.xpCmdshellAvailable
    # 错误块的长度
    kb.errorChunkLength = hashDBRetrieve(HASHDB_KEYS.KB_ERROR_CHUNK_LENGTH)
    if isNumPosStrValue(kb.errorChunkLength):
        kb.errorChunkLength = int(kb.errorChunkLength)
    else:
        kb.errorChunkLength = None
    # 临时路径
    conf.tmpPath = conf.tmpPath or hashDBRetrieve(HASHDB_KEYS.CONF_TMP_PATH)
    # 注入记录
    for injection in hashDBRetrieve(HASHDB_KEYS.KB_INJECTIONS, True) or []:
        if isinstance(injection, InjectionDict) and injection.place in conf.paramDict and \
            injection.parameter in conf.paramDict[injection.place]:

            if not conf.tech or intersect(conf.tech, injection.data.keys()):
                if intersect(conf.tech, injection.data.keys()):
                    injection.data = dict(_ for _ in injection.data.items() if _[0] in conf.tech)

                if injection not in kb.injections:
                    kb.injections.append(injection)

    _resumeDBMS()
    _resumeOS()

def _resumeDBMS():
    """
    从HashDB恢复存储的DBMS信息
    """

    value = hashDBRetrieve(HASHDB_KEYS.DBMS)

    if not value:
        return

    dbms = value.lower()
    dbmsVersion = [UNKNOWN_DBMS_VERSION]
    _ = "(%s)" % ("|".join([alias for alias in SUPPORTED_DBMS]))
    _ = re.search(r"\A%s (.*)" % _, dbms, re.I)

    if _:
        dbms = _.group(1).lower()
        dbmsVersion = [_.group(2)]

    if conf.dbms:
        check = True
        for aliases, _, _, _ in DBMS_DICT.values():
            if conf.dbms.lower() in aliases and dbms not in aliases:
                check = False
                break

        if not check:
            message = "您提供'%s'作为后端DBMS，" % conf.dbms
            message += "但是从过去扫描目标URL的信息中假定sqlmap后端DBMS是'%s'。" % dbms
            message += "你真的想强制指定后端DBMS值吗? [y/N] "

            if not readInput(message, default='N', boolean=True):
                conf.dbms = None
                Backend.setDbms(dbms)
                Backend.setVersionList(dbmsVersion)
    else:
        infoMsg = "恢复后端 DBMS '%s' " % dbms
        logger.info(infoMsg)

        Backend.setDbms(dbms)
        Backend.setVersionList(dbmsVersion)

def _resumeOS():
    """
    从HashDB恢复存储的操作系统信息
    """

    value = hashDBRetrieve(HASHDB_KEYS.OS)

    if not value:
        return

    os = value

    if os and os != 'None':
        infoMsg = "恢复后端DBMS操作系统 '%s' " % os
        logger.info(infoMsg)

        if conf.os and conf.os.lower() != os.lower():
            message = "you provided '%s' as back-end DBMS operating " % conf.os
            message += "system, but from a past scan information on the "
            message += "target URL sqlmap assumes the back-end DBMS "
            message += "operating system is %s. " % os
            message += "Do you really want to force the back-end DBMS "
            message += "OS value? [y/N] "

            if not readInput(message, default='N', boolean=True):
                conf.os = os
        else:
            conf.os = os

        Backend.setOs(conf.os)

def _setResultsFile():
    """
    创建保存多目标模式输出结果的文件
    """

    if not conf.multipleTargets:
        return

    if not conf.resultsFP:
        conf.resultsFilename = os.path.join(paths.SQLMAP_OUTPUT_PATH, time.strftime(RESULTS_FILE_FORMAT).lower())
        try:
            conf.resultsFP = openFile(conf.resultsFilename, "w+", UNICODE_ENCODING, buffering=0)
        except (OSError, IOError), ex:
            try:
                warnMsg = "无法创建结果文件 '%s' ('%s'). " % (conf.resultsFilename, getUnicode(ex))
                handle, conf.resultsFilename = tempfile.mkstemp(prefix=MKSTEMP_PREFIX.RESULTS, suffix=".csv")
                os.close(handle)
                conf.resultsFP = openFile(conf.resultsFilename, "w+", UNICODE_ENCODING, buffering=0)
                warnMsg += "使用临时文件 '%s' 代替" % conf.resultsFilename
                logger.warn(warnMsg)
            except IOError, _:
                errMsg = "无法写入临时目录 ('%s'). " % _
                errMsg += "请确保您的磁盘未满 "
                errMsg += "且有足够的写入权限 "
                errMsg += "创建临时文件或目录"
                raise SqlmapSystemException(errMsg)

        conf.resultsFP.writelines("Target URL,Place,Parameter,Technique(s),Note(s)%s" % os.linesep)

        logger.info("在多目标模式下使用 '%s' 作为CSV结果文件" % conf.resultsFilename)

def _createFilesDir():
    """
    创建文件目录.
    """

    if not conf.rFile:
        return

    conf.filePath = paths.SQLMAP_FILES_PATH % conf.hostname

    if not os.path.isdir(conf.filePath):
        try:
            os.makedirs(conf.filePath, 0755)
        except OSError, ex:
            tempDir = tempfile.mkdtemp(prefix="sqlmapfiles")
            warnMsg = "无法创建文件目录 "
            warnMsg += "'%s' (%s). " % (conf.filePath, getUnicode(ex))
            warnMsg += "使用临时目录 '%s' 代替" % tempDir
            logger.warn(warnMsg)

            conf.filePath = tempDir

def _createDumpDir():
    """
    创建转储目录.
    """

    if not conf.dumpTable and not conf.dumpAll and not conf.search:
        return

    conf.dumpPath = paths.SQLMAP_DUMP_PATH % conf.hostname

    if not os.path.isdir(conf.dumpPath):
        try:
            os.makedirs(conf.dumpPath, 0755)
        except OSError, ex:
            tempDir = tempfile.mkdtemp(prefix="sqlmapdump")
            warnMsg = "无法创建转储目录 "
            warnMsg += "'%s' (%s). " % (conf.dumpPath, getUnicode(ex))
            warnMsg += "使用临时目录 '%s' 代替" % tempDir
            logger.warn(warnMsg)

            conf.dumpPath = tempDir

def _configureDumper():
    conf.dumper = dumper
    conf.dumper.setOutputFile()

def _createTargetDirs():
    """
    创建输出目录
    """

    try:#如果不存在就创建并赋予755权限
        if not os.path.isdir(paths.SQLMAP_OUTPUT_PATH):
            os.makedirs(paths.SQLMAP_OUTPUT_PATH, 0755)
        # os.path.join拼接路径randomStr创建一个随机的文件名
        _ = os.path.join(paths.SQLMAP_OUTPUT_PATH, randomStr())
        open(_, "w+b").close()
        os.remove(_)

        if conf.outputDir:
            warnMsg = u"使用'%s'作为输出目录" % paths.SQLMAP_OUTPUT_PATH
            logger.warn(warnMsg)
    except (OSError, IOError), ex:
        try:
            tempDir = tempfile.mkdtemp(prefix="sqlmapoutput")
        except Exception, _:
            errMsg = "无法写入临时目录 ('%s'). " % _
            errMsg += "请确保您的磁盘未满 "
            errMsg += "且有足够的写入权限 "
            errMsg += "创建临时文件或目录"
            raise SqlmapSystemException(errMsg)

        warnMsg = "unable to %s output directory " % ("create" if not os.path.isdir(paths.SQLMAP_OUTPUT_PATH) else "write to the")
        warnMsg += "'%s' (%s). " % (paths.SQLMAP_OUTPUT_PATH, getUnicode(ex))
        warnMsg += "使用临时目录 '%s' 代替" % getUnicode(tempDir)
        logger.warn(warnMsg)

        paths.SQLMAP_OUTPUT_PATH = tempDir

    conf.outputPath = os.path.join(getUnicode(paths.SQLMAP_OUTPUT_PATH), normalizeUnicode(getUnicode(conf.hostname)))

    if not os.path.isdir(conf.outputPath):
        try:
            os.makedirs(conf.outputPath, 0755)
        except (OSError, IOError), ex:
            try:
                tempDir = tempfile.mkdtemp(prefix="sqlmapoutput")
            except Exception, _:
                errMsg = "无法写入临时目录 ('%s'). " % _
                errMsg += "请确保您的磁盘未满 "
                errMsg += "且有足够的写入权限 "
                errMsg += "创建临时文件和/或目录"
                raise SqlmapSystemException(errMsg)

            warnMsg = "无法创建输出目录 "
            warnMsg += "'%s' (%s). " % (conf.outputPath, getUnicode(ex))
            warnMsg += "使用临时目录 '%s' 代替" % getUnicode(tempDir)
            logger.warn(warnMsg)

            conf.outputPath = tempDir

    try:#写入基本信息
        #codecs.open(路径/文件名, 打开模式, 编码方式)
        #with 语句，不管在处理文件过程中是否发生异常，都能保证 with 语句执行完毕后关闭已经打开的文件句柄。
        with codecs.open(os.path.join(conf.outputPath, "target.txt"), "w+", UNICODE_ENCODING) as f:
            #write向文件f写入url等信息
            f.write(kb.originalUrls.get(conf.url) or conf.url or conf.hostname)
            f.write(" (%s)" % (HTTPMETHOD.POST if conf.data else HTTPMETHOD.GET))
            f.write("  # %s" % getUnicode(subprocess.list2cmdline(sys.argv), encoding=sys.stdin.encoding))
            if conf.data:
                f.write("\n\n%s" % getUnicode(conf.data))
    except IOError, ex:
        if "denied" in getUnicode(ex):
            errMsg = "你没有足够的权限 "
        else:
            errMsg = "尝试时发生错误 "
        errMsg += "写入输出目录 '%s' (%s)" % (paths.SQLMAP_OUTPUT_PATH, getSafeExString(ex))

        raise SqlmapMissingPrivileges(errMsg)

    _createDumpDir()
    _createFilesDir()
    _configureDumper()

def _restoreMergedOptions():
    """
    还原合并的选项（命令行，配置文件和默认值）
    这可能会在以前的目标测试过程中发生变化。
    """

    for option in RESTORE_MERGED_OPTIONS:
        conf[option] = mergedOptions[option]

def initTargetEnv():
    """
    初始化目标环境.
    """

    if conf.multipleTargets:
        if conf.hashDB:
            conf.hashDB.close()

        if conf.cj:
            resetCookieJar(conf.cj)

        conf.paramDict = {}
        conf.parameters = {}
        conf.hashDBFile = None

        _setKnowledgeBaseAttributes(False)
        _restoreMergedOptions()
        _setDBMS()

    if conf.data:
        class _(unicode):
            pass

        kb.postUrlEncode = True

        for key, value in conf.httpHeaders:
            if key.upper() == HTTP_HEADER.CONTENT_TYPE.upper():
                kb.postUrlEncode = "urlencoded" in value
                break

        if kb.postUrlEncode:
            original = conf.data
            conf.data = _(urldecode(conf.data))
            setattr(conf.data, UNENCODED_ORIGINAL_VALUE, original)
            kb.postSpaceToPlus = '+' in original

def setupTargetEnv():
    _createTargetDirs()
    _setRequestParams()
    _setHashDB()
    _resumeHashDBValues()
    _setResultsFile()
    _setAuthCred()
