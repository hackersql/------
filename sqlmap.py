#!/usr/bin/env python
#coding=utf-8

"""
Copyright (c) 2006-2017 sqlmap developers (http://sqlmap.org/)
See the file 'doc/COPYING' for copying permission
"""

import sys

sys.dont_write_bytecode = True

try:
    __import__("lib.utils.versioncheck")  # this has to be the first non-standard import
except ImportError:
    exit(u"[!] 检测到错误的安装(缺少模块)访问'https://github.com/sqlmapproject/sqlmap/#installation' 了解更多详细信息")

import bdb
import distutils
import glob
import inspect
import json
import logging
import os
import re
import shutil
import sys
import thread
import threading
import time
import traceback
import warnings

warnings.filterwarnings(action="ignore", message=".*was already imported", category=UserWarning)
warnings.filterwarnings(action="ignore", category=DeprecationWarning)

from lib.core.data import logger

try:
    from lib.controller.controller import start
    from lib.core.common import banner
    from lib.core.common import checkIntegrity
    from lib.core.common import createGithubIssue
    from lib.core.common import dataToStdout
    from lib.core.common import getSafeExString
    from lib.core.common import getUnicode
    from lib.core.common import maskSensitiveData
    from lib.core.common import openFile
    from lib.core.common import setPaths
    from lib.core.common import weAreFrozen
    from lib.core.data import cmdLineOptions
    from lib.core.data import conf
    from lib.core.data import kb
    from lib.core.common import unhandledExceptionMessage
    from lib.core.common import MKSTEMP_PREFIX
    from lib.core.exception import SqlmapBaseException
    from lib.core.exception import SqlmapShellQuitException
    from lib.core.exception import SqlmapSilentQuitException
    from lib.core.exception import SqlmapUserQuitException
    from lib.core.option import initOptions
    from lib.core.option import init
    from lib.core.profiling import profile
    from lib.core.settings import GIT_PAGE
    from lib.core.settings import IS_WIN
    from lib.core.settings import LEGAL_DISCLAIMER
    from lib.core.settings import THREAD_FINALIZATION_TIMEOUT
    from lib.core.settings import UNICODE_ENCODING
    from lib.core.settings import VERSION
    from lib.core.testing import smokeTest
    from lib.core.testing import liveTest
    from lib.parse.cmdline import cmdLineParser
#如果try语句没有发生任何错误，忽略except子句，try子句执行后结束。
except KeyboardInterrupt:   #键盘中断
    errMsg = u"用户中止"
    logger.error(errMsg)
#如果在执行try语句的过程中发生了异常，那么try子句余下的部分将被忽略。如果异常的类型和except 之后的名称相符，那么对应的except子句将被执行。最后执行 try 语句之后的代码。
    raise SystemExit #raise 语句抛出一个指定的异常

def modulePath():
    """
    返回sqlmap.py程序的路径
    首先判断weAreFrozen()是否为真
    如果weAreFrozen()为真说明sqlmap被py2exe打包成了exe可执行程序
    sys.executable返回Python可执行文件路径
    否则就是当前文件名也就是sqlmap.py
    """

    try:
        _ = sys.executable if weAreFrozen() else __file__ # 'D:/Python27/sqlmap/sqlmap.py'
    except NameError:
        _ = inspect.getsourcefile(modulePath)

    return getUnicode(os.path.dirname(os.path.realpath(_)), encoding=sys.getfilesystemencoding() or UNICODE_ENCODING)

def checkEnvironment():
    try:
        os.path.isdir(modulePath())
    except UnicodeEncodeError:
        errMsg = u"您的系统没有正确处理非ASCII路径 "
        errMsg += u"请将sqlmap的目录移动到另一个位置 "
        logger.critical(errMsg)
        raise SystemExit

    if distutils.version.LooseVersion(VERSION) < distutils.version.LooseVersion("1.0"):
        errMsg = u"您的运行时环境（例如PYTHONPATH）已损坏，"
        errMsg += u"请确保您没有运行较旧版本的sqlmap或者较新版本的运行时脚本"
        logger.critical(errMsg)
        raise SystemExit

    # Patch for pip (import) environment
    if "sqlmap.sqlmap" in sys.modules:
        for _ in ("cmdLineOptions", "conf", "kb"):
            globals()[_] = getattr(sys.modules["lib.core.data"], _)

        for _ in ("SqlmapBaseException", "SqlmapShellQuitException", "SqlmapSilentQuitException", "SqlmapUserQuitException"):
            globals()[_] = getattr(sys.modules["lib.core.exception"], _)


def main():
    """
    sqlmap程序入口
    """

    try:
        checkEnvironment()
        setPaths(modulePath())
        banner()

        # 存储原始命令行选项以备以后恢复
        cmdLineOptions.update(cmdLineParser().__dict__)
        initOptions(cmdLineOptions)

        if conf.get("api"):
            # heavy imports
            from lib.utils.api import StdDbOut
            from lib.utils.api import setRestAPILog

            # 覆盖系统标准输出和标准错误，以写入IPC数据库
            sys.stdout = StdDbOut(conf.taskid, messagetype="stdout")
            sys.stderr = StdDbOut(conf.taskid, messagetype="stderr")
            setRestAPILog()

        conf.showTime = True
        dataToStdout(u"[!] 好好学习%s\n\n" % LEGAL_DISCLAIMER, forceOutput=True)
        dataToStdout(u"[*] 开始时间 %s\n\n" % time.strftime("%X"), forceOutput=True)

        init()

        if conf.profile:
            profile()
        elif conf.smokeTest:
            smokeTest()
        elif conf.liveTest:
            liveTest()
        else:
            try:
                start()
            except thread.error as ex:
                if "can't start new thread" in getSafeExString(ex):
                    errMsg = u"无法启动新线程,请检查操作系统(linux上查看:ulimit -a)限制"
                    logger.critical(errMsg)
                    raise SystemExit
                else:
                    raise

    except SqlmapUserQuitException:
        errMsg = u"用户退出"
        try:
            logger.error(errMsg)
        except KeyboardInterrupt:
            pass

    except (SqlmapSilentQuitException, bdb.BdbQuit):
        pass

    except SqlmapShellQuitException:
        cmdLineOptions.sqlmapShell = False

    except SqlmapBaseException as ex:
        errMsg = getSafeExString(ex)
        try:
            logger.critical(errMsg)
        except KeyboardInterrupt:
            pass
        raise SystemExit

    except KeyboardInterrupt:
        print

        errMsg = u"用户中止"
        try:
            logger.error(errMsg)
        except KeyboardInterrupt:
            pass

    except EOFError:
        print
        errMsg = u"退出"

        try:
            logger.error(errMsg)
        except KeyboardInterrupt:
            pass

    except SystemExit:
        pass

    except:
        print
        errMsg = unhandledExceptionMessage()
        excMsg = traceback.format_exc()
        valid = checkIntegrity()

        try:
            if valid is False:
                errMsg = u"代码完整性检查失败(关闭自动问题创建)"
                errMsg += u"您应该从官方GitHub存储库中的%s检索最新的开发版本" % GIT_PAGE
                logger.critical(errMsg)
                print
                dataToStdout(excMsg)
                raise SystemExit

            elif "tamper/" in excMsg:
                logger.critical(errMsg)
                print
                dataToStdout(excMsg)
                raise SystemExit

            elif "MemoryError" in excMsg:
                errMsg = u"内存耗尽检测"
                logger.error(errMsg)
                raise SystemExit

            elif any(_ in excMsg for _ in ("No space left", "Disk quota exceeded")):
                errMsg = u"输出设备上没有空间"
                logger.error(errMsg)
                raise SystemExit

            elif all(_ in excMsg for _ in ("No such file", "_'", "self.get_prog_name()")):
                errMsg = u"检测到损坏的安装('%s'). " % excMsg.strip().split('\n')[-1]
                errMsg += u"您应该从官方GitHub存储库中的'%s'检索最新的开发版本" % GIT_PAGE
                logger.error(errMsg)
                raise SystemExit

            elif "Read-only file system" in excMsg:
                errMsg = u"输出设备以只读方式挂载"
                logger.error(errMsg)
                raise SystemExit

            elif "OperationalError: disk I/O error" in excMsg:
                errMsg = u"输出设备上的I/O错误"
                logger.error(errMsg)
                raise SystemExit

            elif "_mkstemp_inner" in excMsg:
                errMsg = u"访问临时文件时出现问题"
                logger.error(errMsg)
                raise SystemExit

            elif "can't start new thread" in excMsg:
                errMsg = u"创建新线程实例时出现问题,"
                errMsg += u"请确保您没有运行太多进程"
                if not IS_WIN:
                    errMsg += u"(或增加'ulimit -u'值)"
                logger.error(errMsg)
                raise SystemExit
            # False Positive“误报” False Negative“漏报”
            elif "'DictObject' object has no attribute '" in excMsg and all(_ in errMsg for _ in ("(fingerprinted)", "(identified)")):
                errMsg = u"在枚举中有一个问题。由于误报的可能性很大，"
                errMsg += u"建议您重新运行'--flush-session'"
                logger.error(errMsg)
                raise SystemExit

            elif all(_ in excMsg for _ in ("pymysql", "configparser")):
                errMsg = "检测到pymsql初始化错误（依赖Python3）"
                logger.error(errMsg)
                raise SystemExit

            elif "bad marshal data (unknown type code)" in excMsg:
                match = re.search(r"\s*(.+)\s+ValueError", excMsg)
                errMsg = "您的一个.pyc文件已损坏%s" % (" ('%s')" % match.group(1) if match else "")
                errMsg += "请删除系统上的.pyc文件以解决问题"
                logger.error(errMsg)
                raise SystemExit

            elif "valueStack.pop" in excMsg and kb.get("dumpKeyboardInterrupt"):
                raise SystemExit

            elif any(_ in excMsg for _ in ("Broken pipe",)):
                raise SystemExit

            for match in re.finditer(r'File "(.+?)", line', excMsg):
                file_ = match.group(1)
                file_ = os.path.relpath(file_, os.path.dirname(__file__))
                file_ = file_.replace("\\", '/')
                file_ = re.sub(r"\.\./", '/', file_).lstrip('/')
                excMsg = excMsg.replace(match.group(1), file_)

            errMsg = maskSensitiveData(errMsg)
            excMsg = maskSensitiveData(excMsg)

            if conf.get("api") or not valid:
                logger.critical("%s\n%s" % (errMsg, excMsg))
            else:
                logger.critical(errMsg)
                kb.stickyLevel = logging.CRITICAL
                dataToStdout(excMsg)
                createGithubIssue(errMsg, excMsg)

        except KeyboardInterrupt:
            pass

    finally:
        kb.threadContinue = False

        if conf.get("showTime"):
            dataToStdout(u"\n[*] 结束时间 %s\n\n" % time.strftime("%X"), forceOutput=True)

        kb.threadException = True

        if kb.get("tempDir"):
            for prefix in (MKSTEMP_PREFIX.IPC, MKSTEMP_PREFIX.TESTING, MKSTEMP_PREFIX.COOKIE_JAR, MKSTEMP_PREFIX.BIG_ARRAY):
                for filepath in glob.glob(os.path.join(kb.tempDir, "%s*" % prefix)):
                    try:
                        os.remove(filepath)
                    except OSError:
                        pass
            if not filter(None, (filepath for filepath in glob.glob(os.path.join(kb.tempDir, '*')) if not any(filepath.endswith(_) for _ in ('.lock', '.exe', '_')))):
                shutil.rmtree(kb.tempDir, ignore_errors=True)

        if conf.get("hashDB"):
            try:
                conf.hashDB.flush(True)
            except KeyboardInterrupt:
                pass

        if conf.get("harFile"):
            with openFile(conf.harFile, "w+b") as f:
                json.dump(conf.httpCollector.obtain(), fp=f, indent=4, separators=(',', ': '))

        if cmdLineOptions.get("sqlmapShell"):
            cmdLineOptions.clear()
            conf.clear()
            kb.clear()
            main()

        if conf.get("api"):
            try:
                conf.databaseCursor.disconnect()
            except KeyboardInterrupt:
                pass

        if conf.get("dumper"):
            conf.dumper.flush()

        # 线程完成的短暂延迟
        try:
            _ = time.time()
            while threading.activeCount() > 1 and (time.time() - _) > THREAD_FINALIZATION_TIMEOUT:
                time.sleep(0.01)
        except KeyboardInterrupt:
            pass
        finally:
            # Reference: http://stackoverflow.com/questions/1635080/terminate-a-multi-thread-python-program
            if threading.activeCount() > 1:
                os._exit(0)

if __name__ == "__main__":
    main()
