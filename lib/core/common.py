#!/usr/bin/env python
#coding=utf-8
"""
Copyright (c) 2006-2017 sqlmap developers (http://sqlmap.org/)
See the file 'doc/COPYING' for copying permission
"""

import codecs
import contextlib
import cookielib
import copy
import getpass
import hashlib
import httplib
import inspect
import json
import locale
import logging
import ntpath
import os
import posixpath
import random
import re
import socket
import string
import subprocess
import sys
import tempfile
import threading
import time
import urllib
import urllib2
import urlparse
import unicodedata

from ConfigParser import DEFAULTSECT
from ConfigParser import RawConfigParser
from StringIO import StringIO
from difflib import SequenceMatcher
from math import sqrt
from optparse import OptionValueError
from xml.dom import minidom
from xml.sax import parse
from xml.sax import SAXParseException

from extra.beep.beep import beep
from extra.cloak.cloak import decloak
from extra.safe2bin.safe2bin import safecharencode
from lib.core.bigarray import BigArray
from lib.core.data import conf
from lib.core.data import kb
from lib.core.data import logger
from lib.core.data import paths
from lib.core.convert import base64pickle
from lib.core.convert import base64unpickle
from lib.core.convert import hexdecode
from lib.core.convert import htmlunescape
from lib.core.convert import stdoutencode
from lib.core.convert import unicodeencode
from lib.core.convert import utf8encode
from lib.core.decorators import cachedmethod
from lib.core.defaults import defaults
from lib.core.dicts import DBMS_DICT
from lib.core.dicts import DEFAULT_DOC_ROOTS
from lib.core.dicts import DEPRECATED_OPTIONS
from lib.core.dicts import SQL_STATEMENTS
from lib.core.enums import ADJUST_TIME_DELAY
from lib.core.enums import CONTENT_STATUS
from lib.core.enums import CHARSET_TYPE
from lib.core.enums import DBMS
from lib.core.enums import EXPECTED
from lib.core.enums import HEURISTIC_TEST
from lib.core.enums import HTTP_HEADER
from lib.core.enums import HTTPMETHOD
from lib.core.enums import MKSTEMP_PREFIX
from lib.core.enums import OPTION_TYPE
from lib.core.enums import OS
from lib.core.enums import PLACE
from lib.core.enums import PAYLOAD
from lib.core.enums import REFLECTIVE_COUNTER
from lib.core.enums import SORT_ORDER
from lib.core.exception import SqlmapDataException
from lib.core.exception import SqlmapGenericException
from lib.core.exception import SqlmapNoneDataException
from lib.core.exception import SqlmapInstallationException
from lib.core.exception import SqlmapMissingDependence
from lib.core.exception import SqlmapSilentQuitException
from lib.core.exception import SqlmapSyntaxException
from lib.core.exception import SqlmapSystemException
from lib.core.exception import SqlmapUserQuitException
from lib.core.exception import SqlmapValueException
from lib.core.log import LOGGER_HANDLER
from lib.core.optiondict import optDict
from lib.core.settings import BANNER
from lib.core.settings import BOLD_PATTERNS
from lib.core.settings import BOUNDED_INJECTION_MARKER
from lib.core.settings import BRUTE_DOC_ROOT_PREFIXES
from lib.core.settings import BRUTE_DOC_ROOT_SUFFIXES
from lib.core.settings import BRUTE_DOC_ROOT_TARGET_MARK
from lib.core.settings import DBMS_DIRECTORY_DICT
from lib.core.settings import CUSTOM_INJECTION_MARK_CHAR
from lib.core.settings import DEFAULT_COOKIE_DELIMITER
from lib.core.settings import DEFAULT_GET_POST_DELIMITER
from lib.core.settings import DEFAULT_MSSQL_SCHEMA
from lib.core.settings import DUMMY_USER_INJECTION
from lib.core.settings import DYNAMICITY_MARK_LENGTH
from lib.core.settings import ERROR_PARSING_REGEXES
from lib.core.settings import FILE_PATH_REGEXES
from lib.core.settings import FORCE_COOKIE_EXPIRATION_TIME
from lib.core.settings import FORM_SEARCH_REGEX
from lib.core.settings import GENERIC_DOC_ROOT_DIRECTORY_NAMES
from lib.core.settings import GIT_PAGE
from lib.core.settings import GITHUB_REPORT_OAUTH_TOKEN
from lib.core.settings import GOOGLE_ANALYTICS_COOKIE_PREFIX
from lib.core.settings import HASHDB_MILESTONE_VALUE
from lib.core.settings import HOST_ALIASES
from lib.core.settings import IGNORE_SAVE_OPTIONS
from lib.core.settings import INFERENCE_UNKNOWN_CHAR
from lib.core.settings import INVALID_UNICODE_CHAR_FORMAT
from lib.core.settings import IP_ADDRESS_REGEX
from lib.core.settings import ISSUES_PAGE
from lib.core.settings import IS_WIN
from lib.core.settings import LARGE_OUTPUT_THRESHOLD
from lib.core.settings import LOCALHOST
from lib.core.settings import MIN_ENCODED_LEN_CHECK
from lib.core.settings import MIN_TIME_RESPONSES
from lib.core.settings import MIN_VALID_DELAYED_RESPONSE
from lib.core.settings import NETSCAPE_FORMAT_HEADER_COOKIES
from lib.core.settings import NULL
from lib.core.settings import PARAMETER_AMP_MARKER
from lib.core.settings import PARAMETER_SEMICOLON_MARKER
from lib.core.settings import PARTIAL_HEX_VALUE_MARKER
from lib.core.settings import PARTIAL_VALUE_MARKER
from lib.core.settings import PAYLOAD_DELIMITER
from lib.core.settings import PLATFORM
from lib.core.settings import PRINTABLE_CHAR_REGEX
from lib.core.settings import PUSH_VALUE_EXCEPTION_RETRY_COUNT
from lib.core.settings import PYVERSION
from lib.core.settings import REFERER_ALIASES
from lib.core.settings import REFLECTED_BORDER_REGEX
from lib.core.settings import REFLECTED_MAX_REGEX_PARTS
from lib.core.settings import REFLECTED_REPLACEMENT_REGEX
from lib.core.settings import REFLECTED_REPLACEMENT_TIMEOUT
from lib.core.settings import REFLECTED_VALUE_MARKER
from lib.core.settings import REFLECTIVE_MISS_THRESHOLD
from lib.core.settings import SENSITIVE_DATA_REGEX
from lib.core.settings import SENSITIVE_OPTIONS
from lib.core.settings import SUPPORTED_DBMS
from lib.core.settings import TEXT_TAG_REGEX
from lib.core.settings import TIME_STDEV_COEFF
from lib.core.settings import UNICODE_ENCODING
from lib.core.settings import UNKNOWN_DBMS_VERSION
from lib.core.settings import URI_QUESTION_MARKER
from lib.core.settings import URLENCODE_CHAR_LIMIT
from lib.core.settings import URLENCODE_FAILSAFE_CHARS
from lib.core.settings import USER_AGENT_ALIASES
from lib.core.settings import VERSION_STRING
from lib.core.threads import getCurrentThreadData
from lib.utils.sqlalchemy import _sqlalchemy
from thirdparty.clientform.clientform import ParseResponse
from thirdparty.clientform.clientform import ParseError
from thirdparty.colorama.initialise import init as coloramainit
from thirdparty.magic import magic
from thirdparty.odict.odict import OrderedDict
from thirdparty.termcolor.termcolor import colored

class UnicodeRawConfigParser(RawConfigParser):
    """
    RawConfigParser与unicode书写支持
    """

    def write(self, fp):
        """
        编写配置状态的.ini格式表示。
        """

        if self._defaults:
            fp.write("[%s]\n" % DEFAULTSECT)

            for (key, value) in self._defaults.items():
                fp.write("%s = %s\n" % (key, getUnicode(value, UNICODE_ENCODING).replace('\n', '\n\t')))

            fp.write("\n")

        for section in self._sections:
            fp.write("[%s]\n" % section)

            for (key, value) in self._sections[section].items():
                if key != "__name__":
                    if value is None:
                        fp.write("%s\n" % (key))
                    else:
                        fp.write("%s = %s\n" % (key, getUnicode(value, UNICODE_ENCODING).replace('\n', '\n\t')))

            fp.write("\n")

class Format(object):
    @staticmethod
    def humanize(values, chain=" or "):
        return chain.join(values)

    # Get方法
    @staticmethod
    def getDbms(versions=None):
        """
        格式化后端DBMS指纹值，并返回其格式为可读字符串的值。

        @return：根据指纹技术检测后端DBMS。
        @rtype：C{str}
        """

        if versions is None and Backend.getVersionList():
            versions = Backend.getVersionList()

        return Backend.getDbms() if versions is None else "%s %s" % (Backend.getDbms(), " and ".join(filter(None, versions)))

    @staticmethod
    def getErrorParsedDBMSes():
        """
        解析知识库htmlFp列表，并返回其格式为可读字符串的值。

        @return：根据错误消息解析可能的后端DBMS列表。
        @rtype：C{str}
        """

        htmlParsed = None

        if len(kb.htmlFp) == 0 or kb.heuristicTest != HEURISTIC_TEST.POSITIVE:
            pass
        elif len(kb.htmlFp) == 1:
            htmlParsed = kb.htmlFp[0]
        elif len(kb.htmlFp) > 1:
            htmlParsed = " or ".join(kb.htmlFp)

        return htmlParsed

    @staticmethod
    def getOs(target, info):
        """
        格式化后端操作系统指纹值，并返回其格式为人类可读字符串的值。

        Example of info (kb.headersFp) dictionary:

        {
          'distrib': set(['Ubuntu']),
          'type': set(['Linux']),
          'technology': set(['PHP 5.2.6', 'Apache 2.2.9']),
          'release': set(['8.10'])
        }

        Example of info (kb.bannerFp) dictionary:

        {
          'sp': set(['Service Pack 4']),
          'dbmsVersion': '8.00.194',
          'dbmsServicePack': '0',
          'distrib': set(['2000']),
          'dbmsRelease': '2000',
          'type': set(['Windows'])
        }

        @return: 基于指纹技术检测到的后端操作系统
        @rtype: C{str}
        """

        infoStr = ""
        infoApi = {}

        if info and "type" in info:
            if conf.api:
                infoApi[u"%s操作系统" % target] = info
            else:
                infoStr += u"%s操作系统: %s" % (target, Format.humanize(info["type"]))

                if "distrib" in info:
                    infoStr += " %s" % Format.humanize(info["distrib"])

                if "release" in info:
                    infoStr += " %s" % Format.humanize(info["release"])

                if "sp" in info:
                    infoStr += " %s" % Format.humanize(info["sp"])

                if "codename" in info:
                    infoStr += " (%s)" % Format.humanize(info["codename"])

        if "technology" in info:
            if conf.api:
                infoApi["web application technology"] = Format.humanize(info["technology"], ", ")
            else:
                infoStr += u"\n网站选用的WEB服务器类型和开发语言: %s" % Format.humanize(info["technology"], ", ")

        if conf.api:
            return infoApi
        else:
            return infoStr.lstrip()

class Backend:
    # Set methods
    @staticmethod
    def setDbms(dbms):
        dbms = aliasToDbmsEnum(dbms)

        if dbms is None:
            return None

        # 一点点预防，理论上这个条件应该是假的
        elif kb.dbms is not None and kb.dbms != dbms:
            warnMsg = u"很可能是误报"
            logger.warn(warnMsg)

            msg = u"以前sqlmap后端DBMS的指纹为%s" % kb.dbms
            msg += u"但现在的指纹为%s，" % dbms
            msg += u"请指定哪个DBMS应该是正确的 [%s(默认)/%s] " % (kb.dbms, dbms)

            while True:
                choice = readInput(msg, default=kb.dbms)

                if aliasToDbmsEnum(choice) == kb.dbms:
                    kb.dbmsVersion = []
                    kb.resolutionDbms = kb.dbms
                    break
                elif aliasToDbmsEnum(choice) == dbms:
                    kb.dbms = aliasToDbmsEnum(choice)
                    break
                else:
                    warnMsg = "无效值"
                    logger.warn(warnMsg)

        elif kb.dbms is None:
            kb.dbms = aliasToDbmsEnum(dbms)

        return kb.dbms

    @staticmethod
    def setVersion(version):
        if isinstance(version, basestring):
            kb.dbmsVersion = [version]

        return kb.dbmsVersion

    @staticmethod
    def setVersionList(versionsList):
        if isinstance(versionsList, list):
            kb.dbmsVersion = versionsList
        elif isinstance(versionsList, basestring):
            Backend.setVersion(versionsList)
        else:
            logger.error(u"版本列表versionsList的格式无效")

    @staticmethod
    def forceDbms(dbms, sticky=False):
        if not kb.stickyDBMS:
            kb.forcedDbms = aliasToDbmsEnum(dbms)
            kb.stickyDBMS = sticky

    @staticmethod
    def flushForcedDbms(force=False):
        if not kb.stickyDBMS or force:
            kb.forcedDbms = None
            kb.stickyDBMS = False

    @staticmethod
    def setOs(os):
        if os is None:
            return None

        # 一点点预防，理论上这个条件应该是假的
        elif kb.os is not None and isinstance(os, basestring) and kb.os.lower() != os.lower():
            msg = u"以前sqlmap后端DBMS操作系统的指纹为%s" % kb.os
            msg += u"但现在的指纹为%s，" % os
            msg += u"请指定哪个操作系统正确[%s (默认)/%s] " % (kb.os, os)

            while True:
                choice = readInput(msg, default=kb.os)

                if choice == kb.os:
                    break
                elif choice == os:
                    kb.os = choice.capitalize()
                    break
                else:
                    warnMsg = u"无效值"
                    logger.warn(warnMsg)

        elif kb.os is None and isinstance(os, basestring):
            kb.os = os.capitalize()

        return kb.os

    @staticmethod
    def setOsVersion(version):
        if version is None:
            return None

        elif kb.osVersion is None and isinstance(version, basestring):
            kb.osVersion = version

    @staticmethod
    def setOsServicePack(sp):
        if sp is None:
            return None

        elif kb.osSP is None and isinstance(sp, int):
            kb.osSP = sp

    @staticmethod
    def setArch():
        msg = u"请选择后端数据库管理系统架构类型?"
        msg += u"\n[1] 32位 (默认)"
        msg += u"\n[2] 64位"

        while True:
            choice = readInput(msg, default='1')

            if isinstance(choice, basestring) and choice.isdigit() and int(choice) in (1, 2):
                kb.arch = 32 if int(choice) == 1 else 64
                break
            else:
                warnMsg = "无效值，有效值为1和2"
                logger.warn(warnMsg)

        return kb.arch

    # Get methods
    @staticmethod
    def getForcedDbms():
        return aliasToDbmsEnum(kb.get("forcedDbms"))

    @staticmethod
    def getDbms():
        return aliasToDbmsEnum(kb.get("dbms"))

    @staticmethod
    def getErrorParsedDBMSes():
        """
        返回数组，解析DBMS名称

        这个函数被调用到:

        1. 询问用户是否在检测阶段跳过特定的DBMS测试，lib/controller/checks.py - 检测阶段。
        2. 对DBMS的指纹进行排序, lib/controller/handler.py -指纹阶段。
        """

        return kb.htmlFp if kb.get("heuristicTest") == HEURISTIC_TEST.POSITIVE else []

    @staticmethod
    def getIdentifiedDbms():
        """
        这个函数被调用到：

        对测试进行排序，getSortedInjectionTests() --检测阶段。
        等等
        """

        dbms = None

        if not kb:
            pass
        elif not kb.get("testMode") and conf.get("dbmsHandler") and getattr(conf.dbmsHandler, "_dbms", None):
            dbms = conf.dbmsHandler._dbms
        elif Backend.getForcedDbms() is not None:
            dbms = Backend.getForcedDbms()
        elif Backend.getDbms() is not None:
            dbms = Backend.getDbms()
        elif kb.get("injection") and kb.injection.dbms:
            dbms = unArrayizeValue(kb.injection.dbms)
        elif Backend.getErrorParsedDBMSes():
            dbms = unArrayizeValue(Backend.getErrorParsedDBMSes())
        elif conf.get("dbms"):
            dbms = conf.get("dbms")

        return aliasToDbmsEnum(dbms)

    @staticmethod
    def getVersion():
        versions = filter(None, flattenValue(kb.dbmsVersion))
        if not isNoneValue(versions):
            return versions[0]
        else:
            return None

    @staticmethod
    def getVersionList():
        versions = filter(None, flattenValue(kb.dbmsVersion))
        if not isNoneValue(versions):
            return versions
        else:
            return None

    @staticmethod
    def getOs():
        return kb.os

    @staticmethod
    def getOsVersion():
        return kb.osVersion

    @staticmethod
    def getOsServicePack():
        return kb.osSP

    @staticmethod
    def getArch():
        if kb.arch is None:
            Backend.setArch()
        return kb.arch

    # Comparison methods
    @staticmethod
    def isDbms(dbms):
        if not kb.get("testMode") and all((Backend.getDbms(), Backend.getIdentifiedDbms())) and Backend.getDbms() != Backend.getIdentifiedDbms():
            singleTimeWarnMessage(u"识别到('%s')和('%s')的数据库管理系统指纹不同. 如果您在枚举阶段遇到问题，请重新运行'--flush-session'" % (Backend.getIdentifiedDbms(), Backend.getDbms()))
        return Backend.getIdentifiedDbms() == aliasToDbmsEnum(dbms)

    @staticmethod
    def isDbmsWithin(aliases):
        return Backend.getDbms() is not None and Backend.getDbms().lower() in aliases

    @staticmethod
    def isVersion(version):
        return Backend.getVersion() is not None and Backend.getVersion() == version

    @staticmethod
    def isVersionWithin(versionList):
        if Backend.getVersionList() is None:
            return False

        for _ in Backend.getVersionList():
            if _ != UNKNOWN_DBMS_VERSION and _ in versionList:
                return True

        return False

    @staticmethod
    def isVersionGreaterOrEqualThan(version):
        return Backend.getVersion() is not None and str(Backend.getVersion()) >= str(version)

    @staticmethod
    def isOs(os):
        return Backend.getOs() is not None and Backend.getOs().lower() == os.lower()

def paramToDict(place, parameters=None):
    """
    将参数分为名称和值，检查这些参数是否在可测试参数内，并返回到字典中。
    """

    testableParameters = OrderedDict()

    if place in conf.parameters and not parameters:
        parameters = conf.parameters[place]

    parameters = re.sub(r"&(\w{1,4});", r"%s\g<1>%s" % (PARAMETER_AMP_MARKER, PARAMETER_SEMICOLON_MARKER), parameters)
    if place == PLACE.COOKIE:
        splitParams = parameters.split(conf.cookieDel or DEFAULT_COOKIE_DELIMITER)
    else:
        splitParams = parameters.split(conf.paramDel or DEFAULT_GET_POST_DELIMITER)

    for element in splitParams:
        element = re.sub(r"%s(.+?)%s" % (PARAMETER_AMP_MARKER, PARAMETER_SEMICOLON_MARKER), r"&\g<1>;", element)
        parts = element.split("=")

        if len(parts) >= 2:
            parameter = urldecode(parts[0].replace(" ", ""))

            if not parameter:
                continue

            if conf.paramDel and conf.paramDel == '\n':
                parts[-1] = parts[-1].rstrip()

            condition = not conf.testParameter
            condition |= conf.testParameter is not None and parameter in conf.testParameter
            condition |= place == PLACE.COOKIE and len(intersect((PLACE.COOKIE,), conf.testParameter, True)) > 0

            if condition:
                testableParameters[parameter] = "=".join(parts[1:])
                if not conf.multipleTargets and not (conf.csrfToken and parameter == conf.csrfToken):
                    _ = urldecode(testableParameters[parameter], convall=True)
                    if (_.endswith("'") and _.count("'") == 1
                      or re.search(r'\A9{3,}', _) or re.search(r'\A-\d+\Z', _) or re.search(DUMMY_USER_INJECTION, _))\
                      and not parameter.upper().startswith(GOOGLE_ANALYTICS_COOKIE_PREFIX):
                        warnMsg = u"您似乎已经提供了受污染的参数值('%s') ，" % element
                        warnMsg += u"其中可能包含手动SQL注入测试的残留字符/语句"
                        warnMsg += u"请始终只使用有效的参数值，以便sqlmap能够正常运行"
                        logger.warn(warnMsg)

                        message = u"你真的确定要继续(sqlmap可能有问题)? [y/N] "

                        if not readInput(message, default='N', boolean=True):
                            raise SqlmapSilentQuitException
                    elif not _:
                        warnMsg = u"参数'%s'的值为空" % parameter
                        warnMsg += u"请始终只使用有效的参数值，以便sqlmap能够正常运行"
                        logger.warn(warnMsg)

                if place in (PLACE.POST, PLACE.GET):
                    for regex in (r"\A((?:<[^>]+>)+\w+)((?:<[^>]+>)+)\Z", r"\A([^\w]+.*\w+)([^\w]+)\Z"):
                        match = re.search(regex, testableParameters[parameter])
                        if match:
                            try:
                                candidates = OrderedDict()

                                def walk(head, current=None):
                                    if current is None:
                                        current = head
                                    if isListLike(current):
                                        for _ in current:
                                            walk(head, _)
                                    elif isinstance(current, dict):
                                        for key in current.keys():
                                            value = current[key]
                                            if isinstance(value, (list, tuple, set, dict)):
                                                if value:
                                                    walk(head, value)
                                            elif isinstance(value, (bool, int, float, basestring)):
                                                original = current[key]
                                                if isinstance(value, bool):
                                                    current[key] = "%s%s" % (str(value).lower(), BOUNDED_INJECTION_MARKER)
                                                else:
                                                    current[key] = "%s%s" % (value, BOUNDED_INJECTION_MARKER)
                                                candidates["%s (%s)" % (parameter, key)] = re.sub("(%s\s*=\s*)%s" % (re.escape(parameter), re.escape(testableParameters[parameter])), r"\g<1>%s" % json.dumps(deserialized), parameters)
                                                current[key] = original

                                deserialized = json.loads(testableParameters[parameter])
                                walk(deserialized)

                                if candidates:
                                    message = u"对于%s参数'%s'，提供的值似乎是JSON可解串的。" % (place, parameter)
                                    message += u"你想注入里面吗? [y/N] "

                                    if not readInput(message, default='N', boolean=True):
                                        del testableParameters[parameter]
                                        testableParameters.update(candidates)
                                    break
                            except (KeyboardInterrupt, SqlmapUserQuitException):
                                raise
                            except Exception:
                                pass

                            _ = re.sub(regex, "\g<1>%s\g<%d>" % (kb.customInjectionMark, len(match.groups())), testableParameters[parameter])
                            message = u"%s参数'%s'的提供值似乎有边界，" % (place, parameter)
                            message += u"你想注入里面吗? ('%s') [y/N] " % getUnicode(_)

                            if readInput(message, default='N', boolean=True):
                                testableParameters[parameter] = re.sub(regex, "\g<1>%s\g<2>" % BOUNDED_INJECTION_MARKER, testableParameters[parameter])
                            break

    if conf.testParameter:
        if not testableParameters:
            paramStr = ", ".join(test for test in conf.testParameter)

            if len(conf.testParameter) > 1:
                warnMsg = u"提供的参数'%s'" % paramStr
                warnMsg += u"不在%s内" % place
                logger.warn(warnMsg)
            else:
                parameter = conf.testParameter[0]

                if not intersect(USER_AGENT_ALIASES + REFERER_ALIASES + HOST_ALIASES, parameter, True):
                    debugMsg = u"提供的参数'%s'" % paramStr
                    debugMsg += u"不在%s内" % place
                    logger.debug(debugMsg)

        elif len(conf.testParameter) != len(testableParameters.keys()):
            for parameter in conf.testParameter:
                if parameter not in testableParameters:
                    debugMsg = u"提供的参数'%s'" % parameter
                    debugMsg += u"不在%s内" % place
                    logger.debug(debugMsg)

    if testableParameters:
        for parameter, value in testableParameters.items():
            if value and not value.isdigit():
                for encoding in ("hex", "base64"):
                    try:
                        decoded = value.decode(encoding)
                        if len(decoded) > MIN_ENCODED_LEN_CHECK and all(_ in string.printable for _ in decoded):
                            warnMsg = u"提供的参数'%s'" % parameter
                            warnMsg += u"似乎被编码为'%s'" % encoding
                            logger.warn(warnMsg)
                            break
                    except:
                        pass

    return testableParameters

def getManualDirectories():
    directories = None
    defaultDocRoot = DEFAULT_DOC_ROOTS.get(Backend.getOs(), DEFAULT_DOC_ROOTS[OS.LINUX])

    if kb.absFilePaths:
        for absFilePath in kb.absFilePaths:
            if directories:
                break

            if directoryPath(absFilePath) == '/':
                continue

            absFilePath = normalizePath(absFilePath)
            windowsDriveLetter = None

            if isWindowsDriveLetterPath(absFilePath):
                windowsDriveLetter, absFilePath = absFilePath[:2], absFilePath[2:]
                absFilePath = ntToPosixSlashes(posixToNtSlashes(absFilePath))

            for _ in list(GENERIC_DOC_ROOT_DIRECTORY_NAMES) + [conf.hostname]:
                _ = "/%s/" % _

                if _ in absFilePath:
                    directories = "%s%s" % (absFilePath.split(_)[0], _)
                    break

            if not directories and conf.path.strip('/') and conf.path in absFilePath:
                directories = absFilePath.split(conf.path)[0]

            if directories and windowsDriveLetter:
                directories = "%s/%s" % (windowsDriveLetter, ntToPosixSlashes(directories))

    directories = normalizePath(directories)

    if conf.webRoot:
        directories = [conf.webRoot]
        infoMsg = u"使用'%s'作为Web服务器文档根目录" % conf.webRoot
        logger.info(infoMsg)
    elif directories:
        infoMsg = u"检索Web服务器文档根目录: '%s'" % directories
        logger.info(infoMsg)
    else:
        warnMsg = u"无法自动检索Web服务器文档根目录"
        logger.warn(warnMsg)

        directories = []

        message = "提供你要访问的可写目录位置?\n"
        message += u"[1] 常用位置 ('%s') (默认)\n" % ", ".join(root for root in defaultDocRoot)
        message += u"[2] 自定义位置\n"
        message += u"[3] 自定义目录列表文件\n"
        message += u"[4] 暴力搜索"
        choice = readInput(message, default='1')

        if choice == '2':
            message = u"请提供绝对目录路径，用逗号分隔列表: "
            directories = readInput(message, default="").split(',')
        elif choice == '3':
            message = u"列表文件位置?\n"
            listPath = readInput(message, default="")
            checkFile(listPath)
            directories = getFileItems(listPath)
        elif choice == '4':
            targets = set([conf.hostname])
            _ = conf.hostname.split('.')

            if _[0] == "www":
                targets.add('.'.join(_[1:]))
                targets.add('.'.join(_[1:-1]))
            else:
                targets.add('.'.join(_[:-1]))

            targets = filter(None, targets)

            for prefix in BRUTE_DOC_ROOT_PREFIXES.get(Backend.getOs(), DEFAULT_DOC_ROOTS[OS.LINUX]):
                if BRUTE_DOC_ROOT_TARGET_MARK in prefix and re.match(IP_ADDRESS_REGEX, conf.hostname):
                    continue

                for suffix in BRUTE_DOC_ROOT_SUFFIXES:
                    for target in targets:
                        if not prefix.endswith("/%s" % suffix):
                            item = "%s/%s" % (prefix, suffix)
                        else:
                            item = prefix

                        item = item.replace(BRUTE_DOC_ROOT_TARGET_MARK, target).replace("//", '/').rstrip('/')
                        if item not in directories:
                            directories.append(item)

                        if BRUTE_DOC_ROOT_TARGET_MARK not in prefix:
                            break

            infoMsg = u"使用生成的目录列表: %s" % ','.join(directories)
            logger.info(infoMsg)

            msg = u"使用任何其他自定义目录[不使用直接按Enter]: "
            answer = readInput(msg)

            if answer:
                directories.extend(answer.split(','))

        else:
            directories = defaultDocRoot

    return directories

def getAutoDirectories():
    retVal = set()

    if kb.absFilePaths:
        infoMsg = u"检索Web服务器的绝对路径: "
        infoMsg += "'%s'" % ", ".join(ntToPosixSlashes(path) for path in kb.absFilePaths)
        logger.info(infoMsg)

        for absFilePath in kb.absFilePaths:
            if absFilePath:
                directory = directoryPath(absFilePath)
                directory = ntToPosixSlashes(directory)
                retVal.add(directory)
    else:
        warnMsg = u"无法自动解析任何Web服务器路径"
        logger.warn(warnMsg)

    return list(retVal)

def filePathToSafeString(filePath):
    """
    返回给定文件路径的字符串表示形式，以保证单个文件名的使用

    >>> filePathToSafeString('C:/Windows/system32')
    'C__Windows_system32'
    """

    retVal = filePath.replace("/", "_").replace("\\", "_")
    retVal = retVal.replace(" ", "_").replace(":", "_")

    return retVal

def singleTimeDebugMessage(message):
    singleTimeLogMessage(message, logging.DEBUG)

def singleTimeWarnMessage(message):
    singleTimeLogMessage(message, logging.WARN)

def singleTimeLogMessage(message, level=logging.INFO, flag=None):
    if flag is None:
        flag = hash(message)

    if not conf.smokeTest and flag not in kb.singleLogFlags:
        kb.singleLogFlags.add(flag)
        logger.log(level, message)

def boldifyMessage(message):
    retVal = message

    if any(_ in message for _ in BOLD_PATTERNS):
        retVal = setColor(message, True)

    return retVal

def setColor(message, bold=False):
    retVal = message
    level = extractRegexResult(r"\[(?P<result>[A-Z ]+)\]", message) or kb.get("stickyLevel")

    if message and getattr(LOGGER_HANDLER, "is_tty", False):  # 着色处理程序
        if bold:
            retVal = colored(message, color=None, on_color=None, attrs=("bold",))
        elif level:
            level = getattr(logging, level, None) if isinstance(level, basestring) else level
            _ = LOGGER_HANDLER.level_map.get(level)
            if _:
                background, foreground, bold = _
                retVal = colored(message, color=foreground, on_color="on_%s" % background if background else None, attrs=("bold",) if bold else None)

            kb.stickyLevel = level if message and message[-1] != "\n" else None

    return retVal

def dataToStdout(data, forceOutput=False, bold=False, content_type=None, status=CONTENT_STATUS.IN_PROGRESS):
    """
    将文本写入stdout（控制台）流
    """

    message = ""

    if not kb.get("threadException"):
        if forceOutput or not getCurrentThreadData().disableStdOut:
            if kb.get("multiThreadMode"):
                logging._acquireLock()

            if isinstance(data, unicode):
                message = stdoutencode(data)
            else:
                message = data

            try:
                if conf.get("api"):
                    sys.stdout.write(message, status, content_type)
                else:
                    sys.stdout.write(setColor(message, bold))

                sys.stdout.flush()
            except IOError:
                pass

            if kb.get("multiThreadMode"):
                logging._releaseLock()

            kb.prependFlag = isinstance(data, basestring) and (len(data) == 1 and data not in ('\n', '\r') or len(data) > 2 and data[0] == '\r' and data[-1] != '\n')

def dataToTrafficFile(data):
    if not conf.trafficFile:
        return

    try:
        conf.trafficFP.write(data)
        conf.trafficFP.flush()
    except IOError, ex:
        errMsg = u"在尝试写入流量文件'%s'时发生错误('%s')" % (conf.trafficFile, getSafeExString(ex))
        raise SqlmapSystemException(errMsg)

def dataToDumpFile(dumpFile, data):
    try:
        dumpFile.write(data)
        dumpFile.flush()
    except IOError, ex:
        if "No space left" in getUnicode(ex):
            errMsg = u"输出设备上没有空间"
            logger.error(errMsg)
        elif "Permission denied" in getUnicode(ex):
            errMsg = u"没有权限刷新转储数据"
            logger.error(errMsg)
        else:
            raise

def dataToOutFile(filename, data):
    retVal = None

    if data:
        while True:
            retVal = os.path.join(conf.filePath, filePathToSafeString(filename))

            try:
                with open(retVal, "w+b") as f:  
                # 因为数据是原始的ASCII编码数据，所以必须保持非编码解码器
                    f.write(unicodeencode(data))
            except UnicodeEncodeError, ex:
                _ = normalizeUnicode(filename)
                if filename != _:
                    filename = _
                else:
                    errMsg = u"无法写入输出文件('%s')" % getSafeExString(ex)
                    raise SqlmapGenericException(errMsg)
            except IOError, ex:
                errMsg = u"尝试写入输出文件时出错('%s')" % getSafeExString(ex)
                raise SqlmapGenericException(errMsg)
            else:
                break

    return retVal

def readInput(message, default=None, checkBatch=True, boolean=False):
    """
    从终端读取输入
    """

    retVal = None
    kb.stickyLevel = None

    message = getUnicode(message)

    if "\n" in message:
        message += "%s> " % ("\n" if message.count("\n") > 1 else "")
    elif message[-1] == ']':
        message += " "

    if kb.get("prependFlag"):
        message = "\n%s" % message
        kb.prependFlag = False

    if conf.get("answers"):
        for item in conf.answers.split(','):
            question = item.split('=')[0].strip()
            answer = item.split('=')[1] if len(item.split('=')) > 1 else None
            if answer and question.lower() in message.lower():
                retVal = getUnicode(answer, UNICODE_ENCODING)
            elif answer is None and retVal:
                retVal = "%s,%s" % (retVal, getUnicode(item, UNICODE_ENCODING))

    if retVal:
        dataToStdout("\r%s%s\n" % (message, retVal), forceOutput=True, bold=True)

        debugMsg = u"使用给定的答案"
        logger.debug(debugMsg)

    if retVal is None:
        if checkBatch and conf.get("batch"):
            if isListLike(default):
                options = ','.join(getUnicode(opt, UNICODE_ENCODING) for opt in default)
            elif default:
                options = getUnicode(default, UNICODE_ENCODING)
            else:
                options = unicode()

            dataToStdout("\r%s%s\n" % (message, options), forceOutput=True, bold=True)

            debugMsg = u"使用默认行为，以批处理模式运行"
            logger.debug(debugMsg)

            retVal = default
        else:
            logging._acquireLock()

            if conf.get("beep"):
                beep()

            dataToStdout("\r%s" % message, forceOutput=True, bold=True)
            kb.prependFlag = False

            try:
                retVal = raw_input() or default
                retVal = getUnicode(retVal, encoding=sys.stdin.encoding) if retVal else retVal
            except:
                try:
                    time.sleep(0.05)  # Reference: http://www.gossamer-threads.com/lists/python/python/781893
                except:
                    pass
                finally:
                    kb.prependFlag = True
                    raise SqlmapUserQuitException

            finally:
                logging._releaseLock()

    if retVal and default and isinstance(default, basestring) and len(default) == 1:
        retVal = retVal.strip()

    if boolean:
        retVal = retVal.strip().upper() == 'Y'

    return retVal

def randomRange(start=0, stop=1000, seed=None):
    """
    返回给定范围内的随机整数值

    >>> random.seed(0)
    >>> randomRange(1, 500)
    423
    """

    if seed is not None:
        _ = getCurrentThreadData().random
        _.seed(seed)
        randint = _.randint
    else:
        randint = random.randint

    return int(randint(start, stop))

def randomInt(length=4, seed=None):
    """
    返回带有提供位数的随机整型值

    >>> random.seed(0)
    >>> randomInt(6)
    874254
    """

    if seed is not None:
        _ = getCurrentThreadData().random
        _.seed(seed)
        choice = _.choice
    else:
        choice = random.choice

    return int("".join(choice(string.digits if _ != 0 else string.digits.replace('0', '')) for _ in xrange(0, length)))

def randomStr(length=4, lowercase=False, alphabet=None, seed=None):
    """
    返回带有字符数的随机字符串值

    >>> random.seed(0)
    >>> randomStr(6)
    'RNvnAv'
    """

    if seed is not None:
        _ = getCurrentThreadData().random
        _.seed(seed)
        choice = _.choice
    else:
        choice = random.choice

    if alphabet:
        retVal = "".join(choice(alphabet) for _ in xrange(0, length))
    elif lowercase:
        retVal = "".join(choice(string.ascii_lowercase) for _ in xrange(0, length))
    else:
        retVal = "".join(choice(string.ascii_letters) for _ in xrange(0, length))

    return retVal

def sanitizeStr(value):
    """
    消除关于新行和换行符字符的字符串值

    >>> sanitizeStr('foo\\n\\rbar')
    u'foo bar'
    """

    return getUnicode(value).replace("\n", " ").replace("\r", "")

def getHeader(headers, key):
    """
    返回header值忽略字母大小写

    >>> getHeader({"Foo": "bar"}, "foo")
    'bar'
    """

    retVal = None
    for _ in (headers or {}):
        if _.upper() == key.upper():
            retVal = headers[_]
            break
    return retVal

def checkFile(filename, raiseOnError=True):
    """
    检查文件的存在性和可读性
    """

    valid = True

    try:
        if filename is None or not os.path.isfile(filename):
            valid = False
    except UnicodeError:
        valid = False

    if valid:
        try:
            with open(filename, "rb"):
                pass
        except:
            valid = False

    if not valid and raiseOnError:
        raise SqlmapSystemException(u"无法读取文件'%s'" % filename)

    return valid

def banner():
    """
    此功能打印sqlmap标识与其版本
    """

    if not any(_ in sys.argv for _ in ("--version", "--api")):
        # BANNER = re.sub(r"\[.\]", lambda _: "[\033[01;41m%s\033[01;49m]" % random.sample(HEURISTIC_CHECK_ALPHABET, 1)[0], BANNER)
        # 用于启发式检查的字母
        # HEURISTIC_CHECK_ALPHABET = ('"', '\'', ')', '(', ',', '.')
        _ = BANNER

        if not getattr(LOGGER_HANDLER, "is_tty", False) or "--disable-coloring" in sys.argv:
            _ = re.sub("\033.+?m", "", _)
        elif IS_WIN:
            coloramainit()

        dataToStdout(_, forceOutput=True)

def parsePasswordHash(password):
    """
    在微软SQL Server密码散列值的情况下，将其扩展到其组件。
    """

    blank = " " * 8

    if not password or password == " ":
        password = NULL

    if Backend.isDbms(DBMS.MSSQL) and password != NULL and isHexEncodedString(password):
        hexPassword = password
        password = "%s\n" % hexPassword
        password += "%sheader: %s\n" % (blank, hexPassword[:6])
        password += "%ssalt: %s\n" % (blank, hexPassword[6:14])
        password += "%smixedcase: %s\n" % (blank, hexPassword[14:54])

        if not Backend.isVersionWithin(("2005", "2008")):
            password += "%suppercase: %s" % (blank, hexPassword[54:])

    return password

def cleanQuery(query):
    """
    将所有SQL语句（相似）关键字切换为大写
    """

    retVal = query

    for sqlStatements in SQL_STATEMENTS.values():
        for sqlStatement in sqlStatements:
            queryMatch = re.search("(?i)\b(%s)\b" % sqlStatement.replace("(", "").replace(")", "").strip(), query)

            if queryMatch and "sys_exec" not in query:
                retVal = retVal.replace(queryMatch.group(1), sqlStatement.upper())

    return retVal

def setPaths(rootPath):
    """
    设置项目目录和文件的绝对路径
    """

    paths.SQLMAP_ROOT_PATH = rootPath

    # sqlmap paths
    paths.SQLMAP_EXTRAS_PATH = os.path.join(paths.SQLMAP_ROOT_PATH, "extra")
    paths.SQLMAP_PROCS_PATH = os.path.join(paths.SQLMAP_ROOT_PATH, "procs")
    paths.SQLMAP_SHELL_PATH = os.path.join(paths.SQLMAP_ROOT_PATH, "shell")
    paths.SQLMAP_TAMPER_PATH = os.path.join(paths.SQLMAP_ROOT_PATH, "tamper")
    paths.SQLMAP_WAF_PATH = os.path.join(paths.SQLMAP_ROOT_PATH, "waf")
    paths.SQLMAP_TXT_PATH = os.path.join(paths.SQLMAP_ROOT_PATH, "txt")
    paths.SQLMAP_UDF_PATH = os.path.join(paths.SQLMAP_ROOT_PATH, "udf")
    paths.SQLMAP_XML_PATH = os.path.join(paths.SQLMAP_ROOT_PATH, "xml")
    paths.SQLMAP_XML_BANNER_PATH = os.path.join(paths.SQLMAP_XML_PATH, "banner")
    paths.SQLMAP_XML_PAYLOADS_PATH = os.path.join(paths.SQLMAP_XML_PATH, "payloads")

    _ = os.path.join(os.path.expandvars(os.path.expanduser("~")), ".sqlmap")
    paths.SQLMAP_HOME_PATH = _
    paths.SQLMAP_OUTPUT_PATH = getUnicode(paths.get("SQLMAP_OUTPUT_PATH", os.path.join(_, "output")), encoding=sys.getfilesystemencoding() or UNICODE_ENCODING)
    paths.SQLMAP_DUMP_PATH = os.path.join(paths.SQLMAP_OUTPUT_PATH, "%s", "dump")
    paths.SQLMAP_FILES_PATH = os.path.join(paths.SQLMAP_OUTPUT_PATH, "%s", "files")

    # sqlmap files
    paths.OS_SHELL_HISTORY = os.path.join(_, "os.hst")
    paths.SQL_SHELL_HISTORY = os.path.join(_, "sql.hst")
    paths.SQLMAP_SHELL_HISTORY = os.path.join(_, "sqlmap.hst")
    paths.GITHUB_HISTORY = os.path.join(_, "github.hst")
    paths.CHECKSUM_MD5 = os.path.join(paths.SQLMAP_TXT_PATH, "checksum.md5")
    paths.COMMON_COLUMNS = os.path.join(paths.SQLMAP_TXT_PATH, "common-columns.txt")
    paths.COMMON_TABLES = os.path.join(paths.SQLMAP_TXT_PATH, "common-tables.txt")
    paths.COMMON_OUTPUTS = os.path.join(paths.SQLMAP_TXT_PATH, 'common-outputs.txt')
    paths.SQL_KEYWORDS = os.path.join(paths.SQLMAP_TXT_PATH, "keywords.txt")
    paths.SMALL_DICT = os.path.join(paths.SQLMAP_TXT_PATH, "smalldict.txt")
    paths.USER_AGENTS = os.path.join(paths.SQLMAP_TXT_PATH, "user-agents.txt")
    paths.WORDLIST = os.path.join(paths.SQLMAP_TXT_PATH, "wordlist.zip")
    paths.ERRORS_XML = os.path.join(paths.SQLMAP_XML_PATH, "errors.xml")
    paths.BOUNDARIES_XML = os.path.join(paths.SQLMAP_XML_PATH, "boundaries.xml")
    paths.LIVE_TESTS_XML = os.path.join(paths.SQLMAP_XML_PATH, "livetests.xml")
    paths.QUERIES_XML = os.path.join(paths.SQLMAP_XML_PATH, "queries.xml")
    paths.GENERIC_XML = os.path.join(paths.SQLMAP_XML_BANNER_PATH, "generic.xml")
    paths.MSSQL_XML = os.path.join(paths.SQLMAP_XML_BANNER_PATH, "mssql.xml")
    paths.MYSQL_XML = os.path.join(paths.SQLMAP_XML_BANNER_PATH, "mysql.xml")
    paths.ORACLE_XML = os.path.join(paths.SQLMAP_XML_BANNER_PATH, "oracle.xml")
    paths.PGSQL_XML = os.path.join(paths.SQLMAP_XML_BANNER_PATH, "postgresql.xml")

    for path in paths.values():
        if any(path.endswith(_) for _ in (".txt", ".xml", ".zip")):
            checkFile(path)

def weAreFrozen():
    """
    检查是否通过py2exe将python脚本转换成了windows上的可独立执行的可执行程序(*.exe),
    参考：http://www.py2exe.org/index.cgi/WhereAmI
    """

    return hasattr(sys, "frozen") # 如果sys中包含frozen字符串说明sqlmap被打包成了exe程序

def parseTargetDirect():
    """
    解析目标DBMS并将一些属性设置到配置单例中。
    """

    if not conf.direct:
        return

    # 一些DBMS连接器（例如pymssql）不喜欢带非美国字母的Unicode
    conf.direct = conf.direct.encode(UNICODE_ENCODING)  


    details = None
    remote = False

    for dbms in SUPPORTED_DBMS:
        details = re.search("^(?P<dbms>%s)://(?P<credentials>(?P<user>.+?)\:(?P<pass>.*)\@)?(?P<remote>(?P<hostname>[\w.-]+?)\:(?P<port>[\d]+)\/)?(?P<db>[\w\d\ \:\.\_\-\/\\\\]+?)$" % dbms, conf.direct, re.I)

        if details:
            conf.dbms = details.group("dbms")

            if details.group('credentials'):
                conf.dbmsUser = details.group("user")
                conf.dbmsPass = details.group("pass")
            else:
                if conf.dbmsCred:
                    conf.dbmsUser, conf.dbmsPass = conf.dbmsCred.split(':')
                else:
                    conf.dbmsUser = ""
                    conf.dbmsPass = ""

            if not conf.dbmsPass:
                conf.dbmsPass = None

            if details.group("remote"):
                remote = True
                conf.hostname = details.group("hostname").strip()
                conf.port = int(details.group("port"))
            else:
                conf.hostname = "localhost"
                conf.port = 0

            conf.dbmsDb = details.group("db")
            conf.parameters[None] = "direct connection"

            break

    if not details:
        errMsg = u"目标信息的语法错误, 正确的语法是"
        errMsg += u"'mysql://USER:PASSWORD@DBMS_IP:DBMS_PORT/DATABASE_NAME'"
        errMsg += u"或者'access://DATABASE_FILEPATH'"
        raise SqlmapSyntaxException(errMsg)

    for dbmsName, data in DBMS_DICT.items():
        if dbmsName == conf.dbms or conf.dbms.lower() in data[0]:
            try:
                if dbmsName in (DBMS.ACCESS, DBMS.SQLITE, DBMS.FIREBIRD):
                    if remote:
                        warnMsg = "不支持通过网络直接连接 %s DBMS" % dbmsName
                        logger.warn(warnMsg)

                        conf.hostname = "localhost"
                        conf.port = 0
                elif not remote:
                    errMsg = u"缺少远程连接细节 (例如"
                    errMsg += u"'mysql://USER:PASSWORD@DBMS_IP:DBMS_PORT/DATABASE_NAME'"
                    errMsg += u"或'access://DATABASE_FILEPATH')"
                    raise SqlmapSyntaxException(errMsg)

                if dbmsName in (DBMS.MSSQL, DBMS.SYBASE):
                    import _mssql
                    import pymssql

                    if not hasattr(pymssql, "__version__") or pymssql.__version__ < "1.0.2":
                        errMsg = u"'%s'的第三方库必须是version >= 1.0.2才能正常工作。" % data[1]
                        errMsg += "从'%s'下载" % data[2]
                        raise SqlmapMissingDependence(errMsg)

                elif dbmsName == DBMS.MYSQL:
                    import pymysql
                elif dbmsName == DBMS.PGSQL:
                    import psycopg2
                elif dbmsName == DBMS.ORACLE:
                    import cx_Oracle
                elif dbmsName == DBMS.SQLITE:
                    import sqlite3
                elif dbmsName == DBMS.ACCESS:
                    import pyodbc
                elif dbmsName == DBMS.FIREBIRD:
                    import kinterbasdb
            except ImportError:
                if _sqlalchemy and data[3] in _sqlalchemy.dialects.__all__:
                    pass
                else:
                    errMsg = u"sqlmap需要第三方库'%s'才能直接连接到DBMS " % data[1]
                    errMsg += u"'%s'， 您可以从'%s'下载。" % (dbmsName, data[2])
                    errMsg += u"另一种方法是使用一个'python-sqlalchemy'软件包来支持安装的方言'%s'" % data[3]
                    raise SqlmapMissingDependence(errMsg)

def parseTargetUrl():
    """
    解析目标URL并将一些属性设置为配置单例
    """

    if not conf.url:
        return

    originalUrl = conf.url

    if re.search("\[.+\]", conf.url) and not socket.has_ipv6:
        errMsg = u"此平台不支持IPv6寻址"
        raise SqlmapGenericException(errMsg)

    if not re.search("^http[s]*://", conf.url, re.I) and \
            not re.search("^ws[s]*://", conf.url, re.I):
        if ":443/" in conf.url:
            conf.url = "https://" + conf.url
        else:
            conf.url = "http://" + conf.url

    if kb.customInjectionMark in conf.url:
        conf.url = conf.url.replace('?', URI_QUESTION_MARKER)

    try:
        urlSplit = urlparse.urlsplit(conf.url)
    except ValueError, ex:
        errMsg = "已提供的URL'%s'无效('%s')，" % (conf.url, getSafeExString(ex))
        errMsg += u"请确保您在主机名部分中没有任何多余字符（例如'['或']'）"
        raise SqlmapGenericException(errMsg)

    hostnamePort = urlSplit.netloc.split(":") if not re.search("\[.+\]", urlSplit.netloc) else filter(None, (re.search("\[.+\]", urlSplit.netloc).group(0), re.search("\](:(?P<port>\d+))?", urlSplit.netloc).group("port")))

    conf.scheme = urlSplit.scheme.strip().lower() if not conf.forceSSL else "https"
    conf.path = urlSplit.path.strip()
    conf.hostname = hostnamePort[0].strip()

    conf.ipv6 = conf.hostname != conf.hostname.strip("[]")
    conf.hostname = conf.hostname.strip("[]").replace(kb.customInjectionMark, "")

    try:
        _ = conf.hostname.encode("idna")
    except LookupError:
        _ = conf.hostname.encode(UNICODE_ENCODING)
    except UnicodeError:
        _ = None

    if any((_ is None, re.search(r'\s', conf.hostname), '..' in conf.hostname, conf.hostname.startswith('.'), '\n' in originalUrl)):
        errMsg = u"无效的目标网址('%s')" % originalUrl
        raise SqlmapSyntaxException(errMsg)

    if len(hostnamePort) == 2:
        try:
            conf.port = int(hostnamePort[1])
        except:
            errMsg = u"无效的目标 URL"
            raise SqlmapSyntaxException(errMsg)
    elif conf.scheme == "https":
        conf.port = 443
    else:
        conf.port = 80

    if conf.port < 1 or conf.port > 65535:
        errMsg = u"无效的目标URL端口 (%d)" % conf.port
        raise SqlmapSyntaxException(errMsg)

    conf.url = getUnicode("%s://%s:%d%s" % (conf.scheme, ("[%s]" % conf.hostname) if conf.ipv6 else conf.hostname, conf.port, conf.path))
    conf.url = conf.url.replace(URI_QUESTION_MARKER, '?')

    if urlSplit.query:
        if '=' not in urlSplit.query:
            conf.url = "%s?%s" % (conf.url, getUnicode(urlSplit.query))
        else:
            conf.parameters[PLACE.GET] = urldecode(urlSplit.query) if urlSplit.query and urlencode(DEFAULT_GET_POST_DELIMITER, None) not in urlSplit.query else urlSplit.query

    if not conf.referer and (intersect(REFERER_ALIASES, conf.testParameter, True) or conf.level >= 3):
        debugMsg = u"设置HTTP Referer header到目标URL"
        logger.debug(debugMsg)
        conf.httpHeaders = [_ for _ in conf.httpHeaders if _[0] != HTTP_HEADER.REFERER]
        conf.httpHeaders.append((HTTP_HEADER.REFERER, conf.url.replace(kb.customInjectionMark, "")))

    if not conf.host and (intersect(HOST_ALIASES, conf.testParameter, True) or conf.level >= 5):
        debugMsg = u"设置HTTP主机头到目标URL"
        logger.debug(debugMsg)
        conf.httpHeaders = [_ for _ in conf.httpHeaders if _[0] != HTTP_HEADER.HOST]
        conf.httpHeaders.append((HTTP_HEADER.HOST, getHostHeader(conf.url)))

    if conf.url != originalUrl:
        kb.originalUrls[conf.url] = originalUrl

def expandAsteriskForColumns(expression):
    """
    如果用户提供了一个星号而不是列名，
    sqlmap将检索列本身并重新处理SQL查询字符串（表达式）
    """

    asterisk = re.search("^SELECT(\s+TOP\s+[\d]+)?\s+\*\s+FROM\s+`?([^`\s()]+)", expression, re.I)

    if asterisk:
        infoMsg = u"您没有在查询中提供字段。sqlmap将检索列名本身 "
        logger.info(infoMsg)

        _ = asterisk.group(2).replace("..", ".").replace(".dbo.", ".")
        db, conf.tbl = _.split(".", 1) if '.' in _ else (None, _)
        if db is None:
            if expression != conf.query:
                conf.db = db
            else:
                expression = re.sub(r"([^\w])%s" % re.escape(conf.tbl), "\g<1>%s.%s" % (conf.db, conf.tbl), expression)
        else:
            conf.db = db
        conf.db = safeSQLIdentificatorNaming(conf.db)
        conf.tbl = safeSQLIdentificatorNaming(conf.tbl, True)

        columnsDict = conf.dbmsHandler.getColumns(onlyColNames=True)

        if columnsDict and conf.db in columnsDict and conf.tbl in columnsDict[conf.db]:
            columns = columnsDict[conf.db][conf.tbl].keys()
            columns.sort()
            columnsStr = ", ".join(column for column in columns)
            expression = expression.replace("*", columnsStr, 1)

            infoMsg = u"具有扩展列名称的查询是: %s" % expression
            logger.info(infoMsg)

    return expression

def getLimitRange(count, plusOne=False):
    """
    返回在limit/offset结构中使用的值的范围

    >>> [_ for _ in getLimitRange(10)]
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    """

    retVal = None
    count = int(count)
    limitStart, limitStop = 1, count

    if kb.dumpTable:
        if isinstance(conf.limitStop, int) and conf.limitStop > 0 and conf.limitStop < limitStop:
            limitStop = conf.limitStop

        if isinstance(conf.limitStart, int) and conf.limitStart > 0 and conf.limitStart <= limitStop:
            limitStart = conf.limitStart

    retVal = xrange(limitStart, limitStop + 1) if plusOne else xrange(limitStart - 1, limitStop)

    return retVal

def parseUnionPage(page):
    """
    Returns resulting items from UNION query inside provided page content
    从UNION查询返回结果项提供的页面内容
    """

    if page is None:
        return None

    if re.search("(?si)\A%s.*%s\Z" % (kb.chars.start, kb.chars.stop), page):
        # 警告用户在完整的UNION查询注入中，由于大量页面转储可能会导致延迟
        # LARGE_OUTPUT_THRESHOLD = 1024 ** 2
        if len(page) > LARGE_OUTPUT_THRESHOLD:
            warnMsg = u"检测到大量输出，这可能需要一段时间"
            logger.warn(warnMsg)

        data = BigArray()
        keys = set()

        for match in re.finditer("%s(.*?)%s" % (kb.chars.start, kb.chars.stop), page, re.DOTALL | re.IGNORECASE):
            entry = match.group(1)

            if kb.chars.start in entry:
                entry = entry.split(kb.chars.start)[-1]

            if kb.unionDuplicates:
                key = entry.lower()
                if key not in keys:
                    keys.add(key)
                else:
                    continue

            entry = entry.split(kb.chars.delimiter)

            if conf.hexConvert:
                entry = applyFunctionRecursively(entry, decodeHexValue)

            if kb.safeCharEncode:
                entry = applyFunctionRecursively(entry, safecharencode)

            data.append(entry[0] if len(entry) == 1 else entry)
    else:
        data = page

    if len(data) == 1 and isinstance(data[0], basestring):
        data = data[0]

    return data

def parseFilePaths(page):
    """
    检测所提供网页里面内容（可能的）绝对系统路径
    """

    if page:
        for regex in FILE_PATH_REGEXES:
            for match in re.finditer(regex, page):
                absFilePath = match.group("result").strip()
                page = page.replace(absFilePath, "")

                if isWindowsDriveLetterPath(absFilePath):
                    absFilePath = posixToNtSlashes(absFilePath)

                if absFilePath not in kb.absFilePaths:
                    kb.absFilePaths.add(absFilePath)

def getLocalIP():
    """
    获取本地IP地址（暴露于远程/目标）
    """

    retVal = None

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((conf.hostname, conf.port))
        retVal, _ = s.getsockname()
        s.close()
    except:
        debugMsg = "打开套接字socket连接到'%s'时出现错误" % conf.hostname
        logger.debug(debugMsg)

    return retVal

def getRemoteIP():
    """
    获取远程/目标IP地址
    """

    retVal = None

    try:
        retVal = socket.gethostbyname(conf.hostname)
    except socket.gaierror:
        errMsg = "'%s'主机发生地址解析问题" % conf.hostname
        singleTimeLogMessage(errMsg, logging.ERROR)

    return retVal

def getFileType(filePath):
    """
    给定文件路径返回路径内文件类型

    >>> getFileType(__file__)
    'text'
    """

    try:
        _ = magic.from_file(filePath)
    except:
        return "unknown"
    # 如果文件路径中包含"ASCII"或"text"任意一个则返回文本类型，否则为二进制类型。
    return "text" if "ASCII" in _ or "text" in _ else "binary"

def getCharset(charsetType=None):
    """
    返回列表，其中整数表示适用于推理技术的给定字符集类型的字符

    >>> getCharset(CHARSET_TYPE.BINARY)
    [0, 1, 47, 48, 49]
    """

    asciiTbl = []

    if charsetType is None:
        asciiTbl.extend(xrange(0, 128))

    # 0 or 1
    elif charsetType == CHARSET_TYPE.BINARY:
        asciiTbl.extend([0, 1])
        asciiTbl.extend(xrange(47, 50)) #48-49为数字0和1

    # 数字
    elif charsetType == CHARSET_TYPE.DIGITS:
        asciiTbl.extend([0, 1])
        asciiTbl.extend(xrange(47, 58)) #48-57为数字0-9

    # 十六进制
    elif charsetType == CHARSET_TYPE.HEXADECIMAL:
        asciiTbl.extend([0, 1])
        asciiTbl.extend(xrange(47, 58)) # 48-57为数字0-9
        asciiTbl.extend(xrange(64, 71)) # 65-70为字母A-F
        asciiTbl.extend([87, 88])  # 大写X
        asciiTbl.extend(xrange(96, 103)) # 97-102为小写字母a-f
        asciiTbl.extend([119, 120])  # 小写x

    # 字符
    elif charsetType == CHARSET_TYPE.ALPHA:
        asciiTbl.extend([0, 1])
        asciiTbl.extend(xrange(64, 91))     # 65-90为大写字母A-Z
        asciiTbl.extend(xrange(96, 123))    # 97-122为小写字母a-z

    # 字符和数字
    elif charsetType == CHARSET_TYPE.ALPHANUM:
        asciiTbl.extend([0, 1])
        asciiTbl.extend(xrange(47, 58)) # 48-57为数字0-9
        asciiTbl.extend(xrange(64, 91)) # 65-90为大写字母A-Z
        asciiTbl.extend(xrange(96, 123))# 97-122为小写字母a-z

    return asciiTbl

def directoryPath(filepath):
    """
    返回给定文件路径的目录路径

    >>> directoryPath('/var/log/apache.log')
    '/var/log'
    """

    retVal = filepath

    if filepath:
        retVal = ntpath.dirname(filepath) if isWindowsDriveLetterPath(filepath) else posixpath.dirname(filepath)

    return retVal

def normalizePath(filepath):
    """
    返回给定文件路径的规范化字符串表示

    >>> normalizePath('//var///log/apache.log')
    '//var/log/apache.log'
    """

    retVal = filepath

    if retVal:
        retVal = retVal.strip("\r\n")
        retVal = ntpath.normpath(retVal) if isWindowsDriveLetterPath(retVal) else posixpath.normpath(retVal)

    return retVal

def safeExpandUser(filepath):
    """
    Patch for a Python Issue18171 (http://bugs.python.org/issue18171)
    """

    retVal = filepath

    try:
        retVal = os.path.expanduser(filepath)
    except UnicodeError:
        _ = locale.getdefaultlocale()
        encoding = _[1] if _ and len(_) > 1 else UNICODE_ENCODING
        retVal = getUnicode(os.path.expanduser(filepath.encode(encoding)), encoding=encoding)

    return retVal

def safeStringFormat(format_, params):
    """
    Avoids problems with inappropriate string format strings
    避免不适当的字符串格式字符串的问题
    >>> safeStringFormat('SELECT foo FROM %s LIMIT %d', ('bar', '1'))
    u'SELECT foo FROM bar LIMIT 1'
    """

    if format_.count(PAYLOAD_DELIMITER) == 2:
        _ = format_.split(PAYLOAD_DELIMITER)
        _[1] = re.sub(r"(\A|[^A-Za-z0-9])(%d)([^A-Za-z0-9]|\Z)", r"\g<1>%s\g<3>", _[1])
        retVal = PAYLOAD_DELIMITER.join(_)
    else:
        retVal = re.sub(r"(\A|[^A-Za-z0-9])(%d)([^A-Za-z0-9]|\Z)", r"\g<1>%s\g<3>", format_)

    if isinstance(params, basestring):
        retVal = retVal.replace("%s", params, 1)
    elif not isListLike(params):
        retVal = retVal.replace("%s", str(params), 1)
    else:
        start, end = 0, len(retVal)
        match = re.search(r"%s(.+)%s" % (PAYLOAD_DELIMITER, PAYLOAD_DELIMITER), retVal)
        if match and PAYLOAD_DELIMITER not in match.group(1):
            start, end = match.start(), match.end()
        if retVal.count("%s", start, end) == len(params):
            for param in params:
                index = retVal.find("%s", start)
                retVal = retVal[:index] + getUnicode(param) + retVal[index + 2:]
        else:
            if any('%s' in _ for _ in conf.parameters.values()):
                parts = format_.split(' ')
                for i in xrange(len(parts)):
                    if PAYLOAD_DELIMITER in parts[i]:
                        parts[i] = parts[i].replace(PAYLOAD_DELIMITER, "")
                        parts[i] = "%s%s" % (parts[i], PAYLOAD_DELIMITER)
                        break
                format_ = ' '.join(parts)

            count = 0
            while True:
                match = re.search(r"(\A|[^A-Za-z0-9])(%s)([^A-Za-z0-9]|\Z)", retVal)
                if match:
                    if count >= len(params):
                        warnMsg = "字符串格式化过程中参数错误。"
                        warnMsg += "请通过电子邮件内容 \"%r | %r | %r\"报告给dev@sqlmap.org'" % (format_, params, retVal)
                        raise SqlmapValueException(warnMsg)
                    else:
                        retVal = re.sub(r"(\A|[^A-Za-z0-9])(%s)([^A-Za-z0-9]|\Z)", r"\g<1>%s\g<3>" % params[count], retVal, 1)
                        count += 1
                else:
                    break
    return retVal

def getFilteredPageContent(page, onlyText=True, split=" "):
    """
    返回已过滤的页面内容，无需脚本，样式和/或注释或所有HTML标签

    >>> getFilteredPageContent(u'<html><title>foobar</title><body>test</body></html>')
    u'foobar test'
    """

    retVal = page

    # 如果页面的字符集已成功识别
    if isinstance(page, unicode):
        retVal = re.sub(r"(?si)<script.+?</script>|<!--.+?-->|<style.+?</style>%s" % (r"|<[^>]+>|\t|\n|\r" if onlyText else ""), split, page)
        while retVal.find(2 * split) != -1:
            retVal = retVal.replace(2 * split, split)
        retVal = htmlunescape(retVal.strip().strip(split))

    return retVal

def getPageWordSet(page):
    """
    返回页面内容中使用的字集

    >>> sorted(getPageWordSet(u'<html><title>foobar</title><body>test</body></html>'))
    [u'foobar', u'test']
    """

    retVal = set()

    # 如果页面的字符集已成功识别
    if isinstance(page, unicode):
        _ = getFilteredPageContent(page)
        retVal = set(re.findall(r"\w+", _))

    return retVal

def showStaticWords(firstPage, secondPage):
    """
    打印出现在两个不同响应页面中的单词
    """

    infoMsg = "在动态页面内容的最长匹配部分寻找静态词"
    logger.info(infoMsg)

    firstPage = getFilteredPageContent(firstPage)
    secondPage = getFilteredPageContent(secondPage)

    infoMsg = "静态词: "

    if firstPage and secondPage:
        match = SequenceMatcher(None, firstPage, secondPage).find_longest_match(0, len(firstPage), 0, len(secondPage))
        commonText = firstPage[match[0]:match[0] + match[2]]
        commonWords = getPageWordSet(commonText)
    else:
        commonWords = None

    if commonWords:
        commonWords = list(commonWords)
        commonWords.sort(lambda a, b: cmp(a.lower(), b.lower()))

        for word in commonWords:
            if len(word) > 2:
                infoMsg += "'%s', " % word

        infoMsg = infoMsg.rstrip(", ")
    else:
        infoMsg += "None"

    logger.info(infoMsg)

def isWindowsDriveLetterPath(filepath):
    """
    如果给定的文件路径以Windows驱动器号开始，则返回True

    >>> isWindowsDriveLetterPath('C:\\boot.ini')
    True
    >>> isWindowsDriveLetterPath('/var/log/apache.log')
    False
    """

    return re.search("\A[\w]\:", filepath) is not None

def posixToNtSlashes(filepath):
    """
    Replaces all occurances of Posix slashes (/) in provided
    filepath with NT ones (\)
    将文件路径中所有出现的Posix斜杠(/)替换为(\)

    >>> posixToNtSlashes('C:/Windows')
    'C:\\\\Windows'
    """

    return filepath.replace('/', '\\') if filepath else filepath

def ntToPosixSlashes(filepath):
    """
    Replaces all occurances of NT slashes (\) in provided
    filepath with Posix ones 
    用(/)替换提供的文件路径中的所有出现的NT斜杠(\)

    >>> ntToPosixSlashes('C:\\Windows')
    'C:/Windows'
    """

    return filepath.replace('\\', '/') if filepath else filepath

def isHexEncodedString(subject):
    """
    检查所提供的字符串是否是十六进制编码

    >>> isHexEncodedString('DEADBEEF')
    True
    >>> isHexEncodedString('test')
    False
    """

    return re.match(r"\A[0-9a-fA-Fx]+\Z", subject) is not None

@cachedmethod
def getConsoleWidth(default=80):
    """
    返回控制台宽度
    """

    width = None

    if os.getenv("COLUMNS", "").isdigit():
        width = int(os.getenv("COLUMNS"))
    else:
        try:
            try:
                FNULL = open(os.devnull, 'w')
            except IOError:
                FNULL = None
            process = subprocess.Popen("stty size", shell=True, stdout=subprocess.PIPE, stderr=FNULL or subprocess.PIPE)
            stdout, _ = process.communicate()
            items = stdout.split()

            if len(items) == 2 and items[1].isdigit():
                width = int(items[1])
        except (OSError, MemoryError):
            pass

    if width is None:
        try:
            import curses

            stdscr = curses.initscr()
            _, width = stdscr.getmaxyx()
            curses.endwin()
        except:
            pass

    return width or default

def clearConsoleLine(forceOutput=False):
    """
    清除当前控制台中的行
    """

    if getattr(LOGGER_HANDLER, "is_tty", False):
        dataToStdout("\r%s\r" % (" " * (getConsoleWidth() - 1)), forceOutput)

    kb.prependFlag = False
    kb.stickyLevel = None

def parseXmlFile(xmlFile, handler):
    """
    通过给定的处理程序解析XML文件
    """

    try:
        with contextlib.closing(StringIO(readCachedFileContent(xmlFile))) as stream:
            parse(stream, handler)
    except (SAXParseException, UnicodeError), ex:
        errMsg = u"'%s'文件似乎有问题('%s')，" % (xmlFile, getSafeExString(ex))
        errMsg += u"请确保您没有进行任何更改"
        raise SqlmapInstallationException, errMsg

def getSQLSnippet(dbms, sfile, **variables):
    """
    返回位于'procs/'目录内的SQL代码片段的内容
    """

    if sfile.endswith('.sql') and os.path.exists(sfile):
        filename = sfile
    elif not sfile.endswith('.sql') and os.path.exists("%s.sql" % sfile):
        filename = "%s.sql" % sfile
    else:
        filename = os.path.join(paths.SQLMAP_PROCS_PATH, DBMS_DIRECTORY_DICT[dbms], sfile if sfile.endswith('.sql') else "%s.sql" % sfile)
        checkFile(filename)

    retVal = readCachedFileContent(filename)
    retVal = re.sub(r"#.+", "", retVal)
    retVal = re.sub(r";\s+", "; ", retVal).strip("\r\n")

    for _ in variables.keys():
        retVal = re.sub(r"%%%s%%" % _, variables[_], retVal)

    for _ in re.findall(r"%RANDSTR\d+%", retVal, re.I):
        retVal = retVal.replace(_, randomStr())

    for _ in re.findall(r"%RANDINT\d+%", retVal, re.I):
        retVal = retVal.replace(_, randomInt())

    variables = re.findall(r"(?<!\bLIKE ')%(\w+)%", retVal, re.I)

    if variables:
        errMsg = u"SQL文件'%s'中的变量未解析%s '%s'" % ("s" if len(variables) > 1 else "", ", ".join(variables), sfile)
        logger.error(errMsg)

        msg = u"是否要提供替换值? [y/N] "

        if readInput(msg, default='N', boolean=True):
            for var in variables:
                msg = u"插入变量'%s'的值: " % var
                val = readInput(msg, default="")
                retVal = retVal.replace(r"%%%s%%" % var, val)

    return retVal

def readCachedFileContent(filename, mode='rb'):
    """
    缓存读取文件内容（避免多个相同的文件读取）
    """

    if filename not in kb.cache.content:
        with kb.locks.cache:
            if filename not in kb.cache.content:
                checkFile(filename)
                try:
                    with openFile(filename, mode) as f:
                        kb.cache.content[filename] = f.read()
                except (IOError, OSError, MemoryError), ex:
                    errMsg = u"在尝试读取文件'%s'的内容时出错('%s')" % (filename, getSafeExString(ex))
                    raise SqlmapSystemException(errMsg)

    return kb.cache.content[filename]

def readXmlFile(xmlFile):
    """
    读取XML文件内容并返回其DOM表示
    """

    checkFile(xmlFile)
    retVal = minidom.parse(xmlFile).documentElement

    return retVal

def stdev(values):
    """
    计算数字列表的标准偏差
    Reference: http://www.goldb.org/corestats.html

    >>> stdev([0.9, 0.9, 0.9, 1.0, 0.8, 0.9])
    0.06324555320336757
    """

    if not values or len(values) < 2:
        return None

    key = (values[0], values[-1], len(values))

    if kb.get("cache") and key in kb.cache.stdev:
        retVal = kb.cache.stdev[key]
    else:
        avg = average(values)
        _ = reduce(lambda x, y: x + pow((y or 0) - avg, 2), values, 0.0)
        retVal = sqrt(_ / (len(values) - 1))
        if kb.get("cache"):
            kb.cache.stdev[key] = retVal

    return retVal

def average(values):
    """
    计算数字列表的算术平均值

    >>> average([0.9, 0.9, 0.9, 1.0, 0.8, 0.9])
    0.9
    """

    return (sum(values) / len(values)) if values else None

def calculateDeltaSeconds(start):
    """
    返回从开始到现在的经过时间
    """

    return time.time() - start

def initCommonOutputs():
    """
    初始化字典, 其中包含"good samaritan" 功能使用的常用输出值
    """

    kb.commonOutputs = {}
    key = None

    with openFile(paths.COMMON_OUTPUTS, 'r') as f:
        for line in f.readlines():  # 当使用codec.open()时，xreadlines不返回unicode字符串
            if line.find('#') != -1:
                line = line[:line.find('#')]

            line = line.strip()

            if len(line) > 1:
                if line.startswith('[') and line.endswith(']'):
                    key = line[1:-1]
                elif key:
                    if key not in kb.commonOutputs:
                        kb.commonOutputs[key] = set()

                    if line not in kb.commonOutputs[key]:
                        kb.commonOutputs[key].add(line)

def getFileItems(filename, commentPrefix='#', unicode_=True, lowercase=False, unique=False):
    """
    返回文件中包含的换行符分隔项
    """

    retVal = list() if not unique else OrderedDict()

    checkFile(filename)

    try:
        with openFile(filename, 'r', errors="ignore") if unicode_ else open(filename, 'r') as f:
            for line in (f.readlines() if unicode_ else f.xreadlines()):  
            # 当使用codec.open()时，xreadlines不返回unicode字符串
                if commentPrefix:
                    if line.find(commentPrefix) != -1:
                        line = line[:line.find(commentPrefix)]

                line = line.strip()

                if not unicode_:
                    try:
                        line = str.encode(line)
                    except UnicodeDecodeError:
                        continue

                if line:
                    if lowercase:
                        line = line.lower()

                    if unique and line in retVal:
                        continue

                    if unique:
                        retVal[line] = True
                    else:
                        retVal.append(line)
    except (IOError, OSError, MemoryError), ex:
        errMsg = u"在尝试读取文件'%s'的内容时出错('%s')" % (filename, getSafeExString(ex))
        raise SqlmapSystemException(errMsg)

    return retVal if not unique else retVal.keys()

def goGoodSamaritan(prevValue, originalCharset):
    """
    用于检索常用预测特征所需的参数的功能

    prevValue: 到目前为止检索到的查询输出 (e.g. 'i').

    如果参数prevValue有一个完整的单一匹配
    (在kb.partRun的kbpartRun的txt/common-outputs.txt中)，则返回commonValue。 
    如果没有单个值匹配但是有多个，则返回commonCharset，其中包含更多可能的字符
    (从txt/common-outputs.txt中的匹配值检索)以及其他charset作为otherCharset。
    """

    if kb.commonOutputs is None:
        initCommonOutputs()

    predictionSet = set()
    commonValue = None
    commonPattern = None
    countCommonValue = 0

    # 如果我们正在寻找的头(例如数据库)有共同的输出
    if kb.partRun in kb.commonOutputs:
        commonPartOutputs = kb.commonOutputs[kb.partRun]
        commonPattern = commonFinderOnly(prevValue, commonPartOutputs)

        # 如果最长的公共前缀与之前的值相同，则不要考虑它
        if commonPattern and commonPattern == prevValue:
            commonPattern = None

        # 对于每个公共的输出
        for item in commonPartOutputs:
            # 检查公共输出item是否以prevValue开头，其中prevValue是迄今为止枚举的字符
            if item.startswith(prevValue):
                commonValue = item
                countCommonValue += 1

                if len(item) > len(prevValue):
                    char = item[len(prevValue)]
                    predictionSet.add(char)

        # 如果有多个可能的公共输出，则重置单个值
        if countCommonValue > 1:
            commonValue = None

        commonCharset = []
        otherCharset = []

        # 将原始字符集拆分为常用字符（commonCharset）和其他字符（otherCharset）
        for ordChar in originalCharset:
            if chr(ordChar) not in predictionSet:
                otherCharset.append(ordChar)
            else:
                commonCharset.append(ordChar)

        commonCharset.sort()

        return commonValue, commonPattern, commonCharset, originalCharset
    else:
        return None, None, None, originalCharset

def getPartRun(alias=True):
    """
    通过调用堆栈找到匹配conf.dbmsHandler的结构
    返回它或其在txt/common-outputs.txt中使用的别名
    """

    retVal = None
    commonPartsDict = optDict["Enumeration"]

    try:
        stack = [item[4][0] if isinstance(item[4], list) else '' for item in inspect.stack()]

        # 通过堆栈向后找到调用此函数的conf.dbmsHandler方法
        for i in xrange(0, len(stack) - 1):
            for regex in (r"self\.(get[^(]+)\(\)", r"conf\.dbmsHandler\.([^(]+)\(\)"):
                match = re.search(regex, stack[i])

                if match:
                    # 这是调用conf.dbmsHandler或self方法（例如'getDbms'）
                    retVal = match.groups()[0]
                    break

            if retVal is not None:
                break

    # Reference: http://coding.derkeiler.com/Archive/Python/comp.lang.python/2004-06/2267.html
    except TypeError:
        pass

    # 返回INI标签以考虑公共输出（例如'Databases'）
    if alias:
        return commonPartsDict[retVal][1] if isinstance(commonPartsDict.get(retVal), tuple) else retVal
    else:
        return retVal

def getUnicode(value, encoding=None, noneToNull=False):
    """
    返回提供的值的unicode表示形式：

    >>> getUnicode(u'test')
    u'test'
    >>> getUnicode('test')
    u'test'
    >>> getUnicode(1)
    u'1'
    """

    if noneToNull and value is None:
        return NULL

    if isinstance(value, unicode):
        return value
    elif isinstance(value, basestring):
        while True:
            try:
                return unicode(value, encoding or (kb.get("pageEncoding") if kb.get("originalPage") else None) or UNICODE_ENCODING)
            except UnicodeDecodeError, ex:
                try:
                    return unicode(value, UNICODE_ENCODING)
                except:
                    # 用于表示无效unicode字符的格式
                    # INVALID_UNICODE_CHAR_FORMAT = r"\x%02x"
                    value = value[:ex.start] + "".join(INVALID_UNICODE_CHAR_FORMAT % ord(_) for _ in value[ex.start:ex.end]) + value[ex.end:]
    elif isListLike(value):
        value = list(getUnicode(_, encoding, noneToNull) for _ in value)
        return value
    else:
        try:
            return unicode(value)
        except UnicodeDecodeError:
            return unicode(str(value), errors="ignore")  # encoding ignored for non-basestring instances

def longestCommonPrefix(*sequences):
    """
    返回给定序列中最长的公共前缀
    Reference: http://boredzo.org/blog/archives/2007-01-06/longest-common-prefix-in-python-2

    >>> longestCommonPrefix('foobar', 'fobar')
    'fo'
    """

    if len(sequences) == 1:
        return sequences[0]

    sequences = [pair[1] for pair in sorted((len(fi), fi) for fi in sequences)]

    if not sequences:
        return None

    for i, comparison_ch in enumerate(sequences[0]):
        for fi in sequences[1:]:
            ch = fi[i]

            if ch != comparison_ch:
                return fi[:i]

    return sequences[0]

def commonFinderOnly(initial, sequence):
    return longestCommonPrefix(*filter(lambda x: x.startswith(initial), sequence))

def pushValue(value):
    """
    将值push到堆栈（线程依赖）
    """

    _ = None
    success = False

    for i in xrange(PUSH_VALUE_EXCEPTION_RETRY_COUNT):
        try:
            getCurrentThreadData().valueStack.append(copy.deepcopy(value))
            success = True
            break
        except Exception, ex:
            _ = ex

    if not success:
        getCurrentThreadData().valueStack.append(None)

        if _:
            raise _

def popValue():
    """
    从堆栈弹出值（线程依赖）

    >>> pushValue('foobar')
    >>> popValue()
    'foobar'
    """

    return getCurrentThreadData().valueStack.pop()

def wasLastResponseDBMSError():
    """
    如果最后一个Web请求导致（已识别）DBMS错误页面，则返回True
    """

    threadData = getCurrentThreadData()
    return threadData.lastErrorPage and threadData.lastErrorPage[0] == threadData.lastRequestUID

def wasLastResponseHTTPError():
    """
    如果最后一个Web请求导致HTTP代码错误（如500），则返回True
    """

    threadData = getCurrentThreadData()
    return threadData.lastHTTPError and threadData.lastHTTPError[0] == threadData.lastRequestUID

def wasLastResponseDelayed():
    """
    如果最后一个Web请求导致时间延迟，则返回True
    """

    # 99.9999999997440%的所有非基于时间的 SQL 注入受影响的响应次数应在内部 +-7*stdev([正常响应时间])
    # Math reference: http://www.answers.com/topic/standard-deviation

    deviation = stdev(kb.responseTimes.get(kb.responseTimeMode, []))
    threadData = getCurrentThreadData()

    if deviation and not conf.direct and not conf.disableStats:
        if len(kb.responseTimes[kb.responseTimeMode]) < MIN_TIME_RESPONSES:
            warnMsg = u"在具有小于%d响应时间的模型上使用基于时间的标准偏差方法" % MIN_TIME_RESPONSES
            logger.warn(warnMsg)

        lowerStdLimit = average(kb.responseTimes[kb.responseTimeMode]) + TIME_STDEV_COEFF * deviation
        retVal = (threadData.lastQueryDuration >= max(MIN_VALID_DELAYED_RESPONSE, lowerStdLimit))

        if not kb.testMode and retVal:
            if kb.adjustTimeDelay is None:
                msg = u"你想要sqlmap尝试优化DBMS延迟响应的值(选项 '--time-sec')? [Y/n] "

                kb.adjustTimeDelay = ADJUST_TIME_DELAY.DISABLE if not readInput(msg, default='Y', boolean=True) else ADJUST_TIME_DELAY.YES
            if kb.adjustTimeDelay is ADJUST_TIME_DELAY.YES:
                adjustTimeDelay(threadData.lastQueryDuration, lowerStdLimit)

        return retVal
    else:
        delta = threadData.lastQueryDuration - conf.timeSec
        if Backend.getIdentifiedDbms() in (DBMS.MYSQL,):  # MySQL的SLEEP(X)平均持续时间缩短0.05秒
            delta += 0.05
        return delta >= 0

def adjustTimeDelay(lastQueryDuration, lowerStdLimit):
    """
    提供在基于时间的数据检索中调整延时的提示
    """

    candidate = 1 + int(round(lowerStdLimit))

    if candidate:
        kb.delayCandidates = [candidate] + kb.delayCandidates[:-1]

        if all((x == candidate for x in kb.delayCandidates)) and candidate < conf.timeSec:
            conf.timeSec = candidate

            infoMsg = u"由于良好的响应时间，将时间延迟调整为%d%s秒" % (conf.timeSec, 's' if conf.timeSec > 1 else '')
            logger.info(infoMsg)

def getLastRequestHTTPError():
    """
    返回上一个HTTP错误代码
    """

    threadData = getCurrentThreadData()
    return threadData.lastHTTPError[1] if threadData.lastHTTPError else None

def extractErrorMessage(page):
    """
    从页面返回报告的错误消息，如果它找到一个

    >>> extractErrorMessage(u'<html><title>Test</title>\\n<b>Warning</b>: oci_parse() [function.oci-parse]: ORA-01756: quoted string not properly terminated<br><p>Only a test page</p></html>')
    u'oci_parse() [function.oci-parse]: ORA-01756: quoted string not properly terminated'
    """

    retVal = None

    if isinstance(page, basestring):
        for regex in ERROR_PARSING_REGEXES:
            match = re.search(regex, page, re.DOTALL | re.IGNORECASE)

            if match:
                retVal = htmlunescape(match.group("result")).replace("<br>", "\n").strip()
                break

    return retVal

def findLocalPort(ports):
    """
    从给定的端口列表中查找第一个打开的本地主机端口（例如，用于Tor端口检查）
    """

    retVal = None

    for port in ports:
        try:
            try:
                s = socket._orig_socket(socket.AF_INET, socket.SOCK_STREAM)
            except AttributeError:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((LOCALHOST, port))
            retVal = port
            break
        except socket.error:
            pass
        finally:
            try:
                s.close()
            except socket.error:
                pass

    return retVal

def findMultipartPostBoundary(post):
    """
    在给定的多部分POST主体中找到边界参数的值
    """

    retVal = None

    done = set()
    candidates = []

    for match in re.finditer(r"(?m)^--(.+?)(--)?$", post or ""):
        _ = match.group(1).strip().strip('-')

        if _ in done:
            continue
        else:
            candidates.append((post.count(_), _))
            done.add(_)

    if candidates:
        candidates.sort(key=lambda _: _[0], reverse=True)
        retVal = candidates[0][1]

    return retVal

def urldecode(value, encoding=None, unsafe="%%&=;+%s" % CUSTOM_INJECTION_MARK_CHAR, convall=False, plusspace=True):
    """
    URL解码给定值

    >>> urldecode('AND%201%3E%282%2B3%29%23', convall=True)
    u'AND 1>(2+3)#'
    """

    result = value

    if value:
        try:
            # for cases like T%C3%BCrk%C3%A7e
            value = str(value)
        except ValueError:
            pass
        finally:
            if convall:
                result = urllib.unquote_plus(value) if plusspace else urllib.unquote(value)
            else:
                def _(match):
                    charset = reduce(lambda x, y: x.replace(y, ""), unsafe, string.printable)
                    char = chr(ord(match.group(1).decode("hex")))
                    return char if char in charset else match.group(0)
                result = value
                if plusspace:
                    result = result.replace("+", " ")  
                    # 加号在URL编码数据中具有特殊含义(在urallib.unquote_plus使用情况下)
                result = re.sub("%([0-9a-fA-F]{2})", _, result)

    if isinstance(result, str):
        result = unicode(result, encoding or UNICODE_ENCODING, "replace")

    return result

def urlencode(value, safe="%&=-_", convall=False, limit=False, spaceplus=False):
    """
    URL编码给定值

    >>> urlencode('AND 1>(2+3)#')
    'AND%201%3E%282%2B3%29%23'
    """

    if conf.get("direct"):
        return value

    count = 0
    result = None if value is None else ""

    if value:
        if Backend.isDbms(DBMS.MSSQL) and not kb.tamperFunctions and any(ord(_) > 255 for _ in value):
            warnMsg = u"如果您遇到非ASCII标识符名称的问题，"
            warnMsg += u"建议您重新运行'--tamper=charunicodeencode'"
            singleTimeWarnMessage(warnMsg)

        if convall or safe is None:
            safe = ""

        # 当字符 ‘ % ’ 真的需要被编码的情况下，除了使用篡改脚本的情况下
        # (不表示URL编码的字符)
        if all('%' in _ for _ in (safe, value)) and not kb.tamperFunctions:
            value = re.sub("%(?![0-9a-fA-F]{2})", "%25", value)

        while True:
            result = urllib.quote(utf8encode(value), safe)

            if limit and len(result) > URLENCODE_CHAR_LIMIT:
                if count >= len(URLENCODE_FAILSAFE_CHARS):
                    break

                while count < len(URLENCODE_FAILSAFE_CHARS):
                    safe += URLENCODE_FAILSAFE_CHARS[count]
                    count += 1
                    if safe[-1] in value:
                        break
            else:
                break

        if spaceplus:
            result = result.replace(urllib.quote(' '), '+')

    return result

def runningAsAdmin():
    """
    如果当前进程在管理员权限下运行，则返回True
    """

    isAdmin = None

    if PLATFORM in ("posix", "mac"):
        _ = os.geteuid()

        isAdmin = isinstance(_, (int, float, long)) and _ == 0
    elif IS_WIN:
        import ctypes

        _ = ctypes.windll.shell32.IsUserAnAdmin()

        isAdmin = isinstance(_, (int, float, long)) and _ == 1
    else:
        errMsg = u"sqlmap无法检查您是否在此平台上作为管理员帐户运行它。"
        errMsg += u"sqlmap将假定您是一个管理员，这是被请求的接管攻击所必需的。"
        logger.error(errMsg)

        isAdmin = True

    return isAdmin

def logHTTPTraffic(requestLogMsg, responseLogMsg, startTime=None, endTime=None):
    """
    将HTTP流量记录到输出文件
    """

    if conf.harFile:
        conf.httpCollector.collectRequest(requestLogMsg, responseLogMsg, startTime, endTime)

    if conf.trafficFile:
        with kb.locks.log:
            dataToTrafficFile("%s%s" % (requestLogMsg, os.linesep))
            dataToTrafficFile("%s%s" % (responseLogMsg, os.linesep))
            dataToTrafficFile("%s%s%s%s" % (os.linesep, 76 * '#', os.linesep, os.linesep))

def getPageTemplate(payload, place):  # Cross-linked function
    raise NotImplementedError

@cachedmethod
def getPublicTypeMembers(type_, onlyValues=False):
    """
    适用于从类型中获取成员 (例如在枚举中)

    >>> [_ for _ in getPublicTypeMembers(OS, True)]
    ['Linux', 'Windows']
    """

    retVal = []

    for name, value in inspect.getmembers(type_):
        if not name.startswith("__"):
            if not onlyValues:
                retVal.append((name, value))
            else:
                retVal.append(value)

    return retVal

def enumValueToNameLookup(type_, value_):
    """
    返回具有给定值的枚举成员的名称

    >>> enumValueToNameLookup(SORT_ORDER, 100)
    'LAST'
    """

    retVal = None

    for name, value in getPublicTypeMembers(type_):
        if value == value_:
            retVal = name
            break

    return retVal

def extractRegexResult(regex, content, flags=0):
    """
    正则表达式从给定的内容中匹配后返回'result'组值

    >>> extractRegexResult(r'a(?P<result>[^g]+)g', 'abcdefg')
    'bcdef'
    """

    retVal = None

    if regex and content and "?P<result>" in regex:
        match = re.search(regex, content, flags)

        if match:
            retVal = match.group("result")

    return retVal

def extractTextTagContent(page):
    """
    返回包含 "文本" 标签内容的列表

    >>> extractTextTagContent(u'<html><head><title>Title</title></head><body><pre>foobar</pre><a href="#link">Link</a></body></html>')
    [u'Title', u'foobar']
    """

    page = page or ""

    if REFLECTED_VALUE_MARKER in page:
        try:
            page = re.sub(r"(?i)[^\s>]*%s[^\s<]*" % REFLECTED_VALUE_MARKER, "", page)
        except MemoryError:
            page = page.replace(REFLECTED_VALUE_MARKER, "")

    return filter(None, (_.group("result").strip() for _ in re.finditer(TEXT_TAG_REGEX, page)))

def trimAlphaNum(value):
    """
    从给定值的起始和结束截取字母数字字符

    >>> trimAlphaNum(u'AND 1>(2+3)-- foobar')
    u' 1>(2+3)-- '
    """

    while value and value[-1].isalnum():
        value = value[:-1]

    while value and value[0].isalnum():
        value = value[1:]

    return value

def isNumPosStrValue(value):
    """
    如果value是具有正整数表示形式的字符串（或整数），则返回True

    >>> isNumPosStrValue(1)
    True
    >>> isNumPosStrValue('1')
    True
    >>> isNumPosStrValue(0)
    False
    >>> isNumPosStrValue('-2')
    False
    """

    return (value and isinstance(value, basestring) and value.isdigit() and int(value) > 0) or (isinstance(value, int) and value > 0)

@cachedmethod
def aliasToDbmsEnum(dbms):
    """
    从给定的别名返回主要的DBMS名称

    >>> aliasToDbmsEnum('mssql')
    'Microsoft SQL Server'
    """

    retVal = None

    if dbms:
        for key, item in DBMS_DICT.items():
            if dbms.lower() in item[0] or dbms.lower() == key.lower():
                retVal = key
                break

    return retVal

def findDynamicContent(firstPage, secondPage):
    """
    此功能检查提供的页面是否具有动态内容。 如果它们是动态的，将会进行适当的标记
    """

    if not firstPage or not secondPage:
        return

    infoMsg = u"搜索动态内容"
    logger.info(infoMsg)

    blocks = SequenceMatcher(None, firstPage, secondPage).get_matching_blocks()
    kb.dynamicMarkings = []

    # 删除太小的匹配块
    for block in blocks[:]:
        (_, _, length) = block

        if length <= DYNAMICITY_MARK_LENGTH:
            blocks.remove(block)

    # 根据前缀/后缀原则制作动态标记
    if len(blocks) > 0:
        blocks.insert(0, None)
        blocks.append(None)

        for i in xrange(len(blocks) - 1):
            prefix = firstPage[blocks[i][0]:blocks[i][0] + blocks[i][2]] if blocks[i] else None
            suffix = firstPage[blocks[i + 1][0]:blocks[i + 1][0] + blocks[i + 1][2]] if blocks[i + 1] else None

            if prefix is None and blocks[i + 1][0] == 0:
                continue

            if suffix is None and (blocks[i][0] + blocks[i][2] >= len(firstPage)):
                continue

            prefix = trimAlphaNum(prefix)
            suffix = trimAlphaNum(suffix)

            kb.dynamicMarkings.append((prefix[-DYNAMICITY_MARK_LENGTH / 2:] if prefix else None, suffix[:DYNAMICITY_MARK_LENGTH / 2] if suffix else None))

    if len(kb.dynamicMarkings) > 0:
        infoMsg = "标记为删除的动态内容(%d区域%s)" % (len(kb.dynamicMarkings), 's' if len(kb.dynamicMarkings) > 1 else '')
        logger.info(infoMsg)

def removeDynamicContent(page):
    """
    从提供的页面中删除动态内容，基于预先计算的动态标记
    """

    if page:
        for item in kb.dynamicMarkings:
            prefix, suffix = item

            if prefix is None and suffix is None:
                continue
            elif prefix is None:
                page = re.sub(r"(?s)^.+%s" % re.escape(suffix), suffix.replace('\\', r'\\'), page)
            elif suffix is None:
                page = re.sub(r"(?s)%s.+$" % re.escape(prefix), prefix.replace('\\', r'\\'), page)
            else:
                page = re.sub(r"(?s)%s.+%s" % (re.escape(prefix), re.escape(suffix)), "%s%s" % (prefix.replace('\\', r'\\'), suffix.replace('\\', r'\\')), page)

    return page

def filterStringValue(value, charRegex, replacement=""):
    """
    返回仅包含满足提供的正则表达式匹配的字符的字符串值（注意：必须以[...]形式）
    >>> filterStringValue(u'wzydeadbeef0123#', r'[0-9a-f]')
    u'deadbeef0123'
    """

    retVal = value

    if value:
        retVal = re.sub(charRegex.replace("[", "[^") if "[^" not in charRegex else charRegex.replace("[^", "["), replacement, value)

    return retVal

def filterControlChars(value):
    """
    返回字符串值，将控制字符替换为''

    >>> filterControlChars(u'AND 1>(2+3)\\n--')
    u'AND 1>(2+3) --'
    """
    # PRINTABLE_CHAR_REGEX = r"[^\x00-\x1f\x7f-\xff]"
    # 十六进制--->十进制
    # \x7f-\xff表示ASCII字符从127到255，其中\为转义。
    # x00-x1f表示ASCII字符从0-31为控制字符
    return filterStringValue(value, PRINTABLE_CHAR_REGEX, ' ')

def isDBMSVersionAtLeast(version):
    """
    检查识别的DBMS版本是否至少是指定的版本
    """

    retVal = None

    if Backend.getVersion() and Backend.getVersion() != UNKNOWN_DBMS_VERSION:
        value = Backend.getVersion().replace(" ", "").rstrip('.')

        while True:
            index = value.find('.', value.find('.') + 1)

            if index > -1:
                value = value[0:index] + value[index + 1:]
            else:
                break

        value = filterStringValue(value, '[0-9.><=]')

        if isinstance(value, basestring):
            if value.startswith(">="):
                value = float(value.replace(">=", ""))
            elif value.startswith(">"):
                value = float(value.replace(">", "")) + 0.01
            elif value.startswith("<="):
                value = float(value.replace("<=", ""))
            elif value.startswith(">"):
                value = float(value.replace("<", "")) - 0.01

        retVal = getUnicode(value) >= getUnicode(version)

    return retVal

def parseSqliteTableSchema(value):
    """
    从指定的SQLite表模式中解析表列名称和类型
    """

    if value:
        table = {}
        columns = {}

        for match in re.finditer(r"(\w+)[\"'`]?\s+(INT|INTEGER|TINYINT|SMALLINT|MEDIUMINT|BIGINT|UNSIGNED BIG INT|INT2|INT8|INTEGER|CHARACTER|VARCHAR|VARYING CHARACTER|NCHAR|NATIVE CHARACTER|NVARCHAR|TEXT|CLOB|LONGTEXT|BLOB|NONE|REAL|DOUBLE|DOUBLE PRECISION|FLOAT|REAL|NUMERIC|DECIMAL|BOOLEAN|DATE|DATETIME|NUMERIC)\b", value, re.I):
            columns[match.group(1)] = match.group(2)

        table[conf.tbl] = columns
        kb.data.cachedColumns[conf.db] = table

def getTechniqueData(technique=None):
    """
    返回指定技术的注入数据
    """

    return kb.injection.data.get(technique)

def isTechniqueAvailable(technique):
    """
    如果有数据可以使用sqlmap指定的技术注入，则返回True
    """

    if conf.tech and isinstance(conf.tech, list) and technique not in conf.tech:
        return False
    else:
        return getTechniqueData(technique) is not None

def isStackingAvailable():
    """
    堆叠Stack技术是否可用，可用返回True
    """

    retVal = False

    if PAYLOAD.TECHNIQUE.STACKED in kb.injection.data:
        retVal = True
    else:
        for technique in getPublicTypeMembers(PAYLOAD.TECHNIQUE, True):
            _ = getTechniqueData(technique)
            if _ and "stacked" in _["title"].lower():
                retVal = True
                break

    return retVal

def isInferenceAvailable():
    """
    推理技术是否可以使用, 可用返回True
    """

    return any(isTechniqueAvailable(_) for _ in (PAYLOAD.TECHNIQUE.BOOLEAN, PAYLOAD.TECHNIQUE.STACKED, PAYLOAD.TECHNIQUE.TIME))

def setOptimize():
    """
    设置通过开关'-o'开启的选项
    """

    #conf.predictOutput = True
    conf.keepAlive = True
    conf.threads = 3 if conf.threads < 3 else conf.threads
    conf.nullConnection = not any((conf.data, conf.textOnly, conf.titles, conf.string, conf.notString, conf.regexp, conf.tor))

    if not conf.nullConnection:
        debugMsg = u"关闭开关'--null-connection'间接使用开关'-o'"
        logger.debug(debugMsg)

def saveConfig(conf, filename):
    """
    将conf保存到配置文件名
    """

    config = UnicodeRawConfigParser()
    userOpts = {}

    for family in optDict.keys():
        userOpts[family] = []

    for option, value in conf.items():
        for family, optionData in optDict.items():
            if option in optionData:
                userOpts[family].append((option, value, optionData[option]))

    for family, optionData in userOpts.items():
        config.add_section(family)

        optionData.sort()

        for option, value, datatype in optionData:
            if datatype and isListLike(datatype):
                datatype = datatype[0]

            if option in IGNORE_SAVE_OPTIONS:
                continue

            if value is None:
                if datatype == OPTION_TYPE.BOOLEAN:
                    value = "False"
                elif datatype in (OPTION_TYPE.INTEGER, OPTION_TYPE.FLOAT):
                    if option in defaults:
                        value = str(defaults[option])
                    else:
                        value = "0"
                elif datatype == OPTION_TYPE.STRING:
                    value = ""

            if isinstance(value, basestring):
                value = value.replace("\n", "\n ")

            config.set(family, option, value)

    with openFile(filename, "wb") as f:
        try:
            config.write(f)
        except IOError, ex:
            errMsg = u"尝试写入配置文件'%s'时发生错误('%s')" % (filename, getSafeExString(ex))
            raise SqlmapSystemException(errMsg)

def initTechnique(technique=None):
    """
    准备指定技术的数据
    """

    try:
        data = getTechniqueData(technique)
        resetCounter(technique)

        if data:
            kb.pageTemplate, kb.errorIsNone = getPageTemplate(data.templatePayload, kb.injection.place)
            kb.matchRatio = data.matchRatio
            kb.negativeLogic = (technique == PAYLOAD.TECHNIQUE.BOOLEAN) and (data.where == PAYLOAD.WHERE.NEGATIVE)

            # 恢复存储的conf选项
            for key, value in kb.injection.conf.items():
                if value and (not hasattr(conf, key) or (hasattr(conf, key) and not getattr(conf, key))):
                    setattr(conf, key, value)
                    debugMsg = u"恢复配置选项 '%s' (%s)" % (key, value)
                    logger.debug(debugMsg)

                    if value and key == "optimize":
                        setOptimize()
        else:
            warnMsg = "没有可用于'%s'技术的注入数据" % enumValueToNameLookup(PAYLOAD.TECHNIQUE, technique)
            logger.warn(warnMsg)

    except SqlmapDataException:
        errMsg = u"在旧会话文件中丢失数据"
        errMsg += u"请使用'--flush-session'来处理这个错误"
        raise SqlmapNoneDataException(errMsg)

def arrayizeValue(value):
    """
    如果列表不是列表或元组本身，则列出一个值

    >>> arrayizeValue(u'1')
    [u'1']
    """

    if not isListLike(value):
        value = [value]

    return value

def unArrayizeValue(value):
    """
    如果它是一个列表或元组本身，使一个值可以迭代

    >>> unArrayizeValue([u'1'])
    u'1'
    """

    if isListLike(value):
        if not value:
            value = None
        elif len(value) == 1 and not isListLike(value[0]):
            value = value[0]
        else:
            _ = filter(lambda _: _ is not None, (_ for _ in flattenValue(value)))
            value = _[0] if len(_) > 0 else None

    return value

def flattenValue(value):
    """
    返回表示给定值的平面表示的迭代器

    >>> [_ for _ in flattenValue([[u'1'], [[u'2'], u'3']])]
    [u'1', u'2', u'3']
    """

    for i in iter(value):
        if isListLike(i):
            for j in flattenValue(i):
                yield j
        else:
            yield i

def isListLike(value):
    """
    如果给定的值是类似列表的实例，则返回True

    >>> isListLike([1, 2, 3])
    True
    >>> isListLike(u'2')
    False
    """

    return isinstance(value, (list, tuple, set, BigArray))

def getSortedInjectionTests():
    """
    通过最终检测到的DBMS从错误消息中返回优先级测试列表
    """

    retVal = copy.deepcopy(conf.tests)

    def priorityFunction(test):
        retVal = SORT_ORDER.FIRST

        if test.stype == PAYLOAD.TECHNIQUE.UNION:
            retVal = SORT_ORDER.LAST

        elif 'details' in test and 'dbms' in test.details:
            if intersect(test.details.dbms, Backend.getIdentifiedDbms()):
                retVal = SORT_ORDER.SECOND
            else:
                retVal = SORT_ORDER.THIRD

        return retVal

    if Backend.getIdentifiedDbms():
        retVal = sorted(retVal, key=priorityFunction)

    return retVal

def filterListValue(value, regex):
    """
    返回列表，其中包含满足给定正则表达式的部分项

    >>> filterListValue(['users', 'admins', 'logs'], r'(users|admins)')
    ['users', 'admins']
    """

    if isinstance(value, list) and regex:
        retVal = filter(lambda _: re.search(regex, _, re.I), value)
    else:
        retVal = value

    return retVal

def showHttpErrorCodes():
    """
    显示到现在为止引发的所有 HTTP 错误代码
    """

    if kb.httpErrorCodes:
        warnMsg = u"运行期间检测到HTTP错误代码:\n"
        warnMsg += ", ".join("%d (%s) - %d times" % (code, httplib.responses[code] \
          if code in httplib.responses else '?', count) \
          for code, count in kb.httpErrorCodes.items())
        logger.warn(warnMsg)
        if any((str(_).startswith('4') or str(_).startswith('5')) and _ != httplib.INTERNAL_SERVER_ERROR and _ != kb.originalCode for _ in kb.httpErrorCodes.keys()):
            msg = u"当出现太多的4xx或5xx HTTP错误代码可能意味着网站部署了防火墙(例如WAF)"
            logger.debug(msg)

def openFile(filename, mode='r', encoding=UNICODE_ENCODING, errors="replace", buffering=1):  

    # "buffering=1"表示行缓冲(参考: http://stackoverflow.com/a/3168436)
    """
    返回给定文件名的文件句柄
    """

    try:
        return codecs.open(filename, mode, encoding, errors, buffering)
    except IOError:
        errMsg = "文件名'%s'出现文件打开错误，" % filename
        errMsg += "请检查文件的%s权限，并确认它没有被其他进程锁定" % ("write" if \
          mode and ('w' in mode or 'a' in mode or '+' in mode) else "read")
        raise SqlmapSystemException(errMsg)

def decodeIntToUnicode(value):
    """
    将引用的整数值解码为unicode字符

    >>> decodeIntToUnicode(35)
    u'#'
    >>> decodeIntToUnicode(64)
    u'@'
    """
    retVal = value

    if isinstance(value, int):
        try:
            if value > 255:
                _ = "%x" % value
                if len(_) % 2 == 1:
                    _ = "0%s" % _
                raw = hexdecode(_)

                if Backend.isDbms(DBMS.MYSQL):
                    # https://github.com/sqlmapproject/sqlmap/issues/1531
                    retVal = getUnicode(raw, conf.charset or UNICODE_ENCODING)
                elif Backend.isDbms(DBMS.MSSQL):
                    retVal = getUnicode(raw, "UTF-16-BE")
                elif Backend.getIdentifiedDbms() in (DBMS.PGSQL, DBMS.ORACLE):
                    retVal = unichr(value)
                else:
                    retVal = getUnicode(raw, conf.charset)
            else:
                retVal = getUnicode(chr(value))
        except:
            retVal = INFERENCE_UNKNOWN_CHAR

    return retVal

def md5File(filename):
    """
    计算文件的MD5摘要
    参考: http://stackoverflow.com/a/3431838
    请注意，有时您将无法将整个文件装入内存。
    在这种情况下，您必须按顺序读取4096个字节的大小块，然后将它们提供给Md5函数
    """

    checkFile(filename)

    digest = hashlib.md5()
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(4096), ""):
            digest.update(chunk)

    return digest.hexdigest()



def checkIntegrity():
    #在未处理的异常期间检查代码文件的完整性
    
    if not paths:
        return

    logger.debug(u"运行代码完整性检查")

    retVal = False
    """
    for checksum, _ in (re.split(r'\s+', _) for _ in getFileItems(paths.CHECKSUM_MD5)):
        path = os.path.normpath(os.path.join(paths.SQLMAP_ROOT_PATH, _))
        if not os.path.isfile(path):
            logger.error(u"检测到缺少文件'%s'" % path)
            retVal = False
        elif md5File(path) != checksum:
            logger.error(u"检测到文件'%s'的校验和checksum错误" % path)
            retVal = False
    """
    return retVal
    
def unhandledExceptionMessage():
    """
    返回有关发生的未处理异常的详细消息
    """
    errMsg = u"未处理的异常发生在%s，" % VERSION_STRING
    errMsg += u"建议从官方GitHub仓库'%s'上重新运行最新的开发版本。\n" % GIT_PAGE
    errMsg += u"如果异常仍然存在，请在'%s'上创建一个新的issue，" % ISSUES_PAGE
    errMsg += u"并附上以下文本和任何其他必要的信息来重现错误。\n"
    errMsg += u"开发人员将尝试重现错误，并相应地进行修复并将结果反馈给您。\n"
    errMsg += u"sqlmap 版本: %s\n" % VERSION_STRING[VERSION_STRING.find('/') + 1:]
    errMsg += u"Python 版本: %s\n" % PYVERSION
    errMsg += u"操作系统: %s\n" % PLATFORM
    errMsg += u"命令行: %s\n" % re.sub(r".+?\bsqlmap.py\b", "sqlmap.py", getUnicode(" ".join(sys.argv), encoding=sys.stdin.encoding))
    errMsg += u"探测技术/攻击方法/注入手段: %s\n" % (enumValueToNameLookup(PAYLOAD.TECHNIQUE, kb.technique) if kb.get("technique") else ("DIRECT" if conf.get("direct") else None))
    errMsg += u"后端DBMS:"

    if Backend.getDbms() is not None:
        errMsg += " %s (采集指纹)" % Backend.getDbms()

    if Backend.getIdentifiedDbms() is not None and (Backend.getDbms() is None or Backend.getIdentifiedDbms() != Backend.getDbms()):
        errMsg += " %s (确定)" % Backend.getIdentifiedDbms()

    if not errMsg.endswith(')'):
        errMsg += " None"

    return errMsg

def createGithubIssue(errMsg, excMsg):


    #自动创建Github问题与未处理的异常信息


    issues = []
    try:
        issues = getFileItems(paths.GITHUB_HISTORY, unique=True)
    except:
        pass
    finally:
        issues = set(issues)

    _ = re.sub(r"'[^']+'", "''", excMsg)
    _ = re.sub(r"\s+line \d+", "", _)
    _ = re.sub(r'File ".+?/(\w+\.py)', "\g<1>", _)
    _ = re.sub(r".+\Z", "", _)
    key = hashlib.md5(_).hexdigest()[:8]

    if key in issues:
        return

    msg = u"\n您是否想要在Github官方存储库中自动创建一个未处理的异常信息新(匿名)问题? [y/N] "
    try:
        choice = readInput(msg, default='N', boolean=True)
    except:
        choice = None

    if choice:
        ex = None
        errMsg = errMsg[errMsg.find("\n"):]

        req = urllib2.Request(url="https://api.github.com/search/issues?q=%s" % urllib.quote("repo:sqlmapproject/sqlmap Unhandled exception (#%s)" % key))

        try:
            content = urllib2.urlopen(req).read()
            _ = json.loads(content)
            duplicate = _["total_count"] > 0
            closed = duplicate and _["items"][0]["state"] == "closed"
            if duplicate:
                warnMsg = "问题似乎已经上报解决了"
                if closed:
                    warnMsg += " 请从官方GitHub存储库更新到最新的开发版本'%s'" % GIT_PAGE
                logger.warn(warnMsg)
                return
        except:
            pass

        data = {"title": "Unhandled exception (#%s)" % key, "body": "```%s\n```\n```\n%s```" % (errMsg, excMsg)}
        req = urllib2.Request(url="https://api.github.com/repos/sqlmapproject/sqlmap/issues", data=json.dumps(data), headers={"Authorization": "token %s" % GITHUB_REPORT_OAUTH_TOKEN.decode("base64")})

        try:
            content = urllib2.urlopen(req).read()
        except Exception, ex:
            content = None

        issueUrl = re.search(r"https://github.com/sqlmapproject/sqlmap/issues/\d+", content or "")
        if issueUrl:
            infoMsg = "创建的Github问题可以在地址'%s'找到" % issueUrl.group(0)
            logger.info(infoMsg)

            try:
                with open(paths.GITHUB_HISTORY, "a+b") as f:
                    f.write("%s\n" % key)
            except:
                pass
        else:
            warnMsg = "在创建Github问题时出现错误"
            if ex:
                warnMsg += " ('%s')" % getSafeExString(ex)
            if "Unauthorized" in warnMsg:
                warnMsg += ",请更新至最新版本"
            logger.warn(warnMsg)

def maskSensitiveData(msg):
    """
    在提供的消息中屏蔽敏感数据
    """

    retVal = getUnicode(msg)

    for item in filter(None, map(lambda x: conf.get(x), SENSITIVE_OPTIONS)):
        regex = SENSITIVE_DATA_REGEX % re.sub("(\W)", r"\\\1", getUnicode(item))
        while extractRegexResult(regex, retVal):
            value = extractRegexResult(regex, retVal)
            retVal = retVal.replace(value, '*' * len(value))

    if not conf.get("hostname"):
        match = re.search(r"(?i)sqlmap.+(-u|--url)(\s+|=)([^ ]+)", retVal)
        if match:
            retVal = retVal.replace(match.group(3), '*' * len(match.group(3)))

    if getpass.getuser():
        retVal = re.sub(r"(?i)\b%s\b" % re.escape(getpass.getuser()), "*" * len(getpass.getuser()), retVal)

    return retVal

def listToStrValue(value):
    """
    将列表分解成单个字符串值

    >>> listToStrValue([1,2,3])
    '1, 2, 3'
    """

    if isinstance(value, (set, tuple)):
        value = list(value)

    if isinstance(value, list):
        retVal = value.__str__().lstrip('[').rstrip(']')
    else:
        retVal = value

    return retVal

def getExceptionFrameLocals():
    """
    从引发异常的框架返回带有局部变量内容的字典
    """

    retVal = {}

    if sys.exc_info():
        trace = sys.exc_info()[2]
        while trace.tb_next:
            trace = trace.tb_next
        retVal = trace.tb_frame.f_locals

    return retVal

def intersect(valueA, valueB, lowerCase=False):
    """
    返回数组化值的交集

    >>> intersect([1, 2, 3], set([1,3]))
    [1, 3]
    """

    retVal = []

    if valueA and valueB:
        valueA = arrayizeValue(valueA)
        valueB = arrayizeValue(valueB)

        if lowerCase:
            valueA = [val.lower() if isinstance(val, basestring) else val for val in valueA]
            valueB = [val.lower() if isinstance(val, basestring) else val for val in valueB]

        retVal = [val for val in valueA if val in valueB]

    return retVal

def removeReflectiveValues(content, payload, suppressWarning=False):
    """
    基于payload对给定content内容中的反射值进行中和
    就是对空格分号等号这些进行编码
    content:(search.php?q=1 AND 1=2 
    payload:<b>1%20AND%201%3D2</b>
    <b>__REFLECTED_VALUE__</b>
    suppressWarning:抑制警告
    """

    retVal = content

    try:
        if all([content, payload]) and isinstance(content, unicode) and kb.reflectiveMechanism and not kb.heuristicMode:
            def _(value):
                while 2 * REFLECTED_REPLACEMENT_REGEX in value:
                    value = value.replace(2 * REFLECTED_REPLACEMENT_REGEX, REFLECTED_REPLACEMENT_REGEX)
                return value

            payload = getUnicode(urldecode(payload.replace(PAYLOAD_DELIMITER, ''), convall=True))
            regex = _(filterStringValue(payload, r"[A-Za-z0-9]", REFLECTED_REPLACEMENT_REGEX.encode("string-escape")))

            if regex != payload:
                if all(part.lower() in content.lower() for part in filter(None, regex.split(REFLECTED_REPLACEMENT_REGEX))[1:]):  # 快速优化检查
                    parts = regex.split(REFLECTED_REPLACEMENT_REGEX)
                    retVal = content.replace(payload, REFLECTED_VALUE_MARKER)  # 虚拟方法

                    if len(parts) > REFLECTED_MAX_REGEX_PARTS:  # 防止占用大量CPU资源
                        regex = _("%s%s%s" % (REFLECTED_REPLACEMENT_REGEX.join(parts[:REFLECTED_MAX_REGEX_PARTS / 2]), REFLECTED_REPLACEMENT_REGEX, REFLECTED_REPLACEMENT_REGEX.join(parts[-REFLECTED_MAX_REGEX_PARTS / 2:])))

                    parts = filter(None, regex.split(REFLECTED_REPLACEMENT_REGEX))

                    if regex.startswith(REFLECTED_REPLACEMENT_REGEX):
                        regex = r"%s%s" % (REFLECTED_BORDER_REGEX, regex[len(REFLECTED_REPLACEMENT_REGEX):])
                    else:
                        regex = r"\b%s" % regex

                    if regex.endswith(REFLECTED_REPLACEMENT_REGEX):
                        regex = r"%s%s" % (regex[:-len(REFLECTED_REPLACEMENT_REGEX)], REFLECTED_BORDER_REGEX)
                    else:
                        regex = r"%s\b" % regex

                    _retVal = [retVal]
                    def _thread(regex):
                        try:
                            _retVal[0] = re.sub(r"(?i)%s" % regex, REFLECTED_VALUE_MARKER, _retVal[0])

                            if len(parts) > 2:
                                regex = REFLECTED_REPLACEMENT_REGEX.join(parts[1:])
                                _retVal[0] = re.sub(r"(?i)\b%s\b" % regex, REFLECTED_VALUE_MARKER, _retVal[0])
                        except KeyboardInterrupt:
                            raise
                        except:
                            pass

                    thread = threading.Thread(target=_thread, args=(regex,))
                    thread.daemon = True
                    thread.start()
                    thread.join(REFLECTED_REPLACEMENT_TIMEOUT)

                    if thread.isAlive():
                        kb.reflectiveMechanism = False
                        retVal = content
                        if not suppressWarning:
                            debugMsg = u"关闭反射去除机制(由于超时)"
                            logger.debug(debugMsg)
                    else:
                        retVal = _retVal[0]

                if retVal != content:
                    kb.reflectiveCounters[REFLECTIVE_COUNTER.HIT] += 1
                    if not suppressWarning:
                        warnMsg = u"反射值被发现并过滤掉"
                        singleTimeWarnMessage(warnMsg)
                    """
                    通过使用框架，你可以在同一个浏览器窗口中显示不止一个页面。
                    在下面的这个例子中，我们设置了一个两列的框架集。
                    第一列被设置为占据浏览器窗口的 25%。
                    第二列被设置为占据浏览器窗口的 75%。
                    HTML 文档 "frame_a.htm" 被置于第一个列中，
                    而 HTML 文档 "frame_b.htm" 被置于第二个列中：
                    <frameset cols="25%,75%">
                       <frame src="frame_a.htm">
                       <frame src="frame_b.htm">
                    </frameset>
                    """
                    if re.search(r"FRAME[^>]+src=[^>]*%s" % REFLECTED_VALUE_MARKER, retVal, re.I):
                        warnMsg = u"检测到框架FRAME标签中包含易受攻击的参数值，"
                        warnMsg += u"请确保单独测试，以防此页面上的攻击失败"
                        singleTimeWarnMessage(warnMsg)

                elif not kb.testMode and not kb.reflectiveCounters[REFLECTIVE_COUNTER.HIT]:
                    kb.reflectiveCounters[REFLECTIVE_COUNTER.MISS] += 1
                    # 如果REFLECTIVE_COUNTER.MISS > REFLECTIVE_MISS_THRESHOLD值为20 
                    # 关闭反射机制
                    if kb.reflectiveCounters[REFLECTIVE_COUNTER.MISS] > REFLECTIVE_MISS_THRESHOLD:
                        kb.reflectiveMechanism = False
                        if not suppressWarning:
                            debugMsg = u"关闭反射消除机制(为了优化目的)"
                            logger.debug(debugMsg)
    except MemoryError:
        kb.reflectiveMechanism = False
        if not suppressWarning:
            debugMsg = u"关闭反射去除机制(因为内存不足问题)"
            logger.debug(debugMsg)

    return retVal

def normalizeUnicode(value):
    """
    unicode字符串的ASCII规范化
    Reference: http://www.peterbe.com/plog/unicode-to-ascii

    >>> normalizeUnicode(u'\u0161u\u0107uraj')
    'sucuraj'
    """

    return unicodedata.normalize('NFKD', value).encode('ascii', 'ignore') if isinstance(value, unicode) else value

def safeSQLIdentificatorNaming(name, isTable=False):
    """
    返回一个安全的SQL标识名(内部数据格式)的表示
    Reference: http://stackoverflow.com/questions/954884/what-special-characters-are-allowed-in-t-sql-column-retVal
    """

    retVal = name

    if isinstance(name, basestring):
        retVal = getUnicode(name)
        _ = isTable and Backend.getIdentifiedDbms() in (DBMS.MSSQL, DBMS.SYBASE)

        if _:
            retVal = re.sub(r"(?i)\A%s\." % DEFAULT_MSSQL_SCHEMA, "", retVal)

        if retVal.upper() in kb.keywords or (retVal or " ")[0].isdigit() or not re.match(r"\A[A-Za-z0-9_@%s\$]+\Z" % ("." if _ else ""), retVal):  
        # MsSQL是唯一的DBMS，我们自动将模式添加到表名（点是正常的）
            if Backend.getIdentifiedDbms() in (DBMS.MYSQL, DBMS.ACCESS):
                retVal = "`%s`" % retVal.strip("`")
            elif Backend.getIdentifiedDbms() in (DBMS.PGSQL, DBMS.DB2, DBMS.SQLITE, DBMS.INFORMIX, DBMS.HSQLDB):
                retVal = "\"%s\"" % retVal.strip("\"")
            elif Backend.getIdentifiedDbms() in (DBMS.ORACLE,):
                retVal = "\"%s\"" % retVal.strip("\"").upper()
            elif Backend.getIdentifiedDbms() in (DBMS.MSSQL, DBMS.SYBASE) and ((retVal or " ")[0].isdigit() or not re.match(r"\A\w+\Z", retVal, re.U)):
                retVal = "[%s]" % retVal.strip("[]")

        if _ and DEFAULT_MSSQL_SCHEMA not in retVal and '.' not in re.sub(r"\[[^]]+\]", "", retVal):
            retVal = "%s.%s" % (DEFAULT_MSSQL_SCHEMA, retVal)

    return retVal

def unsafeSQLIdentificatorNaming(name):
    """
    从其安全的SQL表示中提取标识符的名称
    """

    retVal = name

    if isinstance(name, basestring):
        if Backend.getIdentifiedDbms() in (DBMS.MYSQL, DBMS.ACCESS):
            retVal = name.replace("`", "")
        elif Backend.getIdentifiedDbms() in (DBMS.PGSQL, DBMS.DB2):
            retVal = name.replace("\"", "")
        elif Backend.getIdentifiedDbms() in (DBMS.ORACLE,):
            retVal = name.replace("\"", "").upper()
        elif Backend.getIdentifiedDbms() in (DBMS.MSSQL,):
            retVal = name.replace("[", "").replace("]", "")

        if Backend.getIdentifiedDbms() in (DBMS.MSSQL, DBMS.SYBASE):
            prefix = "%s." % DEFAULT_MSSQL_SCHEMA
            if retVal.startswith(prefix):
                retVal = retVal[len(prefix):]

    return retVal

def isNoneValue(value):
    """
    返回值是否不可用(None或'')

    >>> isNoneValue(None)
    True
    >>> isNoneValue('None')
    True
    >>> isNoneValue('')
    True
    >>> isNoneValue([])
    True
    >>> isNoneValue([2])
    False
    """

    if isinstance(value, basestring):
        return value in ("None", "")
    elif isListLike(value):
        return all(isNoneValue(_) for _ in value)
    elif isinstance(value, dict):
        return not any(value)
    else:
        return value is None

def isNullValue(value):
    """
    返回值是否显式包含'NULL'值

    >>> isNullValue(u'NULL')
    True
    >>> isNullValue(u'foobar')
    False
    """

    return isinstance(value, basestring) and value.upper() == NULL

def expandMnemonics(mnemonics, parser, args):
    """
    扩展助记符选项
    """

    class MnemonicNode(object):
        def __init__(self):
            self.next = {}
            self.current = []

    head = MnemonicNode()
    pointer = None

    for group in parser.option_groups:
        for option in group.option_list:
            for opt in option._long_opts + option._short_opts:
                pointer = head

                for char in opt:
                    if char == "-":
                        continue
                    elif char not in pointer.next:
                        pointer.next[char] = MnemonicNode()

                    pointer = pointer.next[char]
                    pointer.current.append(option)

    for mnemonic in (mnemonics or "").split(','):
        found = None
        name = mnemonic.split('=')[0].replace("-", "").strip()
        value = mnemonic.split('=')[1] if len(mnemonic.split('=')) > 1 else None
        pointer = head

        for char in name:
            if char in pointer.next:
                pointer = pointer.next[char]
            else:
                pointer = None
                break

        if pointer in (None, head):
            errMsg = "助记符'%s'无法解析为任何参数名称" % name
            raise SqlmapSyntaxException(errMsg)

        elif len(pointer.current) > 1:
            options = {}

            for option in pointer.current:
                for opt in option._long_opts + option._short_opts:
                    opt = opt.strip('-')
                    if opt.startswith(name):
                        options[opt] = option

            if not options:
                warnMsg = "无法解析助记符'%s'" % name
                logger.warn(warnMsg)
            elif name in options:
                found = name
                debugMsg = "助记符'%s'解析为%s). " % (name, found)
                logger.debug(debugMsg)
            else:
                found = sorted(options.keys(), key=lambda x: len(x))[0]
                warnMsg = "检测到具有多义性(助记符'%s'可以解析为:%s)。" % (name, ", ".join("'%s'" % key for key in options.keys()))
                warnMsg += "解析为最短的那些('%s')" % found
                logger.warn(warnMsg)

            if found:
                found = options[found]
        else:
            found = pointer.current[0]
            debugMsg = "助记符'%s'解析为%s). " % (name, found)
            logger.debug(debugMsg)

        if found:
            try:
                value = found.convert_value(found, value)
            except OptionValueError:
                value = None

            if value is not None:
                setattr(args, found.dest, value)
            elif not found.type:  # boolean
                setattr(args, found.dest, True)
            else:
                errMsg = "助记符'%s'需要'%s'类型的值" % (name, found.type)
                raise SqlmapSyntaxException(errMsg)

def safeCSValue(value):
    """
    (csvDel) CSV delimited分隔符
    Reference: http://tools.ietf.org/html/rfc4180

    >>> safeCSValue(u'foo, bar')
    u'"foo, bar"'
    >>> safeCSValue(u'foobar')
    u'foobar'
    """

    retVal = value

    if retVal and isinstance(retVal, basestring):
        if not (retVal[0] == retVal[-1] == '"'):# 如果起始字符和结束字符不是双引号
            # "csvDel"在\sqlmap\lib\core\defaults.py中声明为逗号','
            if any(_ in retVal for _ in (conf.get("csvDel", defaults.csvDel), '"', '\n')):
                retVal = '"%s"' % retVal.replace('"', '""')# 单引号替换为双引号

    return retVal

def filterPairValues(values):
    """
    只返回与长度为2的类似列表的值

    >>> filterPairValues([[1, 2], [3], 1, [4, 5]])
    [[1, 2], [4, 5]]
    """

    retVal = []

    if not isNoneValue(values) and hasattr(values, '__iter__'):
        retVal = filter(lambda x: isinstance(x, (tuple, list, set)) and len(x) == 2, values)

    return retVal

def randomizeParameterValue(value):
    """
    根据字母数字字符的出现随机化参数值

    >>> random.seed(0)
    >>> randomizeParameterValue('foobar')
    'rnvnav'
    >>> randomizeParameterValue('17')
    '83'
    """

    retVal = value

    value = re.sub(r"%[0-9a-fA-F]{2}", "", value)

    for match in re.finditer('[A-Z]+', value):
        while True:
            original = match.group()
            candidate = randomStr(len(match.group())).upper()
            if original != candidate:
                break

        retVal = retVal.replace(original, candidate)

    for match in re.finditer('[a-z]+', value):
        while True:
            original = match.group()
            candidate = randomStr(len(match.group())).lower()
            if original != candidate:
                break

        retVal = retVal.replace(original, candidate)

    for match in re.finditer('[0-9]+', value):
        while True:
            original = match.group()
            candidate = str(randomInt(len(match.group())))
            if original != candidate:
                break

        retVal = retVal.replace(original, candidate)

    return retVal

@cachedmethod
def asciifyUrl(url, forceQuote=False):
    """
    Python的``urllib/urllib2``拒绝打开unicode编码的url.

    因此，要在urllib中打开一个IRI（即一个unicode地址），
    我们首先要将unicode地址转换为等效的ASCII地址
    基本上，需要做两件事情：

    域名需要IDNA编码，也称为Punycode。Python自2.3以来，支持idna和punycode编解码器。
    后者是基本算法，前者知道域语法，并确保每个标签（即子域）按照它们分开处理。

    路径和查询字符串组件需要使用UTF8引用，即需要使用百分比编码，每个八位字节被视为UTF8编码。
    Firefox也以相同的方式对用户名/密码部分进行编码。

    另见See also RFC 3987.

    Reference: http://blog.elsdoerfer.name/2008/12/12/opening-iris-in-python/

    >>> asciifyUrl(u'http://www.\u0161u\u0107uraj.com')
    u'http://www.xn--uuraj-gxa24d.com'
    """

    parts = urlparse.urlsplit(url)
    if not parts.scheme or not parts.netloc:
        # 显然不是一个url
        return url

    if all(char in string.printable for char in url):
        return url

    # idna-encode域
    try:
        hostname = parts.hostname.encode("idna")
    except LookupError:
        hostname = parts.hostname.encode(UNICODE_ENCODING)

    # UTF8 - 引用其他部分。 
    # 我们会单独检查每个部分，如果需要引用 - 这应该会捕获一些额外的用户错误，
    # 例如用户名中的变音符，即使路径*已经被引用。
    def quote(s, safe):
        s = s or ''
        # 触发非ASCII字符 - 另一种选择是：
        #     urllib.quote(s.replace('%', '')) != s.replace('%', '')
        # 这将触发所有 %-字符，例如 '＆'
        if s.encode("ascii", "replace") != s or forceQuote:
            return urllib.quote(s.encode(UNICODE_ENCODING), safe=safe)
        return s

    username = quote(parts.username, '')
    password = quote(parts.password, safe='')
    path = quote(parts.path, safe='/')
    query = quote(parts.query, safe="&=")

    # 将每个部分重新组合成一个完整的url
    netloc = hostname
    if username or password:
        netloc = '@' + netloc
        if password:
            netloc = ':' + password + netloc
        netloc = username + netloc

    try:
        port = parts.port
    except:
        port = None

    if port:
        netloc += ':' + str(port)

    return urlparse.urlunsplit([parts.scheme, netloc, path, query, parts.fragment])

def isAdminFromPrivileges(privileges):
    """
    检查权限以查看是否来自管理员用户
    """

    # 在 PostgreSQL 中, usesuper 特权意味着用户是 DBA
    retVal = (Backend.isDbms(DBMS.PGSQL) and "super" in privileges)

    # 在Oracle中，DBA特权意味着用户是DBA
    retVal |= (Backend.isDbms(DBMS.ORACLE) and "DBA" in privileges)

    # 在MySQL> = 5.0中，SUPER权限意味着用户是DBA
    retVal |= (Backend.isDbms(DBMS.MYSQL) and kb.data.has_information_schema and "SUPER" in privileges)

    # 在MySQL <5.0中，super_priv特权意味着用户是DBA
    retVal |= (Backend.isDbms(DBMS.MYSQL) and not kb.data.has_information_schema and "super_priv" in privileges)

    # 在Firebird中，没有特定的特权意味着用户是DBA
    retVal |= (Backend.isDbms(DBMS.FIREBIRD) and all(_ in privileges for _ in ("SELECT", "INSERT", "UPDATE", "DELETE", "REFERENCES", "EXECUTE")))

    return retVal

def findPageForms(content, url, raise_=False, addToTargets=False):
    """
    为可能的表单解析给定的页面内容
    """

    class _(StringIO):
        def __init__(self, content, url):
            StringIO.__init__(self, unicodeencode(content, kb.pageEncoding) if isinstance(content, unicode) else content)
            self._url = url
        def geturl(self):
            return self._url

    if not content:
        errMsg = "无法解析表单，因为当页面内容看起来是空的，"
        if raise_:
            raise SqlmapGenericException(errMsg)
        else:
            logger.debug(errMsg)

    forms = None
    retVal = set()
    response = _(content, url)

    try:
        forms = ParseResponse(response, backwards_compat=False)
    except (UnicodeError, ValueError):
        pass
    except ParseError:
        if "<html" in (content or ""):
            warnMsg = "在给定的URL('%s)中的HTML格式书写不规范，要过滤它" % url
            logger.warning(warnMsg)
            filtered = _("".join(re.findall(FORM_SEARCH_REGEX, content)), url)
            try:
                forms = ParseResponse(filtered, backwards_compat=False)
            except ParseError:
                errMsg = "没有成功"
                if raise_:
                    raise SqlmapGenericException(errMsg)
                else:
                    logger.debug(errMsg)

    if forms:
        for form in forms:
            try:
                for control in form.controls:
                    if hasattr(control, "items") and not any((control.disabled, control.readonly)):
                        # 如果控件具有可选择项，则选择第一个非禁用项。
                        for item in control.items:
                            if not item.disabled:
                                if not item.selected:
                                    item.selected = True
                                break

                if conf.crawlExclude and re.search(conf.crawlExclude, form.action or ""):
                    dbgMsg = "跳过'%s'" % form.action
                    logger.debug(dbgMsg)
                    continue

                request = form.click()
            except (ValueError, TypeError), ex:
                errMsg = "处理页面表单时出现问题('%s')" % getSafeExString(ex)
                if raise_:
                    raise SqlmapGenericException(errMsg)
                else:
                    logger.debug(errMsg)
            else:
                url = urldecode(request.get_full_url(), kb.pageEncoding)
                method = request.get_method()
                data = request.get_data() if request.has_data() else None
                data = urldecode(data, kb.pageEncoding, plusspace=False)

                if not data and method and method.upper() == HTTPMETHOD.POST:
                    debugMsg = "检测到空白数据的无效POST表单"
                    logger.debug(debugMsg)
                    continue

                # 检测我们是否在处理同一个目标主机
                _ = checkSameHost(response.geturl(), url)

                if conf.scope:
                    if not re.search(conf.scope, url, re.I):
                        continue
                elif not _:
                    continue
                else:
                    target = (url, method, data, conf.cookie, None)
                    retVal.add(target)
    else:
        errMsg = "在给定的目标网址中找不到任何表单"
        if raise_:
            raise SqlmapGenericException(errMsg)
        else:
            logger.debug(errMsg)

    if addToTargets and retVal:
        for target in retVal:
            kb.targets.add(target)

    return retVal

def checkSameHost(*urls):
    """
    如果所有提供的网址指向同一主机，则返回True

    >>> checkSameHost('http://www.target.com/page1.php?id=1', 'http://www.target.com/images/page2.php')
    True
    >>> checkSameHost('http://www.target.com/page1.php?id=1', 'http://www.target2.com/images/page2.php')
    False
    """

    if not urls:
        return None
    elif len(urls) == 1:
        return True
    else:
        return all(urlparse.urlparse(url or "").netloc.split(':')[0] == urlparse.urlparse(urls[0] or "").netloc.split(':')[0] for url in urls[1:])

def getHostHeader(url):
    """
    为给定的目标网址返回适当的主机头值

    >>> getHostHeader('http://www.target.com/vuln.php?id=1')
    'www.target.com'
    """

    retVal = url

    if url:
        retVal = urlparse.urlparse(url).netloc

        if re.search("http(s)?://\[.+\]", url, re.I):
            retVal = extractRegexResult("http(s)?://\[(?P<result>.+)\]", url)
        elif any(retVal.endswith(':%d' % _) for _ in (80, 443)):
            retVal = retVal.split(':')[0]

    return retVal

def checkDeprecatedOptions(args):
    """
    检查已弃用的选项
    """

    for _ in args:
        if _ in DEPRECATED_OPTIONS:
            errMsg = "开关/选项'%s'已被弃用" % _
            if DEPRECATED_OPTIONS[_]:
                errMsg += " (hint: %s)" % DEPRECATED_OPTIONS[_]
            raise SqlmapSyntaxException(errMsg)

def checkSystemEncoding():
    """
    检查有问题的编码
    """

    if sys.getdefaultencoding() == "cp720":
        try:
            codecs.lookup("cp720")
        except LookupError:
            errMsg = "有一个已知的Python问题(#1616979)与支持字符集'cp720'相关。请访问"
            errMsg += "'http://blog.oneortheother.info/tip/python-fix-cp720-encoding/index.html' "
            errMsg += "，并按照说明进行修复。"
            logger.critical(errMsg)

            warnMsg = "临时切换到字符集'cp1256'"
            logger.warn(warnMsg)

            reload(sys)
            sys.setdefaultencoding("cp1256")

def evaluateCode(code, variables=None):
    """
    以字符串形式给出给定的Python代码
    """

    try:
        exec(code, variables)
    except KeyboardInterrupt:
        raise
    except Exception, ex:
        errMsg = "在评估提供的代码时出现错误('%s') " % getSafeExString(ex)
        raise SqlmapGenericException(errMsg)

def serializeObject(object_):
    """
    序列化给定对象

    >>> serializeObject([1, 2, 3, ('a', 'b')])
    'gAJdcQEoSwFLAksDVQFhVQFihnECZS4='
    >>> serializeObject(None)
    'gAJOLg=='
    >>> serializeObject('foobar')
    'gAJVBmZvb2JhcnEBLg=='
    """

    return base64pickle(object_)

def unserializeObject(value):
    """
    从给定的序列化形式反序列化对象

    >>> unserializeObject(serializeObject([1, 2, 3])) == [1, 2, 3]
    True
    >>> unserializeObject('gAJVBmZvb2JhcnEBLg==')
    'foobar'
    """

    return base64unpickle(value) if value else None

def resetCounter(technique):
    """
    为给定的技术重置查询计数器
    """

    kb.counters[technique] = 0

def incrementCounter(technique):
    """
    给定技术的增量(递增)查询计数器
    """

    kb.counters[technique] = getCounter(technique) + 1

def getCounter(technique):
    """
    返回给定技术的查询计数器
    """

    return kb.counters.get(technique, 0)

def applyFunctionRecursively(value, function):
    """
    通过列表式结构递归运用函数

    >>> applyFunctionRecursively([1, 2, [3, 4, [19]], -9], lambda _: _ > 0)
    [True, True, [True, True, [True]], False]
    """

    if isListLike(value):
        retVal = [applyFunctionRecursively(_, function) for _ in value]
    else:
        retVal = function(value)

    return retVal

def decodeHexValue(value, raw=False):
    """
    解码十六进制值

    >>> decodeHexValue('3132332031')
    u'123 1'
    >>> decodeHexValue(['0x31', '0x32'])
    [u'1', u'2']
    """

    retVal = value

    def _(value):
        retVal = value
        if value and isinstance(value, basestring):
            if len(value) % 2 != 0:
                retVal = "%s?" % hexdecode(value[:-1]) if len(value) > 1 else value
                singleTimeWarnMessage("从预期的十六进制表单中解码'%s'时出现问题" % value)
            else:
                retVal = hexdecode(value)

            if not kb.binaryField and not raw:
                if Backend.isDbms(DBMS.MSSQL) and value.startswith("0x"):
                    try:
                        retVal = retVal.decode("utf-16-le")
                    except UnicodeDecodeError:
                        pass
                elif Backend.isDbms(DBMS.HSQLDB):
                    try:
                        retVal = retVal.decode("utf-16-be")
                    except UnicodeDecodeError:
                        pass
                if not isinstance(retVal, unicode):
                    retVal = getUnicode(retVal, "utf8")

        return retVal

    try:
        retVal = applyFunctionRecursively(value, _)
    except:
        singleTimeWarnMessage("从预期的十六进制形式解码'%s'出现问题" % value)

    return retVal

def extractExpectedValue(value, expected):
    """
    提取并返回给定类型的期望值

    >>> extractExpectedValue(['1'], EXPECTED.BOOL)
    True
    >>> extractExpectedValue('1', EXPECTED.INT)
    1
    """

    if expected:
        value = unArrayizeValue(value)

        if isNoneValue(value):
            value = None
        elif expected == EXPECTED.BOOL:
            if isinstance(value, int):
                value = bool(value)
            elif isinstance(value, basestring):
                value = value.strip().lower()
                if value in ("true", "false"):
                    value = value == "true"
                elif value in ("1", "-1"):
                    value = True
                elif value == "0":
                    value = False
                else:
                    value = None
        elif expected == EXPECTED.INT:
            if isinstance(value, basestring):
                value = int(value) if value.isdigit() else None

    return value

def hashDBWrite(key, value, serialize=False):
    """
    将会话数据写入HashDB的助手功能
    """

    _ = "%s%s%s" % (conf.url or "%s%s" % (conf.hostname, conf.port), key, HASHDB_MILESTONE_VALUE)
    conf.hashDB.write(_, value, serialize)

def hashDBRetrieve(key, unserialize=False, checkConf=False):
    """
    用于从HashDB还原会话数据的辅助功能
    """

    _ = "%s%s%s" % (conf.url or "%s%s" % (conf.hostname, conf.port), key, HASHDB_MILESTONE_VALUE)
    retVal = conf.hashDB.retrieve(_, unserialize) if kb.resumeValues and not (checkConf and any((conf.flushSession, conf.freshQueries))) else None

    if not kb.inferenceMode and not kb.fileReadMode and isinstance(retVal, basestring) and any(_ in retVal for _ in (PARTIAL_VALUE_MARKER, PARTIAL_HEX_VALUE_MARKER)):
        retVal = None
    return retVal

def resetCookieJar(cookieJar):
    """
    从给定的cookie jar中清除cookie

    """

    if not conf.loadCookies:
        cookieJar.clear()
    else:
        try:
            if not cookieJar.filename:
                infoMsg = u"从'%s'加载Cookie" % conf.loadCookies
                logger.info(infoMsg)

                content = readCachedFileContent(conf.loadCookies)
                lines = filter(None, (line.strip() for line in content.split("\n") if not line.startswith('#')))
                handle, filename = tempfile.mkstemp(prefix=MKSTEMP_PREFIX.COOKIE_JAR)
                os.close(handle)

                # Reference: http://www.hashbangcode.com/blog/netscape-http-cooke-file-parser-php-584.html
                with openFile(filename, "w+b") as f:
                    f.write("%s\n" % NETSCAPE_FORMAT_HEADER_COOKIES)
                    for line in lines:
                        _ = line.split("\t")
                        if len(_) == 7:
                            _[4] = FORCE_COOKIE_EXPIRATION_TIME
                            f.write("\n%s" % "\t".join(_))

                cookieJar.filename = filename

            cookieJar.load(cookieJar.filename, ignore_expires=True)

            for cookie in cookieJar:
                if cookie.expires < time.time():
                    warnMsg = u"Cookie( %s )已过期" % cookie
                    singleTimeWarnMessage(warnMsg)

            cookieJar.clear_expired_cookies()

            if not cookieJar._cookies:
                errMsg = u"找不到有效的Cookie"
                raise SqlmapGenericException(errMsg)

        except cookielib.LoadError, msg:
            errMsg = u"加载Cookie文件时出现问题('%s')" % re.sub(r"(cookies) file '[^']+'", "\g<1>", str(msg))
            raise SqlmapGenericException(errMsg)

def decloakToTemp(filename):
    """
    将给定文件的内容解包到具有相似名称和扩展名的临时文件
    """

    content = decloak(filename)

    _ = utf8encode(os.path.split(filename[:-1])[-1])

    prefix, suffix = os.path.splitext(_)
    prefix = prefix.split(os.extsep)[0]

    handle, filename = tempfile.mkstemp(prefix=prefix, suffix=suffix)
    os.close(handle)

    with open(filename, "w+b") as f:
        f.write(content)

    return filename

def prioritySortColumns(columns):
    """
    按照升序排列给定的列名称，而包含字符串'id'的列名首先排列

    >>> prioritySortColumns(['password', 'userid', 'name'])
    ['userid', 'name', 'password']
    """

    _ = lambda x: x and "id" in x.lower()
    return sorted(sorted(columns, key=len), lambda x, y: -1 if _(x) and not _(y) else 1 if not _(x) and _(y) else 0)

def getRequestHeader(request, name):
    """
    解决一个问题:urllib2请求头大小写敏感

    Reference: http://bugs.python.org/issue2275
    使urllib.request.Request.has_header()等不区分大小写
    """

    retVal = None

    if request and name:
        _ = name.upper()
        retVal = max([value if _ == key.upper() else None for key, value in request.header_items()])

    return retVal

def isNumber(value):
    """
    如果给定的值是一个(类似)数字对象，则返回True

    >>> isNumber(1)
    True
    >>> isNumber('0')
    True
    >>> isNumber('foobar')
    False
    """

    try:
        float(value)
    except:
        return False
    else:
        return True

def zeroDepthSearch(expression, value):
    """
    在0深度级别的括号内搜索值的匹配项
    """

    retVal = []

    depth = 0
    for index in xrange(len(expression)):
        if expression[index] == '(':
            depth += 1
        elif expression[index] == ')':
            depth -= 1
        elif depth == 0 and expression[index:index + len(value)] == value:
            retVal.append(index)

    return retVal

def splitFields(fields, delimiter=','):
    """
    返回由分隔符分割的（0-深度）字段的列表

    >>> splitFields('foo, bar, max(foo, bar)')
    ['foo', 'bar', 'max(foo,bar)']
    """

    fields = fields.replace("%s " % delimiter, delimiter)
    commas = [-1, len(fields)]
    commas.extend(zeroDepthSearch(fields, ','))
    commas = sorted(commas)

    return [fields[x + 1:y] for (x, y) in zip(commas, commas[1:])]

def pollProcess(process, suppress_errors=False):
    """
    检查过程状态（打印，如果仍在运行）
    """

    while True:
        dataToStdout(".")
        time.sleep(1)

        returncode = process.poll()

        if returncode is not None:
            if not suppress_errors:
                if returncode == 0:
                    dataToStdout(" 结束\n")
                elif returncode < 0:
                    dataToStdout(" 过程由信号%d终止\n" % returncode)
                elif returncode > 0:
                    dataToStdout(" 意外退出, 返回代码%d\n" % returncode)

            break

def getSafeExString(ex, encoding=None):
    """
    将捕获的异常作为一个字符串形式输出
    (注意：要避免的错误: 1) 
    1. "%s" % Exception(u'\u0161') 
    2. "%s" % str(Exception(u'\u0161'))

    >>> getSafeExString(Exception('foobar'))
    u'foobar'
    """

    retVal = ex

    if getattr(ex, "message", None):
        retVal = ex.message
    elif getattr(ex, "msg", None):
        retVal = ex.msg

    return getUnicode(retVal or "", encoding=encoding).strip()
