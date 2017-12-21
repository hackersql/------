#!/usr/bin/env python
#coding=utf-8

"""
Copyright (c) 2006-2017 sqlmap developers (http://sqlmap.org/)
See the file 'doc/COPYING' for copying permission
"""

import contextlib
import logging
import os
import re
import shlex
import socket
import sqlite3
import sys
import tempfile
import time
import urllib2

from lib.core.common import dataToStdout
from lib.core.common import getSafeExString
from lib.core.common import saveConfig
from lib.core.common import unArrayizeValue
from lib.core.convert import hexencode
from lib.core.convert import dejsonize
from lib.core.convert import jsonize
from lib.core.data import conf
from lib.core.data import kb
from lib.core.data import paths
from lib.core.data import logger
from lib.core.datatype import AttribDict
from lib.core.defaults import _defaults
from lib.core.enums import CONTENT_STATUS
from lib.core.enums import MKSTEMP_PREFIX
from lib.core.enums import PART_RUN_CONTENT_TYPES
from lib.core.exception import SqlmapConnectionException
from lib.core.log import LOGGER_HANDLER
from lib.core.optiondict import optDict
from lib.core.settings import RESTAPI_DEFAULT_ADAPTER
from lib.core.settings import IS_WIN
from lib.core.settings import RESTAPI_DEFAULT_ADDRESS
from lib.core.settings import RESTAPI_DEFAULT_PORT
from lib.core.subprocessng import Popen
from lib.parse.cmdline import cmdLineParser
from thirdparty.bottle.bottle import error as return_error
from thirdparty.bottle.bottle import get
from thirdparty.bottle.bottle import hook
from thirdparty.bottle.bottle import post
from thirdparty.bottle.bottle import request
from thirdparty.bottle.bottle import response
from thirdparty.bottle.bottle import run
from thirdparty.bottle.bottle import server_names


# 全局设置
class DataStore(object):
    admin_id = ""
    current_db = None
    tasks = dict()


# API对象
class Database(object):
    filepath = None

    def __init__(self, database=None):
        self.database = self.filepath if database is None else database
        self.connection = None
        self.cursor = None

    def connect(self, who="server"):
        self.connection = sqlite3.connect(self.database, timeout=3, isolation_level=None, check_same_thread=False)
        self.cursor = self.connection.cursor()
        logger.debug(u"REST-JSON API %s 连接到IPC数据库" % who)

    def disconnect(self):
        if self.cursor:
            self.cursor.close()

        if self.connection:
            self.connection.close()

    def commit(self):
        self.connection.commit()

    def execute(self, statement, arguments=None):
        while True:
            try:
                if arguments:
                    self.cursor.execute(statement, arguments)
                else:
                    self.cursor.execute(statement)
            except sqlite3.OperationalError, ex:
                if not "locked" in getSafeExString(ex):
                    raise
            else:
                break

        if statement.lstrip().upper().startswith("SELECT"):
            return self.cursor.fetchall()

    def init(self):
        self.execute("CREATE TABLE logs("
                  "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                  "taskid INTEGER, time TEXT, "
                  "level TEXT, message TEXT"
                  ")")

        self.execute("CREATE TABLE data("
                  "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                  "taskid INTEGER, status INTEGER, "
                  "content_type INTEGER, value TEXT"
                  ")")

        self.execute("CREATE TABLE errors("
                    "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                    "taskid INTEGER, error TEXT"
                    ")")


class Task(object):
    def __init__(self, taskid, remote_addr):
        self.remote_addr = remote_addr
        self.process = None
        self.output_directory = None
        self.options = None
        self._original_options = None
        self.initialize_options(taskid)

    def initialize_options(self, taskid):
        datatype = {"boolean": False, "string": None, "integer": None, "float": None}
        self.options = AttribDict()

        for _ in optDict:
            for name, type_ in optDict[_].items():
                type_ = unArrayizeValue(type_)
                self.options[name] = _defaults.get(name, datatype[type_])

        # 让sqlmap引擎知道它被API调用，IPC数据库的任务ID和文件路径
        self.options.api = True
        self.options.taskid = taskid
        self.options.database = Database.filepath

        # 执行批处理模式并禁用着色和ETA
        self.options.batch = True
        self.options.disableColoring = True
        self.options.eta = False

        self._original_options = AttribDict(self.options)

    def set_option(self, option, value):
        self.options[option] = value

    def get_option(self, option):
        return self.options[option]

    def get_options(self):
        return self.options

    def reset_options(self):
        self.options = AttribDict(self._original_options)

    def engine_start(self):
        handle, configFile = tempfile.mkstemp(prefix=MKSTEMP_PREFIX.CONFIG, text=True)
        os.close(handle)
        saveConfig(self.options, configFile)

        if os.path.exists("sqlmap.py"):
            self.process = Popen(["python", "sqlmap.py", "--api", "-c", configFile], shell=False, close_fds=not IS_WIN)
        elif os.path.exists(os.path.join(os.getcwd(), "sqlmap.py")):
            self.process = Popen(["python", "sqlmap.py", "--api", "-c", configFile], shell=False, cwd=os.getcwd(), close_fds=not IS_WIN)
        else:
            self.process = Popen(["sqlmap", "--api", "-c", configFile], shell=False, close_fds=not IS_WIN)

    def engine_stop(self):
        if self.process:
            self.process.terminate()
            return self.process.wait()
        else:
            return None

    def engine_process(self):
        return self.process

    def engine_kill(self):
        if self.process:
            try:
                self.process.kill()
                return self.process.wait()
            except:
                pass
        return None

    def engine_get_id(self):
        if self.process:
            return self.process.pid
        else:
            return None

    def engine_get_returncode(self):
        if self.process:
            self.process.poll()
            return self.process.returncode
        else:
            return None

    def engine_has_terminated(self):
        return isinstance(self.engine_get_returncode(), int)


# sqlmap引擎的Wrapper函数
class StdDbOut(object):
    def __init__(self, taskid, messagetype="stdout"):
        # 覆盖系统标准输出和标准错误，以写入IPC数据库
        self.messagetype = messagetype
        self.taskid = taskid

        if self.messagetype == "stdout":
            sys.stdout = self
        else:
            sys.stderr = self

    def write(self, value, status=CONTENT_STATUS.IN_PROGRESS, content_type=None):
        if self.messagetype == "stdout":
            if content_type is None:
                if kb.partRun is not None:
                    content_type = PART_RUN_CONTENT_TYPES.get(kb.partRun)
                else:
                    # 忽略所有不相关的消息
                    return

            output = conf.databaseCursor.execute("SELECT id, status, value FROM data WHERE taskid = ? AND content_type = ?", (self.taskid, content_type))

            # 如果得到完整的输出，则从IPC数据库中删除部分输出
            if status == CONTENT_STATUS.COMPLETE:
                if len(output) > 0:
                    for index in xrange(len(output)):
                        conf.databaseCursor.execute("DELETE FROM data WHERE id = ?", (output[index][0],))

                conf.databaseCursor.execute("INSERT INTO data VALUES(NULL, ?, ?, ?, ?)", (self.taskid, status, content_type, jsonize(value)))
                if kb.partRun:
                    kb.partRun = None

            elif status == CONTENT_STATUS.IN_PROGRESS:
                if len(output) == 0:
                    conf.databaseCursor.execute("INSERT INTO data VALUES(NULL, ?, ?, ?, ?)", (self.taskid, status, content_type, jsonize(value)))
                else:
                    new_value = "%s%s" % (dejsonize(output[0][2]), value)
                    conf.databaseCursor.execute("UPDATE data SET value = ? WHERE id = ?", (jsonize(new_value), output[0][0]))
        else:
            conf.databaseCursor.execute("INSERT INTO errors VALUES(NULL, ?, ?)", (self.taskid, str(value) if value else ""))

    def flush(self):
        pass

    def close(self):
        pass

    def seek(self):
        pass

class LogRecorder(logging.StreamHandler):
    def emit(self, record):
        """
        将发送的事件记录到IPC数据库以进行与父进程的异步I/O通信
        """
        conf.databaseCursor.execute("INSERT INTO logs VALUES(NULL, ?, ?, ?, ?)", (conf.taskid, time.strftime("%X"), record.levelname, record.msg % record.args if record.args else record.msg))

def setRestAPILog():
    if conf.api:
        try:
            conf.databaseCursor = Database(conf.database)
            conf.databaseCursor.connect("client")
        except sqlite3.OperationalError, ex:
            raise SqlmapConnectionException, "%s ('%s')" % (ex, conf.database)

        # 设置将日志消息写入IPC数据库的日志处理程序
        logger.removeHandler(LOGGER_HANDLER)
        LOGGER_RECORDER = LogRecorder()
        logger.addHandler(LOGGER_RECORDER)


# Generic functions
def is_admin(taskid):
    return DataStore.admin_id == taskid


@hook("after_request")
def security_headers(json_header=True):
    """
    在所有HTTP响应中设置一些headers
    """
    response.headers["Server"] = "Server"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Pragma"] = "no-cache"
    response.headers["Cache-Control"] = "no-cache"
    response.headers["Expires"] = "0"
    if json_header:
        response.content_type = "application/json; charset=UTF-8"

##############################
#        HTTP状态码函数      #
##############################


@return_error(401)  # 拒绝访问
def error401(error=None):
    security_headers(False)
    return u"拒绝访问"


@return_error(404)  # 未找到页面
def error404(error=None):
    security_headers(False)
    return u"未找到页面"


@return_error(405)  # 方法不允许（例如通过GET请求POST方法时）
def error405(error=None):
    security_headers(False)
    return u"不允许的方法"


@return_error(500)  # 内部服务器错误
def error500(error=None):
    security_headers(False)
    return u"内部服务器错误"

#############################
#        任务管理功能       #
#############################


# Users' methods
@get("/task/new")
def task_new():
    """
    创建新的任务ID
    """
    taskid = hexencode(os.urandom(8))
    remote_addr = request.remote_addr

    DataStore.tasks[taskid] = Task(taskid, remote_addr)

    logger.debug(u"创建新任务: '%s'" % taskid)
    return jsonize({"success": True, "taskid": taskid})


@get("/task/<taskid>/delete")
def task_delete(taskid):
    """
    删除自己的任务ID
    """
    if taskid in DataStore.tasks:
        DataStore.tasks.pop(taskid)

        logger.debug(u"[%s] 删除任务" % taskid)
        return jsonize({"success": True})
    else:
        logger.warning(u"[%s] 提供给task_delete()的任务ID无效" % taskid)
        return jsonize({"success": False, "message": u"任务ID无效"})

###################
# Admin functions #
###################


@get("/admin/<taskid>/list")
def task_list(taskid=None):
    """
    pull拉取任务列表
    """
    tasks = {}

    for key in DataStore.tasks:
        if is_admin(taskid) or DataStore.tasks[key].remote_addr == request.remote_addr:
            tasks[key] = dejsonize(scan_status(key))["status"]

    logger.debug(u"[%s] 列出的任务池 (%s)" % (taskid, "admin" if is_admin(taskid) else request.remote_addr))
    return jsonize({"success": True, "tasks": tasks, "tasks_num": len(tasks)})

@get("/admin/<taskid>/flush")
def task_flush(taskid):
    """
    刷新任务spool（删除所有任务）
    """

    for key in list(DataStore.tasks):
        if is_admin(taskid) or DataStore.tasks[key].remote_addr == request.remote_addr:
            DataStore.tasks[key].engine_kill()
            del DataStore.tasks[key]

    logger.debug(u"[%s] 刷新任务池 (%s)" % (taskid, "admin" if is_admin(taskid) else request.remote_addr))
    return jsonize({"success": True})

##################################
#        sqlmap核心交互功能      #
##################################


# Handle task's options
@get("/option/<taskid>/list")
def option_list(taskid):
    """
    列出某个任务ID的选项
    """
    if taskid not in DataStore.tasks:
        logger.warning("[%s] 提供给option_list()的任务ID无效" % taskid)
        return jsonize({"success": False, "message": "任务ID无效"})

    logger.debug("[%s] Listed task options" % taskid)
    return jsonize({"success": True, "options": DataStore.tasks[taskid].get_options()})


@post("/option/<taskid>/get")
def option_get(taskid):
    """
    获取某个任务ID的选项（命令行开关）的值
    """
    if taskid not in DataStore.tasks:
        logger.warning(u"[%s] 提供给option_get()的任务ID无效" % taskid)
        return jsonize({"success": False, "message": u"任务ID无效"})

    option = request.json.get("option", "")

    if option in DataStore.tasks[taskid].options:
        logger.debug(u"[%s] 检索选项%s的值" % (taskid, option))
        return jsonize({"success": True, option: DataStore.tasks[taskid].get_option(option)})
    else:
        logger.debug(u"[%s] 未知选项%s的请求值" % (taskid, option))
        return jsonize({"success": False, "message": "Unknown option", option: "not set"})


@post("/option/<taskid>/set")
def option_set(taskid):
    """
    为某个任务ID设置一个选项（命令行开关）
    """
    if taskid not in DataStore.tasks:
        logger.warning(u"[%s] 提供给option_set()的任务ID无效" % taskid)
        return jsonize({"success": False, "message": u"任务ID无效"})

    for option, value in request.json.items():
        DataStore.tasks[taskid].set_option(option, value)

    logger.debug(u"[%s] 请求设置选项" % taskid)
    return jsonize({"success": True})


# Handle scans
@post("/scan/<taskid>/start")
def scan_start(taskid):
    """
    启动扫描
    """
    if taskid not in DataStore.tasks:
        logger.warning(u"[%s] 提供给scan_start()的任务ID无效" % taskid)
        return jsonize({"success": False, "message": u"任务ID无效"})

    # 使用用户提供的选项（如果有）初始化sqlmap引擎选项
    for option, value in request.json.items():
        DataStore.tasks[taskid].set_option(option, value)

    # 在单独的进程中启动sqlmap引擎
    DataStore.tasks[taskid].engine_start()

    logger.debug(u"[%s] 开始扫描" % taskid)
    return jsonize({"success": True, "engineid": DataStore.tasks[taskid].engine_get_id()})


@get("/scan/<taskid>/stop")
def scan_stop(taskid):
    """
    停止扫描
    """
    if (taskid not in DataStore.tasks or
            DataStore.tasks[taskid].engine_process() is None or
            DataStore.tasks[taskid].engine_has_terminated()):
        logger.warning(u"[%s] 提供给scan_stop()的任务ID无效" % taskid)
        return jsonize({"success": False, "message": u"任务ID无效"})

    DataStore.tasks[taskid].engine_stop()

    logger.debug(u"[%s] 停止扫描" % taskid)
    return jsonize({"success": True})


@get("/scan/<taskid>/kill")
def scan_kill(taskid):
    """
    杀死扫描
    """
    if (taskid not in DataStore.tasks or
            DataStore.tasks[taskid].engine_process() is None or
            DataStore.tasks[taskid].engine_has_terminated()):
        logger.warning(u"[%s] 提供给scan_kill()的任务ID无效" % taskid)
        return jsonize({"success": False, "message": "任务ID无效"})

    DataStore.tasks[taskid].engine_kill()

    logger.debug(u"[%s] 杀死扫描进程" % taskid)
    return jsonize({"success": True})


@get("/scan/<taskid>/status")
def scan_status(taskid):
    """
    返回扫描的状态
    """
    if taskid not in DataStore.tasks:
        logger.warning(u"[%s] 提供给scan_status()的任务ID无效" % taskid)
        return jsonize({"success": False, "message": u"任务ID无效"})

    if DataStore.tasks[taskid].engine_process() is None:
        status = "not running"
    else:
        status = "terminated" if DataStore.tasks[taskid].engine_has_terminated() is True else "running"

    logger.debug(u"[%s] 检索扫描状态" % taskid)
    return jsonize({
        "success": True,
        "status": status,
        "returncode": DataStore.tasks[taskid].engine_get_returncode()
    })


@get("/scan/<taskid>/data")
def scan_data(taskid):
    """
    检索扫描的数据
    """
    json_data_message = list()
    json_errors_message = list()

    if taskid not in DataStore.tasks:
        logger.warning(u"[%s] 提供给scan_data()的任务ID无效" % taskid)
        return jsonize({"success": False, "message": "任务ID无效"})

    # 从IPC数据库读取taskid的所有数据
    for status, content_type, value in DataStore.current_db.execute("SELECT status, content_type, value FROM data WHERE taskid = ? ORDER BY id ASC", (taskid,)):
        json_data_message.append({"status": status, "type": content_type, "value": dejsonize(value)})

    # 读取IPC数据库中的所有错误消息
    for error in DataStore.current_db.execute("SELECT error FROM errors WHERE taskid = ? ORDER BY id ASC", (taskid,)):
        json_errors_message.append(error)

    logger.debug(u"[%s] 检索的扫描数据和错误消息" % taskid)
    return jsonize({"success": True, "data": json_data_message, "error": json_errors_message})


# Functions to handle scans' logs
@get("/scan/<taskid>/log/<start>/<end>")
def scan_log_limited(taskid, start, end):
    """
    检索日志消息的子集
    """
    json_log_messages = list()

    if taskid not in DataStore.tasks:
        logger.warning(u"[%s] 提供给scan_log_limited()的任务ID无效" % taskid)
        return jsonize({"success": False, "message": "Invalid task ID"})

    if not start.isdigit() or not end.isdigit() or end < start:
        logger.warning(u"[%s] 提供给scan_log_limited()的起始值或结束值无效" % taskid)
        return jsonize({"success": False, "message": u"开始或结束值无效，必须为数字u"})

    start = max(1, int(start))
    end = max(1, int(end))

    # 从IPC数据库读取日志消息的子集
    for time_, level, message in DataStore.current_db.execute("SELECT time, level, message FROM logs WHERE taskid = ? AND id >= ? AND id <= ? ORDER BY id ASC", (taskid, start, end)):
        json_log_messages.append({"time": time_, "level": level, "message": message})

    logger.debug(u"[%s] 检索扫描日志信息子集" % taskid)
    return jsonize({"success": True, "log": json_log_messages})


@get("/scan/<taskid>/log")
def scan_log(taskid):
    """
    检索日志消息
    """
    json_log_messages = list()

    if taskid not in DataStore.tasks:
        logger.warning(u"提供给scan_log()的任务ID[%s]无效" % taskid)
        return jsonize({"success": False, "message": "任务ID无效"})

    # Read all log messages from the IPC database
    for time_, level, message in DataStore.current_db.execute("SELECT time, level, message FROM logs WHERE taskid = ? ORDER BY id ASC", (taskid,)):
        json_log_messages.append({"time": time_, "level": level, "message": message})

    logger.debug(u" 检索扫描[%s]的日志消息" % taskid)
    return jsonize({"success": True, "log": json_log_messages})


# Function to handle files inside the output directory
@get("/download/<taskid>/<target>/<filename:path>")
def download(taskid, target, filename):
    """
    从文件系统下载某个文件
    """
    if taskid not in DataStore.tasks:
        logger.warning(u"[%s] 提供给download()的任务ID无效" % taskid)
        return jsonize({"success": False, "message": u"无效的任务ID"})

    path = os.path.abspath(os.path.join(paths.SQLMAP_OUTPUT_PATH, target, filename))
    # Prevent file path traversal
    if not path.startswith(paths.SQLMAP_OUTPUT_PATH):
        logger.warning(u"[%s] 禁止路径 (%s)" % (taskid, target))
        return jsonize({"success": False, "message": u"禁止路径"})

    if os.path.isfile(path):
        logger.debug(u"[%s] 检索文件 %s 的内容" % (taskid, target))
        with open(path, 'rb') as inf:
            file_content = inf.read()
        return jsonize({"success": True, "file": file_content.encode("base64")})
    else:
        logger.warning(u"[%s] 文件不存在 %s" % (taskid, target))
        return jsonize({"success": False, "message": u"文件不存在"})


def server(host=RESTAPI_DEFAULT_ADDRESS, port=RESTAPI_DEFAULT_PORT, adapter=RESTAPI_DEFAULT_ADAPTER):
    """
    REST-JSON API server
    """
    DataStore.admin_id = hexencode(os.urandom(16))
    handle, Database.filepath = tempfile.mkstemp(prefix=MKSTEMP_PREFIX.IPC, text=False)
    os.close(handle)

    if port == 0:  # random
        with contextlib.closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
            s.bind((host, 0))
            port = s.getsockname()[1]

    logger.info("服务器运行在'%s:%d'.." % (host, port))
    logger.info("Admin ID: %s" % DataStore.admin_id)
    logger.debug("IPC database: '%s'" % Database.filepath)

    # 初始化IPC数据库
    DataStore.current_db = Database()
    DataStore.current_db.connect()
    DataStore.current_db.init()

    # Run RESTful API
    try:
        # 支持的适配器: aiohttp, auto, bjoern, cgi, cherrypy, diesel, eventlet, fapws3, flup, gae, gevent, geventSocketIO, gunicorn, meinheld, paste, rocket, tornado, twisted, waitress, wsgiref
        # 参考: https://bottlepy.org/docs/dev/deployment.html || bottle.server_names

        if adapter == "gevent":
            from gevent import monkey
            monkey.patch_all()
        elif adapter == "eventlet":
            import eventlet
            eventlet.monkey_patch()
        logger.debug("Using adapter '%s' to run bottle" % adapter)
        run(host=host, port=port, quiet=True, debug=False, server=adapter)
    except socket.error, ex:
        if "already in use" in getSafeExString(ex):
            logger.error("Address already in use ('%s:%s')" % (host, port))
        else:
            raise
    except ImportError:
        if adapter.lower() not in server_names:
            errMsg = u"适配器'%s'是未知的" % adapter
            errMsg += u"(注意:可用的适配器 '%s')" % ', '.join(sorted(server_names.keys()))
        else:
            errMsg = u"该系统上未安装适配器'%s'的驱动服务" % adapter
            errMsg += u"(注意：您可以尝试使用'sudo apt-get install python-%s'或'sudo pip install %s')" % (adapter, adapter)
        logger.critical(errMsg)

def _client(url, options=None):
    logger.debug("Calling %s" % url)
    try:
        data = None
        if options is not None:
            data = jsonize(options)
        req = urllib2.Request(url, data, {"Content-Type": "application/json"})
        response = urllib2.urlopen(req)
        text = response.read()
    except:
        if options:
            logger.error(u"无法加载和解析 %s" % url)
        raise
    return text


def client(host=RESTAPI_DEFAULT_ADDRESS, port=RESTAPI_DEFAULT_PORT):
    """
    REST-JSON API client
    """

    dbgMsg = u"从命令行访问客户端示例:"
    dbgMsg += "\n\t$ taskid=$(curl http://%s:%d/task/new 2>1 | grep -o -I '[a-f0-9]\{16\}') && echo $taskid" % (host, port)
    dbgMsg += "\n\t$ curl -H \"Content-Type: application/json\" -X POST -d '{\"url\": \"http://testphp.vulnweb.com/artists.php?artist=1\"}' http://%s:%d/scan/$taskid/start" % (host, port)
    dbgMsg += "\n\t$ curl http://%s:%d/scan/$taskid/data" % (host, port)
    dbgMsg += "\n\t$ curl http://%s:%d/scan/$taskid/log" % (host, port)
    logger.debug(dbgMsg)

    addr = "http://%s:%d" % (host, port)
    logger.info(u"启动REST-JSON API客户端到'%s'..." % addr)

    try:
        _client(addr)
    except Exception, ex:
        if not isinstance(ex, urllib2.HTTPError):
            errMsg = u"在'%s'连接到REST-JSON API服务器时出现问题(%s)" % (addr, ex)
            logger.critical(errMsg)
            return

    taskid = None
    logger.info(u"输入'help'或'?'列出可用的命令")

    while True:
        try:
            command = raw_input("api%s> " % (" (%s)" % taskid if taskid else "")).strip()
            command = re.sub(r"\A(\w+)", lambda match: match.group(1).lower(), command)
        except (EOFError, KeyboardInterrupt):
            print
            break

        if command in ("data", "log", "status", "stop", "kill"):
            if not taskid:
                logger.error(u"任务ID没有被使用")
                continue
            raw = _client("%s/scan/%s/%s" % (addr, taskid, command))
            res = dejsonize(raw)
            if not res["success"]:
                logger.error(u"无法执行命令 %s" % command)
            dataToStdout("%s\n" % raw)

        elif command.startswith("option"):
            if not taskid:
                logger.error(u"任务ID没有被使用")
                continue
            try:
                command, option = command.split(" ")
            except ValueError:
                raw = _client("%s/option/%s/list" % (addr, taskid))
            else:
                options = {"option": option}
                raw = _client("%s/option/%s/get" % (addr, taskid), options)
            res = dejsonize(raw)
            if not res["success"]:
                logger.error(u"无法执行命令 %s" % command)
            dataToStdout("%s\n" % raw)

        elif command.startswith("new"):
            if ' ' not in command:
                logger.error(u"缺少程序参数")
                continue

            try:
                argv = ["sqlmap.py"] + shlex.split(command)[1:]
            except Exception, ex:
                logger.error(u"解析参数('%s')时出错" % ex)
                taskid = None
                continue

            try:
                cmdLineOptions = cmdLineParser(argv).__dict__
            except:
                taskid = None
                continue

            for key in list(cmdLineOptions):
                if cmdLineOptions[key] is None:
                    del cmdLineOptions[key]

            raw = _client("%s/task/new" % addr)
            res = dejsonize(raw)
            if not res["success"]:
                logger.error(u"无法创建新任务")
                continue
            taskid = res["taskid"]
            logger.info(u"新任务ID为'%s'" % taskid)

            raw = _client("%s/scan/%s/start" % (addr, taskid), cmdLineOptions)
            res = dejsonize(raw)
            if not res["success"]:
                logger.error(u"无法启动扫描")
                continue
            logger.info(u"扫描开始")

        elif command.startswith("use"):
            taskid = (command.split()[1] if ' ' in command else "").strip("'\"")
            if not taskid:
                logger.error(u"找不到这个任务ID")
                taskid = None
                continue
            elif not re.search(r"\A[0-9a-fA-F]{16}\Z", taskid):
                logger.error(u"任务ID'%s'无效" % taskid)
                taskid = None
                continue
            logger.info(u"切换到任务ID '%s' " % taskid)

        elif command in ("list", "flush"):
            raw = _client("%s/admin/%s/%s" % (addr, taskid or 0, command))
            res = dejsonize(raw)
            if not res["success"]:
                logger.error(u"无法执行命令 %s" % command)
            elif command == "flush":
                taskid = None
            dataToStdout("%s\n" % raw)

        elif command in ("exit", "bye", "quit", 'q'):
            return

        elif command in ("help", "?"):
            msg =  u"help           显示此帮助信息\n"
            msg += u"new ARGS       使用提供的参数启动新的扫描任务 (例如 'new -u \"http://testphp.vulnweb.com/artists.php?artist=1\"')\n"
            msg += "use TASKID     切换当前上下文到不同的任务 (例如 'use c04d8c5c7582efb4')\n"
            msg += u"data           检索并显示当前任务的数据\n"
            msg += u"log            检索并显示当前任务的日志\n"
            msg += u"status         检索并显示当前任务的状态\n"
            msg += u"option OPTION  检索并显示当前任务的选项\n"
            msg += u"options        检索并显示当前任务的所有选项\n"
            msg += u"stop           停止当前任务\n"
            msg += u"kill           杀死当前任务\n"
            msg += u"list           显示所有任务\n"
            msg += u"flush          刷新任务(删除所有任务)\n"
            msg += u"exit           退出客户端\n"

            dataToStdout(msg)

        elif command:
            logger.error(u"未知命令'%s'" % command)
