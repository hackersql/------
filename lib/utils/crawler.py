#!/usr/bin/env python
#coding=utf-8

"""
Copyright (c) 2006-2017 sqlmap developers (http://sqlmap.org/)
See the file 'doc/COPYING' for copying permission
"""

import httplib
import os
import re
import urlparse
import tempfile
import time

from lib.core.common import checkSameHost
from lib.core.common import clearConsoleLine
from lib.core.common import dataToStdout
from lib.core.common import findPageForms
from lib.core.common import getSafeExString
from lib.core.common import openFile
from lib.core.common import readInput
from lib.core.common import safeCSValue
from lib.core.common import urldecode
from lib.core.data import conf
from lib.core.data import kb
from lib.core.data import logger
from lib.core.enums import MKSTEMP_PREFIX
from lib.core.exception import SqlmapConnectionException
from lib.core.exception import SqlmapSyntaxException
from lib.core.settings import CRAWL_EXCLUDE_EXTENSIONS
from lib.core.threads import getCurrentThreadData
from lib.core.threads import runThreads
from lib.parse.sitemap import parseSitemap
from lib.request.connect import Connect as Request
from thirdparty.beautifulsoup.beautifulsoup import BeautifulSoup
from thirdparty.oset.pyoset import oset

def crawl(target):
    try:
        visited = set()
        threadData = getCurrentThreadData()
        threadData.shared.value = oset()

        def crawlThread():
            threadData = getCurrentThreadData()

            while kb.threadContinue:
                with kb.locks.limit:
                    if threadData.shared.unprocessed:
                        current = threadData.shared.unprocessed.pop()
                        if current in visited:
                            continue
                        elif conf.crawlExclude and re.search(conf.crawlExclude, current):
                            dbgMsg = "skipping '%s'" % current
                            logger.debug(dbgMsg)
                            continue
                        else:
                            visited.add(current)
                    else:
                        break

                content = None
                try:
                    if current:
                        content = Request.getPage(url=current, crawling=True, raise404=False)[0]
                except SqlmapConnectionException, ex:
                    errMsg = u"检测到连接异常(%s)，" % getSafeExString(ex)
                    errMsg += u"跳过网址 '%s'" % current
                    logger.critical(errMsg)
                except SqlmapSyntaxException:
                    errMsg = u"检测到无效的网址，跳过 '%s'" % current
                    logger.critical(errMsg)
                except httplib.InvalidURL, ex:
                    errMsg = u"检测到无效的网址(%s) " % getSafeExString(ex)
                    errMsg += u"跳过网址 '%s'" % current
                    logger.critical(errMsg)

                if not kb.threadContinue:
                    break

                if isinstance(content, unicode):
                    try:
                        match = re.search(r"(?si)<html[^>]*>(.+)</html>", content)
                        if match:
                            content = "<html>%s</html>" % match.group(1)

                        soup = BeautifulSoup(content)
                        tags = soup('a')

                        if not tags:
                            tags = re.finditer(r'(?i)<a[^>]+href="(?P<href>[^>"]+)"', content)

                        for tag in tags:
                            href = tag.get("href") if hasattr(tag, "get") else tag.group("href")

                            if href:
                                if threadData.lastRedirectURL and threadData.lastRedirectURL[0] == threadData.lastRequestUID:
                                    current = threadData.lastRedirectURL[1]
                                url = urlparse.urljoin(current, href)

                                # 通过标记来判断我们是否在处理同一个目标主机
                                _ = checkSameHost(url, target)

                                if conf.scope:
                                    if not re.search(conf.scope, url, re.I):
                                        continue
                                elif not _:
                                    continue

                                if url.split('.')[-1].lower() not in CRAWL_EXCLUDE_EXTENSIONS:
                                    with kb.locks.value:
                                        threadData.shared.deeper.add(url)
                                        if re.search(r"(.*?)\?(.+)", url):
                                            threadData.shared.value.add(url)
                    except UnicodeEncodeError:  # 用于非HTML文件
                        pass
                    except ValueError:          # 用于非有效链接
                        pass
                    finally:
                        if conf.forms:
                            findPageForms(content, current, False, True)

                if conf.verbose in (1, 2):
                    threadData.shared.count += 1
                    status = u'访问了%d/%d个链接(%d%%)' % (threadData.shared.count, threadData.shared.length, round(100.0 * threadData.shared.count / threadData.shared.length))
                    dataToStdout("\r[%s] [INFO] %s" % (time.strftime("%X"), status), True)

        threadData.shared.deeper = set()
        threadData.shared.unprocessed = set([target])

        if not conf.sitemapUrl:
            message = u"你想检查网站是否存在站点地图sitemap(.xml)文件吗? [y/N] "

            if readInput(message, default='N', boolean=True):
                found = True
                items = None
                url = urlparse.urljoin(target, "/sitemap.xml")
                try:
                    items = parseSitemap(url)
                except SqlmapConnectionException, ex:
                    if "page not found" in getSafeExString(ex):
                        found = False
                        logger.warn(u"'sitemap.xml'未找到")
                except:
                    pass
                finally:
                    if found:
                        if items:
                            for item in items:
                                if re.search(r"(.*?)\?(.+)", item):
                                    threadData.shared.value.add(item)
                            if conf.crawlDepth > 1:
                                threadData.shared.unprocessed.update(items)
                        logger.info("%s links found" % ("no" if not items else len(items)))

        infoMsg = u"开始抓取"
        if conf.bulkFile:
            infoMsg += u"目标网址'%s'" % target
        logger.info(infoMsg)

        for i in xrange(conf.crawlDepth):
            threadData.shared.count = 0
            threadData.shared.length = len(threadData.shared.unprocessed)
            numThreads = min(conf.threads, len(threadData.shared.unprocessed))

            if not conf.bulkFile:
                logger.info(u"搜索深度为%d的链接" % (i + 1))

            runThreads(numThreads, crawlThread, threadChoice=(i>0))
            clearConsoleLine(True)

            if threadData.shared.deeper:
                threadData.shared.unprocessed = set(threadData.shared.deeper)
            else:
                break

    except KeyboardInterrupt:
        warnMsg = u"用户在爬行期间中止,sqlmap将使用部分列表"
        logger.warn(warnMsg)

    finally:
        clearConsoleLine(True)

        if not threadData.shared.value:
            warnMsg = u"找不到可用的链接（使用GET参数）"
            logger.warn(warnMsg)
        else:
            for url in threadData.shared.value:
                kb.targets.add((urldecode(url, kb.pageEncoding), None, None, None, None))

        storeResultsToFile(kb.targets)

def storeResultsToFile(results):
    if not results:
        return

    if kb.storeCrawlingChoice is None:
        message = u"您是否希望将抓取结果存储到临时文件中，以便最终使用其他工具进一步处理 [y/N]"

        kb.storeCrawlingChoice = readInput(message, default='N', boolean=True)

    if kb.storeCrawlingChoice:
        handle, filename = tempfile.mkstemp(prefix=MKSTEMP_PREFIX.CRAWLER, suffix=".csv" if conf.forms else ".txt")
        os.close(handle)

        infoMsg = u"将抓取结果写入临时文件'%s' " % filename
        logger.info(infoMsg)

        with openFile(filename, "w+b") as f:
            if conf.forms:
                f.write("URL,POST\n")

            for url, _, data, _, _ in results:
                if conf.forms:
                    f.write("%s,%s\n" % (safeCSValue(url), safeCSValue(data or "")))
                else:
                    f.write("%s\n" % url)
