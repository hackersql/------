#!/usr/bin/env python
#coding=utf-8
"""
Copyright (c) 2006-2017 sqlmap developers (http://sqlmap.org/)
See the file 'doc/COPYING' for copying permission
"""

import difflib
import random
import threading
import time
import traceback

from lib.core.data import conf
from lib.core.data import kb
from lib.core.data import logger
from lib.core.datatype import AttribDict
from lib.core.enums import PAYLOAD
from lib.core.exception import SqlmapConnectionException
from lib.core.exception import SqlmapThreadException
from lib.core.exception import SqlmapUserQuitException
from lib.core.exception import SqlmapValueException
from lib.core.settings import MAX_NUMBER_OF_THREADS
from lib.core.settings import PYVERSION

shared = AttribDict()

class _ThreadData(threading.local):
    """
    代表独立的线程数据
    """

    def __init__(self):
        self.reset()

    def reset(self):
        """
        重新设置线程数据模型
        """

        self.disableStdOut = False
        self.hashDBCursor = None
        self.inTransaction = False
        self.lastCode = None
        self.lastComparisonPage = None
        self.lastComparisonHeaders = None
        self.lastComparisonCode = None
        self.lastComparisonRatio = None
        self.lastErrorPage = None
        self.lastHTTPError = None
        self.lastRedirectMsg = None
        self.lastQueryDuration = 0
        self.lastPage = None
        self.lastRequestMsg = None
        self.lastRequestUID = 0
        self.lastRedirectURL = None
        self.random = random.WichmannHill()
        self.resumed = False
        self.retriesCount = 0
        self.seqMatcher = difflib.SequenceMatcher(None)
        self.shared = shared
        self.validationRun = 0
        self.valueStack = []

ThreadData = _ThreadData()

def getCurrentThreadUID():
    return hash(threading.currentThread())

def readInput(message, default=None, checkBatch=True, boolean=False):
    # 它将被lib.core.common的原始文件覆盖
    pass

def getCurrentThreadData():
    """
    返回当前线程本地数据
    """

    global ThreadData

    return ThreadData

def getCurrentThreadName():
    """
    返回当前的线程名
    """

    return threading.current_thread().getName()

def exceptionHandledFunction(threadFunction, silent=False):
    try:
        threadFunction()
    except KeyboardInterrupt:
        kb.threadContinue = False
        kb.threadException = True
        raise
    except Exception, ex:
        if not silent:
            logger.error("thread %s: %s" % (threading.currentThread().getName(), ex.message))

def setDaemon(thread):
    # Reference: http://stackoverflow.com/questions/190010/daemon-threads-explanation
    if PYVERSION >= "2.6":
        thread.daemon = True
    else:
        thread.setDaemon(True)

def runThreads(numThreads, threadFunction, cleanupFunction=None, forwardException=True, threadChoice=False, startThreadMsg=True):
    threads = []

    kb.multiThreadMode = True
    kb.threadContinue = True
    kb.threadException = False

    if threadChoice and numThreads == 1 and not (kb.injection.data and not any(_ not in (PAYLOAD.TECHNIQUE.TIME, PAYLOAD.TECHNIQUE.STACKED) for _ in kb.injection.data)):
        while True:
            message = u"请输入线程数? [输入%d (当前)]" % numThreads
            choice = readInput(message, default=str(numThreads))
            if choice:
                skipThreadCheck = False
                if choice.endswith('!'):
                    choice = choice[:-1]
                    skipThreadCheck = True
                if choice.isdigit():
                    if int(choice) > MAX_NUMBER_OF_THREADS and not skipThreadCheck:
                        # 最大线程数(避免连接问题或DoS)
                        # MAX_NUMBER_OF_THREADS = 10
                        errMsg = u"最大使用线程数为%d，避免潜在的连接问题" % MAX_NUMBER_OF_THREADS
                        logger.critical(errMsg)
                    else:
                        conf.threads = numThreads = int(choice)
                        break

        if numThreads == 1:
            warnMsg = u"运行在单线程模式,这可能需要一段时间"
            logger.warn(warnMsg)

    try:
        if numThreads > 1:
            if startThreadMsg:
                infoMsg = u"启动%d个线程" % numThreads
                logger.info(infoMsg)
        else:
            threadFunction()
            return

        # 启动线程
        for numThread in xrange(numThreads):
            thread = threading.Thread(target=exceptionHandledFunction, name=str(numThread), args=[threadFunction])

            setDaemon(thread)

            try:
                thread.start()
            except Exception, ex:
                errMsg = u"启动新线程时发生错误('%s')" % ex.message
                logger.critical(errMsg)
                break

            threads.append(thread)

        # 等待他们完成
        alive = True
        while alive:
            alive = False
            for thread in threads:
                if thread.isAlive():
                    alive = True
                    time.sleep(0.1)

    except (KeyboardInterrupt, SqlmapUserQuitException), ex:
        print
        kb.threadContinue = False
        kb.threadException = True

        if numThreads > 1:
            logger.info(u"等待线程完成 %s" % (" (Ctrl + C 被按下)" if isinstance(ex, KeyboardInterrupt) else ""))
        try:
            while (threading.activeCount() > 1):
                pass

        except KeyboardInterrupt:
            raise SqlmapThreadException(u"用户中止(Ctrl + C 被多次按下)")

        if forwardException:
            raise

    except (SqlmapConnectionException, SqlmapValueException), ex:
        print
        kb.threadException = True
        logger.error("thread %s: %s" % (threading.currentThread().getName(), ex.message))

    except:
        from lib.core.common import unhandledExceptionMessage

        print
        kb.threadException = True
        errMsg = unhandledExceptionMessage()
        logger.error("thread %s: %s" % (threading.currentThread().getName(), errMsg))
        traceback.print_exc()

    finally:
        kb.multiThreadMode = False
        kb.bruteMode = False
        kb.threadContinue = True
        kb.threadException = False

        for lock in kb.locks.values():
            if lock.locked():
                try:
                    lock.release()
                except:
                    pass

        if conf.get("hashDB"):
            conf.hashDB.flush(True)

        if cleanupFunction:
            cleanupFunction()
