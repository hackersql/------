#!/usr/bin/env python
#coding=utf-8
"""
Copyright (c) 2006-2017 sqlmap developers (http://sqlmap.org/)
See the file 'doc/COPYING' for copying permission
"""

import logging
import optparse
import sys

sys.dont_write_bytecode = True

__import__("lib.utils.versioncheck")  # this has to be the first non-standard import

from sqlmap import modulePath
from lib.core.common import setPaths
from lib.core.data import logger
from lib.core.settings import RESTAPI_DEFAULT_ADAPTER
from lib.core.settings import RESTAPI_DEFAULT_ADDRESS
from lib.core.settings import RESTAPI_DEFAULT_PORT
from lib.utils.api import client
from lib.utils.api import server

def main():
    """
    REST-JSON API 主函数
    """

    # 将默认日志记录级别设置为debug
    logger.setLevel(logging.DEBUG)

    # 初始化路径
    setPaths(modulePath())

    # 解析命令行选项
    apiparser = optparse.OptionParser()
    apiparser.add_option("-s", "--server", help=u"作为REST-JSON API服务器", default=RESTAPI_DEFAULT_PORT, action="store_true")
    apiparser.add_option("-c", "--client", help=u"作为REST-JSON API客户端", default=RESTAPI_DEFAULT_PORT, action="store_true")
    apiparser.add_option("-H", "--host", help="REST-JSON API服务器主机地址(默认为 \"%s\")" % RESTAPI_DEFAULT_ADDRESS, default=RESTAPI_DEFAULT_ADDRESS, action="store")
    apiparser.add_option("-p", "--port", help="REST-JSON服务器端口(默认为 %d)" % RESTAPI_DEFAULT_PORT, default=RESTAPI_DEFAULT_PORT, type="int", action="store")
    apiparser.add_option("--adapter", help="要使用的服务器适配器(默认为 \"%s\")" % RESTAPI_DEFAULT_ADAPTER, default=RESTAPI_DEFAULT_ADAPTER, action="store")
    (args, _) = apiparser.parse_args()
    """
    adapter(适配器)定义为将一个类的接口变换成客户端所期待的一种接口，
    从而使原本因接口不匹配而无法在一起工作的两个类能够在一起工作。
    """

    # 启动客户端或服务器
    if args.server is True:
        server(args.host, args.port, adapter=args.adapter)
    elif args.client is True:
        client(args.host, args.port)
    else:
        apiparser.print_help()

if __name__ == "__main__":
    main()
