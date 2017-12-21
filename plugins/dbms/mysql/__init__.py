#!/usr/bin/env python
#coding=utf-8
"""
Copyright (c) 2006-2017 sqlmap developers (http://sqlmap.org/)
See the file 'doc/COPYING' for copying permission
"""

from lib.core.enums import DBMS
from lib.core.settings import MYSQL_SYSTEM_DBS
from lib.core.unescaper import unescaper
from plugins.dbms.mysql.enumeration import Enumeration
from plugins.dbms.mysql.filesystem import Filesystem
from plugins.dbms.mysql.fingerprint import Fingerprint
from plugins.dbms.mysql.syntax import Syntax
from plugins.dbms.mysql.takeover import Takeover
from plugins.generic.misc import Miscellaneous

class MySQLMap(Syntax, Fingerprint, Enumeration, Filesystem, Miscellaneous, Takeover):
    """
    这个类定义了MySQL方法
    """

    def __init__(self):
        self.excludeDbsList = MYSQL_SYSTEM_DBS
        self.sysUdfs = {
                         # 自定义函数:    自定义函数返回类型
                         "sys_exec":    { "return": "int" },
                         "sys_eval":    { "return": "string" },
                         "sys_bineval": { "return": "int" }
                       }

        Syntax.__init__(self)
        Fingerprint.__init__(self)
        Enumeration.__init__(self)
        Filesystem.__init__(self)
        Miscellaneous.__init__(self)
        Takeover.__init__(self)

    unescaper[DBMS.MYSQL] = Syntax.escape
