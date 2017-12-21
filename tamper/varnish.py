#!/usr/bin/env python
#coding=utf-8
"""
Copyright (c) 2006-2017 sqlmap developers (http://sqlmap.org/)
See the file 'doc/COPYING' for copying permission
"""

from lib.core.enums import PRIORITY

__priority__ = PRIORITY.NORMAL

def dependencies():
    pass

def tamper(payload, **kwargs):
    """
    附加一个HTTP头"X-originating-IP"来绕过WAF保护防火墙

    127.0.0.1（Loopback Address）是回送地址，指本地机，一般用来测试使用。
    即主机IP堆栈内部的IP地址，主要用于网络软件测试以及本地机进程间通信，
    无论什么程序，一旦使用回送地址发送数据，协议软件立即返回，不进行任何网络传输。

    Notes:
        Reference: http://h30499.www3.hp.com/t5/Fortify-Application-Security/Bypassing-web-application-firewalls-using-HTTP-headers/ba-p/6418366

        Examples:
        >> X-forwarded-for: TARGET_CACHESERVER_IP (184.189.250.X)
        >> X-remote-IP: TARGET_PROXY_IP (184.189.250.X)
        >> X-originating-IP: TARGET_LOCAL_IP (127.0.0.1)
        >> x-remote-addr: TARGET_INTERNALUSER_IP (192.168.1.X)
        >> X-remote-IP: * or %00 or %0A
    """

    headers = kwargs.get("headers", {})
    headers["X-originating-IP"] = "127.0.0.1"
    return payload
