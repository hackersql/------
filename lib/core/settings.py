#!/usr/bin/env python
#coding=utf-8
"""
Copyright (c) 2006-2017 sqlmap developers (http://sqlmap.org/)
See the file 'doc/COPYING' for copying permission
"""

import os
import random
import re
import subprocess
import string
import sys
import types

from lib.core.datatype import AttribDict
from lib.core.enums import DBMS
from lib.core.enums import DBMS_DIRECTORY_NAME
from lib.core.enums import OS

# sqlmap version (<major>.<minor>.<month>.<monthly commit>)
VERSION = "1.1.7.21"
TYPE = "dev" if VERSION.count('.') > 2 and VERSION.split('.')[-1] != '0' else "stable"
TYPE_COLORS = {"dev": 33, "stable": 90, "pip": 34}
VERSION_STRING = u"sqlmap/%s#%s" % ('.'.join(VERSION.split('.')[:-1]) if VERSION.count('.') > 2 and VERSION.split('.')[-1] == '0' else VERSION, TYPE)
DESCRIPTION = "automatic SQL injection and database takeover tool"
SITE = u"欢迎使用sq1map中文版 by hackersql"
ISSUES_PAGE = "https://github.com/sqlmapproject/sqlmap/issues/new"
GIT_REPOSITORY = "git://github.com/hackersql/sq1map.git"
GIT_PAGE = "https://github.com/hackersql/sq1map.git"
DEFAULT_SQLMAP_HTTP_USER_AGENT = "Mozilla/5.0 (iPhone; CPU iPhone OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A5376e Safari/8536.25"

# colorful banner
BANNER = """\033[01;33m\
        ___
       __H__
 ___ ___[.]_____ ___ ___  \033[01;37m{\033[01;%dm%s\033[01;37m}\033[01;33m
|_ -| . [.]     | .'| . |
|___|_  [.]_|_|_|__,|  _|
      |_|V          |_|   \033[0m\033[4;37m%s\033[0m\n
""" % (TYPE_COLORS.get(TYPE, 31), VERSION_STRING.split('/')[-1], SITE)

# 与kb.matchRatio的最小比例距离导致为True
DIFF_TOLERANCE = 0.05
CONSTANT_RATIO = 0.9

# 用于启发式检查WAF/IPS/IDS保护目标的比例
IDS_WAF_CHECK_RATIO = 0.5

# 用于启发式检查WAF/IPS/IDS保护目标，超时时间
IDS_WAF_CHECK_TIMEOUT = 10

# 在页面稳定的情况下匹配比例的较低和较高值
LOWER_RATIO_BOUND = 0.02
UPPER_RATIO_BOUND = 0.98

# 标记特殊情况下，当参数值包含HTML编码字符
PARAMETER_AMP_MARKER = "__AMP__"
PARAMETER_SEMICOLON_MARKER = "__SEMICOLON__"
BOUNDARY_BACKSLASH_MARKER = "__BACKSLASH__"
PARTIAL_VALUE_MARKER = "__PARTIAL_VALUE__"
PARTIAL_HEX_VALUE_MARKER = "__PARTIAL_HEX_VALUE__"
URI_QUESTION_MARKER = "__QUESTION_MARK__"
ASTERISK_MARKER = "__ASTERISK_MARK__"
REPLACEMENT_MARKER = "__REPLACEMENT_MARK__"
BOUNDED_INJECTION_MARKER = "__BOUNDED_INJECTION_MARK__"

RANDOM_INTEGER_MARKER = "[RANDINT]"
RANDOM_STRING_MARKER = "[RANDSTR]"
SLEEP_TIME_MARKER = "[SLEEPTIME]"

PAYLOAD_DELIMITER = "__PAYLOAD_DELIMITER__"
CHAR_INFERENCE_MARK = "%c"
PRINTABLE_CHAR_REGEX = r"[^\x00-\x1f\x7f-\xff]"

# 用于提取表名称的正则表达式(例如 Ms Access)
SELECT_FROM_TABLE_REGEX = r"\bSELECT .+? FROM (?P<result>([\w.]|`[^`<>]+`)+)"

# 用于识别文本内容类型的正则表达式
TEXT_CONTENT_TYPE_REGEX = r"(?i)(text|form|message|xml|javascript|ecmascript|json)"

# 用于识别通用权限消息的正则表达式
PERMISSION_DENIED_REGEX = r"(command|permission|access)\s*(was|is)?\s*denied"

# 用于识别通用最大连接消息的正则表达式
MAX_CONNECTIONS_REGEX = r"max.+connections"

# 在询问用户是否要继续之前，连续连接错误最多次数
MAX_CONSECUTIVE_CONNECTION_ERRORS = 15

# 预连接之前的超时时间(由于Web服务器重置它的可能性很高)
PRECONNECT_CANDIDATE_TIMEOUT = 10

# “Murphy”（测试）模式下的最长睡眠时间
MAX_MURPHY_SLEEP_TIME = 3

# 用于从Google搜索中提取结果的正则表达式
GOOGLE_REGEX = r"webcache\.googleusercontent\.com/search\?q=cache:[^:]+:([^+]+)\+&amp;cd=|url\?\w+=((?![^>]+webcache\.googleusercontent\.com)http[^>]+)&(sa=U|rct=j)"

# 用于从DuckDuckGo搜索中提取结果的正则表达式
DUCKDUCKGO_REGEX = r'"u":"([^"]+)'

# 用于从搜索断开的页面中提取结果的正则表达式
DISCONNECT_SEARCH_REGEX = r'<p class="url wrapword">([^<]+)</p>'

# 用于搜索的虚拟用户代理（如果默认用户代理返回不同的结果）
DUMMY_SEARCH_USER_AGENT = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:49.0) Gecko/20100101 Firefox/49.0"

# 用于从“文本”标签中提取内容的正则表达式
TEXT_TAG_REGEX = r"(?si)<(abbr|acronym|b|blockquote|br|center|cite|code|dt|em|font|h\d|i|li|p|pre|q|strong|sub|sup|td|th|title|tt|u)(?!\w).*?>(?P<result>[^<]+)"

# 用于识别IP地址的正则表达式
IP_ADDRESS_REGEX = r"\b(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\b"

# Regular expression used for recognition of generic "your ip has been blocked" messages
# 用于识别通用的“您的ip已被阻止”消息的正则表达式
BLOCKED_IP_REGEX = r"(?i)(\A|\b)ip\b.*\b(banned|blocked|block list|firewall)"

# 在GROUP_CONCAT MySQL技术中使用的转储字符
CONCAT_ROW_DELIMITER = ','
CONCAT_VALUE_DELIMITER = '|'

# 用于基于时间的查询延迟检查的系数（必须 >= 7）
TIME_STDEV_COEFF = 7

# 其甚至可以被视为延迟最小响应时间（不是一个完整的要求）
MIN_VALID_DELAYED_RESPONSE = 0.5

# 标准偏差后，应显示关于连接滞后的警告消息
WARN_TIME_STDEV = 0.5

# 可用联合注入响应的最小长度（针对子区域的快速防御）
UNION_MIN_RESPONSE_CHARS = 10

# 用于基于联合的列数检查的系数（必须> = 7）
UNION_STDEV_COEFF = 7

# 延时调整候选队列长度
TIME_DELAY_CANDIDATES = 3

# HTTP Accept标头的默认值
HTTP_ACCEPT_HEADER_VALUE = "*/*"

# HTTP Accept-Encoding标头的默认值
HTTP_ACCEPT_ENCODING_HEADER_VALUE = "gzip,deflate"

# 通过后门运行命令的默认超时时间
BACKDOOR_RUN_CMD_TIMEOUT = 5

# 在程序结束时等待线程完成的秒数
THREAD_FINALIZATION_TIMEOUT = 1

# 每一个值在inject.py/getValue()中使用的最大技术数量
MAX_TECHNIQUES_PER_VALUE = 2

# 如果缺少部分联合转储，缓冲数组必须在一定大小后刷新
MAX_BUFFERED_PARTIAL_UNION_LENGTH = 1024

# 用于在没有显式数据库名称的情况下在DBMS（es）中命名元数据库的后缀
METADB_SUFFIX = "_masterdb"

# 异常期间重试pushValue的次数（例如KeyboardInterrupt）
PUSH_VALUE_EXCEPTION_RETRY_COUNT = 3

# 基于标准差的时间比较所需的最小时间响应集
MIN_TIME_RESPONSES = 30

# 根据标准偏差搜索有效联合列号union column所需的最小比较比
MIN_UNION_RESPONSES = 5

# 在结束推理后的这些空白数目应该停止（以防万一）
INFERENCE_BLANK_BREAK = 10

# 当推理不能检索正确的字符值时，请使用此替换字符
INFERENCE_UNKNOWN_CHAR = '?'

# 在推理中使用大于号
INFERENCE_GREATER_CHAR = ">"

# 推理中使用等于号
INFERENCE_EQUALS_CHAR = "="

# 推理中使用不等于号
INFERENCE_NOT_EQUALS_CHAR = "!="

# 用于表示未知DBMS的字符串
UNKNOWN_DBMS = "Unknown"

# 用于表示未知DBMS版本的字符串
UNKNOWN_DBMS_VERSION = "Unknown"

# 动态清除引擎中使用的动态标记长度
DYNAMICITY_MARK_LENGTH = 32

# 字典攻击中使用的虚拟用户前缀
DUMMY_USER_PREFIX = "__dummy__"

# 参考: http://en.wikipedia.org/wiki/ISO/IEC_8859-1
DEFAULT_PAGE_ENCODING = "iso-8859-1"

# 在虚拟试验中使用的网址
DUMMY_URL = "http://foo/bar?id=1"

# 系统变量
IS_WIN = subprocess.mswindows

# 导入操作系统依赖模块的名称，以下名称目前已注册：'posix'，'nt'，'mac'，'os2'，'ce'，'java'，'riscos'
PLATFORM = os.name
PYVERSION = sys.version.split()[0]

# DBMS系统数据库
MSSQL_SYSTEM_DBS = ("Northwind", "master", "model", "msdb", "pubs", "tempdb")
MYSQL_SYSTEM_DBS = ("information_schema", "mysql", "performance_schema")
PGSQL_SYSTEM_DBS = ("information_schema", "pg_catalog", "pg_toast", "pgagent")
ORACLE_SYSTEM_DBS = ("ANONYMOUS", "APEX_PUBLIC_USER", "CTXSYS", "DBSNMP", "DIP", "EXFSYS", "FLOWS_%", "FLOWS_FILES", "LBACSYS", "MDDATA", "MDSYS", "MGMT_VIEW", "OLAPSYS", "ORACLE_OCM", "ORDDATA", "ORDPLUGINS", "ORDSYS", "OUTLN", "OWBSYS", "SI_INFORMTN_SCHEMA", "SPATIAL_CSW_ADMIN_USR", "SPATIAL_WFS_ADMIN_USR", "SYS", "SYSMAN", "SYSTEM", "WKPROXY", "WKSYS", "WK_TEST", "WMSYS", "XDB", "XS$NULL")  # Reference: https://blog.vishalgupta.com/2011/06/19/predefined-oracle-system-schemas/ 
SQLITE_SYSTEM_DBS = ("sqlite_master", "sqlite_temp_master")
ACCESS_SYSTEM_DBS = ("MSysAccessObjects", "MSysACEs", "MSysObjects", "MSysQueries", "MSysRelationships", "MSysAccessStorage", "MSysAccessXML", "MSysModules", "MSysModules2")
FIREBIRD_SYSTEM_DBS = ("RDB$BACKUP_HISTORY", "RDB$CHARACTER_SETS", "RDB$CHECK_CONSTRAINTS", "RDB$COLLATIONS", "RDB$DATABASE", "RDB$DEPENDENCIES", "RDB$EXCEPTIONS", "RDB$FIELDS", "RDB$FIELD_DIMENSIONS", " RDB$FILES", "RDB$FILTERS", "RDB$FORMATS", "RDB$FUNCTIONS", "RDB$FUNCTION_ARGUMENTS", "RDB$GENERATORS", "RDB$INDEX_SEGMENTS", "RDB$INDICES", "RDB$LOG_FILES", "RDB$PAGES", "RDB$PROCEDURES", "RDB$PROCEDURE_PARAMETERS", "RDB$REF_CONSTRAINTS", "RDB$RELATIONS", "RDB$RELATION_CONSTRAINTS", "RDB$RELATION_FIELDS", "RDB$ROLES", "RDB$SECURITY_CLASSES", "RDB$TRANSACTIONS", "RDB$TRIGGERS", "RDB$TRIGGER_MESSAGES", "RDB$TYPES", "RDB$USER_PRIVILEGES", "RDB$VIEW_RELATIONS")
MAXDB_SYSTEM_DBS = ("SYSINFO", "DOMAIN")
SYBASE_SYSTEM_DBS = ("master", "model", "sybsystemdb", "sybsystemprocs")
DB2_SYSTEM_DBS = ("NULLID", "SQLJ", "SYSCAT", "SYSFUN", "SYSIBM", "SYSIBMADM", "SYSIBMINTERNAL", "SYSIBMTS", "SYSPROC", "SYSPUBLIC", "SYSSTAT", "SYSTOOLS")
HSQLDB_SYSTEM_DBS = ("INFORMATION_SCHEMA", "SYSTEM_LOB")
INFORMIX_SYSTEM_DBS = ("sysmaster", "sysutils", "sysuser", "sysadmin")

MSSQL_ALIASES = ("microsoft sql server", "mssqlserver", "mssql", "ms")
MYSQL_ALIASES = ("mysql", "my", "mariadb", "maria")
PGSQL_ALIASES = ("postgresql", "postgres", "pgsql", "psql", "pg")
ORACLE_ALIASES = ("oracle", "orcl", "ora", "or")
SQLITE_ALIASES = ("sqlite", "sqlite3")
ACCESS_ALIASES = ("msaccess", "access", "jet", "microsoft access")
FIREBIRD_ALIASES = ("firebird", "mozilla firebird", "interbase", "ibase", "fb")
MAXDB_ALIASES = ("maxdb", "sap maxdb", "sap db")
SYBASE_ALIASES = ("sybase", "sybase sql server")
DB2_ALIASES = ("db2", "ibm db2", "ibmdb2")
HSQLDB_ALIASES = ("hsql", "hsqldb", "hs", "hypersql")
INFORMIX_ALIASES = ("informix", "ibm informix", "ibminformix")

DBMS_DIRECTORY_DICT = dict((getattr(DBMS, _), getattr(DBMS_DIRECTORY_NAME, _)) for _ in dir(DBMS) if not _.startswith("_"))

SUPPORTED_DBMS = MSSQL_ALIASES + MYSQL_ALIASES + PGSQL_ALIASES + ORACLE_ALIASES + SQLITE_ALIASES + ACCESS_ALIASES + FIREBIRD_ALIASES + MAXDB_ALIASES + SYBASE_ALIASES + DB2_ALIASES + HSQLDB_ALIASES + INFORMIX_ALIASES
SUPPORTED_OS = ("linux", "windows")

DBMS_ALIASES = ((DBMS.MSSQL, MSSQL_ALIASES), (DBMS.MYSQL, MYSQL_ALIASES), (DBMS.PGSQL, PGSQL_ALIASES), (DBMS.ORACLE, ORACLE_ALIASES), (DBMS.SQLITE, SQLITE_ALIASES), (DBMS.ACCESS, ACCESS_ALIASES), (DBMS.FIREBIRD, FIREBIRD_ALIASES), (DBMS.MAXDB, MAXDB_ALIASES), (DBMS.SYBASE, SYBASE_ALIASES), (DBMS.DB2, DB2_ALIASES), (DBMS.HSQLDB, HSQLDB_ALIASES))

USER_AGENT_ALIASES = ("ua", "useragent", "user-agent")
REFERER_ALIASES = ("ref", "referer", "referrer")
HOST_ALIASES = ("host",)

HSQLDB_DEFAULT_SCHEMA = "PUBLIC"

# 不能用于在Windows操作系统上命名文件的名称
WINDOWS_RESERVED_NAMES = ("CON", "PRN", "AUX", "NUL", "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9", "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9")

# 基本帮助(-h)输出中显示的项目
BASIC_HELP_ITEMS = (
    "url",
    "googleDork",
    "data",
    "cookie",
    "randomAgent",
    "proxy",
    "testParameter",
    "dbms",
    "level",
    "risk",
    "tech",
    "getAll",
    "getBanner",
    "getCurrentUser",
    "getCurrentDb",
    "getPasswordHashes",
    "getTables",
    "getColumns",
    "getSchema",
    "dumpTable",
    "dumpAll",
    "db",
    "tbl",
    "col",
    "osShell",
    "osPwn",
    "batch",
    "checkTor",
    "flushSession",
    "tor",
    "sqlmapShell",
    "wizard",
)

# NULL值的字符串表示形式
NULL = "NULL"

# 空白('')值的字符串表示形式
BLANK = "<blank>"

# 当前数据库的字符串表示
CURRENT_DB = "CD"

# 用于在错误消息中查找文件路径的正则表达式
FILE_PATH_REGEXES = (r"<b>(?P<result>[^<>]+?)</b> on line \d+", r"(?P<result>[^<>'\"]+?)['\"]? on line \d+", r"(?:[>(\[\s])(?P<result>[A-Za-z]:[\\/][\w. \\/-]*)", r"(?:[>(\[\s])(?P<result>/\w[/\w.-]+)", r"href=['\"]file://(?P<result>/[^'\"]+)")

# 用于解析错误消息的正则表达式(--parse-errors)
ERROR_PARSING_REGEXES = (
    r"<b>[^<]*(fatal|error|warning|exception)[^<]*</b>:?\s*(?P<result>.+?)<br\s*/?\s*>",
    r"(?m)^(fatal|error|warning|exception):?\s*(?P<result>[^\n]+?)$",
    r"(?P<result>[^\n>]*SQL Syntax[^\n<]+)",
    r"<li>Error Type:<br>(?P<result>.+?)</li>",
    r"CDbCommand (?P<result>[^<>\n]*SQL[^<>\n]+)",
    r"error '[0-9a-f]{8}'((<[^>]+>)|\s)+(?P<result>[^<>]+)",
    r"\[[^\n\]]+(ODBC|JDBC)[^\n\]]+\](\[[^\]]+\])?(?P<result>[^\n]+(in query expression|\(SQL| at /[^ ]+pdo)[^\n<]+)"
)

# 用于从html headers头中的meta标签解析charset信息的正则表达式
# charset设置网页的文件编码，作用是声明客户端的浏览器用什么字符集编码显示该页面，例如GBK、UTF-8
META_CHARSET_REGEX = r'(?si)<head>.*<meta[^>]+charset="?(?P<result>[^"> ]+).*</head>'

# 用于从meta html标头解析refresh信息的正则表达式
# refresh用于刷新与跳转(重定向)页面
# refresh出现在http-equiv属性中，使用content属性表示刷新或跳转的开始时间与跳转的网址
# 5秒之后刷新本页面:
# <meta http-equiv="refresh" content="5" />
# 5秒之后转到指定网页:
# <meta http-equiv="refresh" content="5; url=http://www.xxx.com/" />
META_REFRESH_REGEX = r'(?si)<head>(?!.*?<noscript.*?</head).*?<meta http-equiv="?refresh"?[^>]+content="?[^">]+url=["\']?(?P<result>[^\'">]+).*</head>'

# 用于在测试的表单数据中解析空字段的正则表达式
EMPTY_FORM_FIELDS_REGEX = r'(&|\A)(?P<result>[^=]+=(&|\Z))'

# 常用密码后缀，有些网站要求设置密码不能是纯字母，所以下面的数字是大家在字母后添加最多的数字密码后缀
# MySpace密码要求迫使人们至少输入一个非字母字符。在密码结尾添加单个1似乎是最受欢迎的选择
# 下表显示了通过MySpace密码要求附加到字母密码的最流行的数字后缀。大多数人只需在其密码中添加“1”即可。
# Reference: http://www.cs.ru.nl/bachelorscripties/2010/Martin_Devillers___0437999___Analyzing_password_strength.pdf
COMMON_PASSWORD_SUFFIXES = ("1", "123", "2", "12", "3", "13", "7", "11", "5", "22", "23", "01", "4", "07", "21", "14", "10", "06", "08", "8", "15", "69", "16", "6", "18")

# MySpace要求每个密码至少包含一个非字母字符（如0，1，2，或！，？，@）
# Reference: http://www.the-interweb.com/serendipity/index.php?/archives/94-A-brief-analysis-of-40,000-leaked-MySpace-passwords.html
COMMON_PASSWORD_SUFFIXES += ("!", ".", "*", "!!", "?", ";", "..", "!!!", ", ", "@")

# 在WebScarab日志文件中的请求之间使用分割器
WEBSCARAB_SPLITTER = "### Conversation"

# BURP日志文件中的请求之间使用分割器
BURP_REQUEST_REGEX = r"={10,}\s+[^=]+={10,}\s(.+?)\s={10,}"

# 用于解析XML Burp保存的历史项目的正则表达式
BURP_XML_HISTORY_REGEX = r'<port>(\d+)</port>.+?<request base64="true"><!\[CDATA\[([^]]+)'

# 用于Unicode数据的编码
UNICODE_ENCODING = "utf8"

# Reference: http://www.w3.org/Protocols/HTTP/Object_Headers.html#uri
URI_HTTP_HEADER = "URI"

# Uri format which could be injectable (e.g. www.site.com/id82)
URI_INJECTABLE_REGEX = r"//[^/]*/([^\.*?]+)\Z"

# 用于掩蔽敏感数据的正则表达式
SENSITIVE_DATA_REGEX = "(\s|=)(?P<result>[^\s=]*%s[^\s]*)\s"

# 在匿名(未处理的异常)报告中显式隐藏的选项(以及内部带有<hostname>等的任何内容)
SENSITIVE_OPTIONS = ("hostname", "data", "dnsDomain", "googleDork", "authCred", "proxyCred", "tbl", "db", "col", "user", "cookie", "proxy", "rFile", "wFile", "dFile", "testParameter", "authCred")

# 最大线程数(避免连接问题或DoS)
MAX_NUMBER_OF_THREADS = 10

# 统计集的最小和最大值之间的最小范围
MIN_STATISTICAL_RANGE = 0.01

# 比较值的最小值
MIN_RATIO = 0.0

# 比较值的最大值
MAX_RATIO = 1.0

# 自动选择字符串的最小句子长度（在匹配率高的情况下）
CANDIDATE_SENTENCE_MIN_LENGTH = 10

# 用于标记提供数据内的注入位置的字符
CUSTOM_INJECTION_MARK_CHAR = '*'

# 其他方式来声明注入位置
INJECT_HERE_REGEX = '(?i)%INJECT[_ ]?HERE%'

# 用于通过基于错误的payloads检索数据的最小块长度
MIN_ERROR_CHUNK_LENGTH = 8

# 用于通过基于错误的有效载荷检索数据的最大块长度
MAX_ERROR_CHUNK_LENGTH = 1024

# 如果注入的语句包含以下任何SQL关键字，请不要转义
EXCLUDE_UNESCAPE = ("WAITFOR DELAY ", " INTO DUMPFILE ", " INTO OUTFILE ", "CREATE ", "BULK ", "EXEC ", "RECONFIGURE ", "DECLARE ", "'%s'" % CHAR_INFERENCE_MARK)

# 标记用于替换反射值
REFLECTED_VALUE_MARKER = "__REFLECTED_VALUE__"

# 用于替换边界非字母字符的正则表达式
REFLECTED_BORDER_REGEX = r"[^A-Za-z]+"

# 用于替换非字母字符的正则表达式
REFLECTED_REPLACEMENT_REGEX = r".+"

# 每个反射值替换所用的最大时间（秒）
REFLECTED_REPLACEMENT_TIMEOUT = 3

# 反射正则表达式中的字母数字最大数量（用于速度）
REFLECTED_MAX_REGEX_PARTS = 10

# 可以在URL编码值过长的情况下用作故障安全值的字符
URLENCODE_FAILSAFE_CHARS = "()|,"

# URL编码值的最大长度，在此之后的值将被舍弃
URLENCODE_CHAR_LIMIT = 2000

# Microsoft SQL Server DBMS的默认模式
DEFAULT_MSSQL_SCHEMA = "dbo"

# 显示散列攻击信息每个模块的项目
HASH_MOD_ITEM_DISPLAY = 11

# 最大整数值
MAX_INT = sys.maxint

# 需要在多个目标运行模式下还原的选项
RESTORE_MERGED_OPTIONS = ("col", "db", "dnsDomain", "privEsc", "tbl", "regexp", "string", "textOnly", "threads", "timeSec", "tmpPath", "uChar", "user")

# 检测阶段要忽略的参数（大写）
IGNORE_PARAMETERS = ("__VIEWSTATE", "__VIEWSTATEENCRYPTED", "__VIEWSTATEGENERATOR", "__EVENTARGUMENT", "__EVENTTARGET", "__EVENTVALIDATION", "ASPSESSIONID", "ASP.NET_SESSIONID", "JSESSIONID", "CFID", "CFTOKEN")

# 用于识别ASP.NET控件参数的正则表达式
ASP_NET_CONTROL_REGEX = r"(?i)\Actl\d+\$"

# Google Analytics（分析）Cookie名称的前缀
GOOGLE_ANALYTICS_COOKIE_PREFIX = "__UTM"

# 配置覆盖环境变量的前缀
SQLMAP_ENVIRONMENT_PREFIX = "SQLMAP_"

# 关闭恢复控制台信息以避免可能引起的系统变慢
TURN_OFF_RESUME_INFO_LIMIT = 20

# 用于多目标模式的结果文件的Strftime格式
RESULTS_FILE_FORMAT = "results-%m%d%Y_%I%M%p.csv"

# 具有Python支持的编解码器列表的官方网页
CODECS_LIST_PAGE = "http://docs.python.org/library/codecs.html#standard-encodings"

# 用于区分标量与多行命令的简单正则表达式（不是唯一的条件）
SQL_SCALAR_REGEX = r"\A(SELECT(?!\s+DISTINCT\(?))?\s*\w*\("

# 配置保存期间要忽略的选项/开关值
IGNORE_SAVE_OPTIONS = ("saveConfig",)

# 本地主机的IP地址
LOCALHOST = "127.0.0.1"

# Tor使用的默认SOCKS端口
DEFAULT_TOR_SOCKS_PORTS = (9050, 9150)

# Tor使用的默认HTTP端口
DEFAULT_TOR_HTTP_PORTS = (8123, 8118)

# 页面文本内容的比例低于20%
LOW_TEXT_PERCENT = 20

# 这些MySQL关键字不能 (alone) 出现在查询版本的注释表单中（/* !...*/）
# 因为它们会被当作内置函数，而不是一个标识符
# Reference: http://dev.mysql.com/doc/refman/5.1/en/function-resolution.html
# 要在表达式中使用名称作为函数调用，名称和下一个(括号字符之间不能有空格 。
# 相反，要使用函数名作为标识符，不能立即用括号括起来。
IGNORE_SPACE_AFFECTED_KEYWORDS = ("CAST", "COUNT", "EXTRACT", "GROUP_CONCAT", "MAX", "MID", "MIN", "SESSION_USER", "SUBSTR", "SUBSTRING", "SUM", "SYSTEM_USER", "TRIM")

# 在getValue()中期望使用大写的关键字
GET_VALUE_UPPERCASE_KEYWORDS = ("SELECT", "FROM", "WHERE", "DISTINCT", "COUNT")

# 法律免责声明
LEGAL_DISCLAIMER = " 天天向上"

# 如果反射错误值大于20，关闭反射去除机制以提高系统速度)
REFLECTIVE_MISS_THRESHOLD = 20

# 用于提取HTML标题的正则表达式
HTML_TITLE_REGEX = "<title>(?P<result>[^<]+)</title>"

# 用于WordPress哈希破解程序中Base64转换的表
ITOA64 = "./0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"

PICKLE_REDUCE_WHITELIST = (types.BooleanType, types.DictType, types.FloatType, types.IntType, types.ListType, types.LongType, types.NoneType, types.StringType, types.TupleType, types.UnicodeType, types.XRangeType, type(AttribDict()), type(set()))

# 用于快速区分用户是否提供了污染参数值的字符
DUMMY_SQL_INJECTION_CHARS = ";()'"

# 简单检查虚拟用户
DUMMY_USER_INJECTION = r"(?i)[^\w](AND|OR)\s+[^\s]+[=><]|\bUNION\b.+\bSELECT\b|\bSELECT\b.+\bFROM\b|\b(CONCAT|information_schema|SLEEP|DELAY)\b"

# 爬虫跳过的扩展名
CRAWL_EXCLUDE_EXTENSIONS = ("3ds", "3g2", "3gp", "7z", "DS_Store", "a", "aac", "adp", "ai", "aif", "aiff", "apk", "ar", "asf", "au", "avi", "bak", "bin", "bk", "bmp", "btif", "bz2", "cab", "caf", "cgm", "cmx", "cpio", "cr2", "dat", "deb", "djvu", "dll", "dmg", "dmp", "dng", "doc", "docx", "dot", "dotx", "dra", "dsk", "dts", "dtshd", "dvb", "dwg", "dxf", "ear", "ecelp4800", "ecelp7470", "ecelp9600", "egg", "eol", "eot", "epub", "exe", "f4v", "fbs", "fh", "fla", "flac", "fli", "flv", "fpx", "fst", "fvt", "g3", "gif", "gz", "h261", "h263", "h264", "ico", "ief", "image", "img", "ipa", "iso", "jar", "jpeg", "jpg", "jpgv", "jpm", "jxr", "ktx", "lvp", "lz", "lzma", "lzo", "m3u", "m4a", "m4v", "mar", "mdi", "mid", "mj2", "mka", "mkv", "mmr", "mng", "mov", "movie", "mp3", "mp4", "mp4a", "mpeg", "mpg", "mpga", "mxu", "nef", "npx", "o", "oga", "ogg", "ogv", "otf", "pbm", "pcx", "pdf", "pea", "pgm", "pic", "png", "pnm", "ppm", "pps", "ppt", "pptx", "ps", "psd", "pya", "pyc", "pyo", "pyv", "qt", "rar", "ras", "raw", "rgb", "rip", "rlc", "rz", "s3m", "s7z", "scm", "scpt", "sgi", "shar", "sil", "smv", "so", "sub", "swf", "tar", "tbz2", "tga", "tgz", "tif", "tiff", "tlz", "ts", "ttf", "uvh", "uvi", "uvm", "uvp", "uvs", "uvu", "viv", "vob", "war", "wav", "wax", "wbmp", "wdp", "weba", "webm", "webp", "whl", "wm", "wma", "wmv", "wmx", "woff", "woff2", "wvx", "xbm", "xif", "xls", "xlsx", "xlt", "xm", "xpi", "xpm", "xwd", "xz", "z", "zip", "zipx")

# HTTP头中经常出现的模式包含自定义注入标记字符'*'
PROBLEMATIC_CUSTOM_INJECTION_PATTERNS = r"(;q=[^;']+)|(\*/\*)"

# 检查常用的表是否存在
BRUTE_TABLE_EXISTS_TEMPLATE = "EXISTS(SELECT %d FROM %s)"

# 检查常用的列是否存在
BRUTE_COLUMN_EXISTS_TEMPLATE = "EXISTS(SELECT %s FROM %s)"

# 用于检查IDS/IPS/WAF中存在的Payload(下面类似的语句越多越好)
# Payload used for checking of existence of IDS/IPS/WAF (dummier the better)
IDS_WAF_CHECK_PAYLOAD = "AND 1=1 UNION ALL SELECT 1,NULL,'<script>alert(\"XSS\")</script>',table_name FROM information_schema.tables WHERE 2>1--/**/; EXEC xp_cmdshell('cat ../../../etc/passwd')#"

# shellcodeexec中的数据将被填充随机字符串
SHELLCODEEXEC_RANDOM_STRING_MARKER = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"

# 使用--check-internet检查Internet连接的通用地址
CHECK_INTERNET_ADDRESS = "http://ipinfo.io/"

# 在对checkinternet地址的响应中寻找值
CHECK_INTERNET_VALUE = "IP Address Details"

# 用于激发特定WAF/IPS/IDS行为的代码
WAF_ATTACK_VECTORS = (
    "",  # NIL
    "search=<script>alert(1)</script>",
    "file=../../../../etc/passwd",
    "q=<invalid>foobar",
    "id=1 %s" % IDS_WAF_CHECK_PAYLOAD
)

# 用于字典攻击阶段的状态表示
ROTATING_CHARS = ('\\', '|', '|', '/', '-')

# BigArray对象使用的最大块长度(以字节为单位)(只有最后一个块和缓存的块被保存在内存中)
BIGARRAY_CHUNK_SIZE = 1024 * 1024

# socket预连接的最大数量
SOCKET_PRE_CONNECT_QUEUE_SIZE = 3

# 控制台只显示最后n行
TRIM_STDOUT_DUMP_SIZE = 256

"""
在Linux系统中，标准的I/O提供了三种类型的缓冲。
1、全缓冲：在这种情况下，在填满I/O缓冲区后再进行实际的I/O操作。
对于驻留在磁盘上的文件通常由标准I/O库实施全缓冲。
调用fflush函数冲洗一个流。冲洗意味着将缓冲区的内容写到磁盘上。
2、行缓冲：在这种情况下，当在输入和输出遇到换行符时，标准I/O执行I/O操作。
允许我们一次输出一个字符。涉及一个终端时，通常使用行缓冲。
3、不带缓冲的。标准I/O不对字符进行缓冲处理。
例如：如果标准I/O函数fputs写15个字符到不带缓冲的流上，就会调用write的相关的函数立即写入打开的文件上。

可选缓冲参数指定文件所需的缓冲区大小：
0表示无缓冲
1表示行缓冲
任何其他正值表示使用(大约)该大小的缓冲区。
负缓存意味着使用系统默认值，tty设备通常为行缓冲，对文件进行完全缓冲，如果省略，则使用系统默认值。
"""
# Reference: http://stackoverflow.com/a/3168436
# Reference: https://support.microsoft.com/en-us/kb/899149
DUMP_FILE_BUFFER_SIZE = 1024

# 限制解析响应头的次数
PARSE_HEADERS_LIMIT = 3

# 在ORDER BY技术中使用的步长用于在UNION查询注入中查找正确的列数
ORDER_BY_STEP = 10

# 推断重新验证字符的最大次数（根据需要）
MAX_REVALIDATION_STEPS = 5

# 可用于在提供的命令行中分割参数值的字符（例如，在--tamper中）
PARAMETER_SPLITTING_REGEX = r"[,|;]"

# 描述可能的union char值的正则表达式（例如在-union-char中使用）
# \Z仅匹配字符串末尾    abc\Z  ---->   abc
# \A仅匹配字符串开头    \Aabc  ---->   abc
# \w+ 匹配包括下划线的任何单词字符,等价于'[A-Za-z0-9_]'。(+匹配一次或多次)
UNION_CHAR_REGEX = r"\A\w+\Z"

# 用于在特殊情况下存储原始参数值的属性（例如POST）
UNENCODED_ORIGINAL_VALUE = "original"

# 包含用户名的通用列名（在某些情况下用于哈希破解）
COMMON_USER_COLUMNS = ("login", "user", "username", "user_name", "user_login", "benutzername", "benutzer", "utilisateur", "usager", "consommateur", "utente", "utilizzatore", "usufrutuario", "korisnik", "usuario", "consumidor", "client", "cuser")

# GET/POST值中的默认分隔符
DEFAULT_GET_POST_DELIMITER = '&'

# Cookie值中的默认分隔符
DEFAULT_COOKIE_DELIMITER = ';'

# 当提供--load-cookies选项时，用于强制Cookie到期的Unix时间戳，
FORCE_COOKIE_EXPIRATION_TIME = "9999999999"

# 用于自动创建未处理异常问题的Github OAuth令牌
GITHUB_REPORT_OAUTH_TOKEN = "NTMyNWNkMmZkMzRlMDZmY2JkMmY0MGI4NWI0MzVlM2Q5YmFjYWNhYQ=="

# 跳过非强制的HashDB刷新请求，低于缓存项的阈值
HASHDB_FLUSH_THRESHOLD = 32

# 失败时HashDB刷新尝试的重试次数
HASHDB_FLUSH_RETRIES = 3

# 不成功的HashDB检索尝试的重试次数
HASHDB_RETRIEVE_RETRIES = 3

# 不成功的HashDB结束事务尝试的重试次数
HASHDB_END_TRANSACTION_RETRIES = 3

# 用于对旧的HashDB值的强制弃用的唯一的里程碑值(例如，当改变hash/pickle机制时)
HASHDB_MILESTONE_VALUE = "dPHoJRQYvs"  # python -c 'import random, string; print "".join(random.sample(string.ascii_letters, 10))'

# 警告用户在完整的UNION查询注入中，由于大量页面转储可能会导致延迟
LARGE_OUTPUT_THRESHOLD = 1024 ** 2

# 在巨大的表上，如果每行检索都需要ORDER BY则性能会下降很多（在使用ERROR注入的表转储中最为显着）
SLOW_ORDER_COUNT_THRESHOLD = 10000

# 如果在第一个给定的行数中找不到任何数据, 则放弃哈希识别
HASH_RECOGNITION_QUIT_THRESHOLD = 10000

# 任何单个URL的重定向的最大数量—这是由于cookie引入的状态所需要的
MAX_SINGLE_URL_REDIRECTIONS = 4

# 在假设我们处于循环状态之前，重定向的最大总数（不考虑URL）
MAX_TOTAL_REDIRECTIONS = 10

# Reference: http://www.tcpipguide.com/free/t_DNSLabelsNamesandSyntaxRules.htm
MAX_DNS_LABEL = 63

# 用于DNS技术中名称解析请求的前缀和后缀字符串的字母（不包括不与内容混合的十六进制字符）
DNS_BOUNDARIES_ALPHABET = re.sub("[a-fA-F]", "", string.ascii_letters)

# 用于启发式检查的字母
HEURISTIC_CHECK_ALPHABET = ('"', '\'', ')', '(', ',', '.')

# Minor artistic touch
BANNER = re.sub(r"\[.\]", lambda _: "[\033[01;41m%s\033[01;49m]" % random.sample(HEURISTIC_CHECK_ALPHABET, 1)[0], BANNER)

# 用于虚拟非SQLi（例如XSS）启发式检查测试参数值的字符串
DUMMY_NON_SQLI_CHECK_APPENDIX = "<'\">"

# 用于识别文件包含错误的正则表达式
FI_ERROR_REGEX = "(?i)[^\n]{0,100}(no such file|failed (to )?open)[^\n]{0,100}"

# 在非SQLI启发式检查中使用的前缀和后缀长度
NON_SQLI_CHECK_PREFIX_SUFFIX_LENGTH = 6

# 连接块大小（处理大块响应，以避免MemoryError崩溃 - 例如在完整的UNION注入中的大表转储）
MAX_CONNECTION_CHUNK_SIZE = 10 * 1024 * 1024

# 最大响应总页面大小（如果较大则截断）
MAX_CONNECTION_TOTAL_SIZE = 50 * 1024 * 1024

# 防止MemoryError异常(在应用程序中使用较大的序列时造成的)
MAX_DIFFLIB_SEQUENCE_LENGTH = 10 * 1024 * 1024

# 二分算法中输入(入口)的最大 (多线程) 长度
MAX_BISECTION_LENGTH = 50 * 1024 * 1024

# 标记用于截取大块不必要的内容
LARGE_CHUNK_TRIM_MARKER = "__TRIMMED_CONTENT__"

# 通用SQL注释构造
GENERIC_SQL_COMMENT = "-- [RANDSTR]"

# 返回时间自动调整机制的阈值
VALID_TIME_CHARS_RUN_THRESHOLD = 100

# 仅当表格足够大时才检查空列
CHECK_ZERO_COLUMNS_THRESHOLD = 10

# 对包含以下字符串的信息加粗显示 
BOLD_PATTERNS = ("提供了空参数", "残留字符", "可注入", "' 很容易受到攻击", "不可注入", "不能注入", "测试失败", "测试通过", "实时测试最终结果", "测试显示", "后端DBMS不是", "后端DBMS是", "创建的Github", "被目标服务器阻止", "部署了防火墙", "CAPTCHA")

# 常用的www根目录名称
GENERIC_DOC_ROOT_DIRECTORY_NAMES = ("htdocs", "httpdocs", "public", "wwwroot", "www")

# sqlmap参数的最大长度
MAX_HELP_OPTION_LENGTH = 18

# 最大连接重试次数（以防止递归问题）
MAX_CONNECT_RETRIES = 100

# 用于检测格式错误的字符串
FORMAT_EXCEPTION_STRINGS = ("Type mismatch", "Error converting", "Conversion failed", "String or binary data would be truncated", "Failed to convert", "unable to interpret text value", "Input string was not in a correct format", "System.FormatException", "java.lang.NumberFormatException", "ValueError: invalid literal", "DataTypeMismatchException", "CF_SQL_INTEGER", " for CFSQLTYPE ", "cfqueryparam cfsqltype", "InvalidParamTypeException", "Invalid parameter type", "is not of type numeric", "<cfif Not IsNumeric(", "invalid input syntax for integer", "invalid input syntax for type", "invalid number", "character to number conversion error", "unable to interpret text value", "String was not recognized as a valid", "Convert.ToInt", "cannot be converted to a ", "InvalidDataException")

# 用于提取ASP.NET视图状态值的正则表达式
VIEWSTATE_REGEX = r'(?i)(?P<name>__VIEWSTATE[^"]*)[^>]+value="(?P<result>[^"]+)'

# 用于提取ASP.NET事件验证值的正则表达式
EVENTVALIDATION_REGEX = r'(?i)(?P<name>__EVENTVALIDATION[^"]*)[^>]+value="(?P<result>[^"]+)'

# 在有限输出的完整联合测试中生成的行数（不能太大，以防止payload长度问题）
LIMITED_ROWS_TEST_NUMBER = 15

# 用于bottle服务器的默认适配器
RESTAPI_DEFAULT_ADAPTER = "wsgiref"

# 默认REST-JSON API服务器侦听地址
RESTAPI_DEFAULT_ADDRESS = "127.0.0.1"

# 默认REST-JSON API服务器侦听端口
RESTAPI_DEFAULT_PORT = 8775

# 用于表示无效unicode字符的格式
INVALID_UNICODE_CHAR_FORMAT = r"\x%02x"

# XML POST数据的正则表达式
XML_RECOGNITION_REGEX = r"(?s)\A\s*<[^>]+>(.+>)?\s*\Z"

# 用于检测JSON POST数据的正则表达式
JSON_RECOGNITION_REGEX = r'(?s)\A(\s*\[)*\s*\{.*"[^"]+"\s*:\s*("[^"]+"|\d+).*\}\s*(\]\s*)*\Z'

# 用于检测类似JSON的POST数据的正则表达式
JSON_LIKE_RECOGNITION_REGEX = r"(?s)\A(\s*\[)*\s*\{.*'[^']+'\s*:\s*('[^']+'|\d+).*\}\s*(\]\s*)*\Z"

# 用于检测多部分POST数据的正则表达式
MULTIPART_RECOGNITION_REGEX = r"(?i)Content-Disposition:[^;]+;\s*name="

# 用于检测类似于数组的 POST 数据的正则表达式
ARRAY_LIKE_RECOGNITION_REGEX = r"(\A|%s)(\w+)\[\]=.+%s\2\[\]=" % (DEFAULT_GET_POST_DELIMITER, DEFAULT_GET_POST_DELIMITER)

# 默认POST数据内容类型
DEFAULT_CONTENT_TYPE = "application/x-www-form-urlencoded; charset=utf-8"

# 原始文本POST数据内容类型
PLAIN_TEXT_CONTENT_TYPE = "text/plain; charset=utf-8"

# 检查是否存在 Suhosin (类似) 保护机制时使用的长度
SUHOSIN_MAX_VALUE_LENGTH = 512

# 在可以考虑将其转储到磁盘之前，（二进制）条目的最小大小
MIN_BINARY_DISK_DUMP_SIZE = 100

# Payload的文件名xml文件（按加载顺序）
PAYLOAD_XML_FILES = ("boolean_blind.xml", "error_based.xml", "inline_query.xml", "stacked_queries.xml", "time_blind.xml", "union_query.xml")

# 用于提取表单标签的正则表达式
FORM_SEARCH_REGEX = r"(?si)<form(?!.+<form).+?</form>"

# 在历史文件中保存的最大行数
MAX_HISTORY_LENGTH = 1000

# 编码内容（hex，base64，...）检查所需的最小字段条目长度
MIN_ENCODED_LEN_CHECK = 5

# 必须初始化Metasploit远程会话的超时时间
METASPLOIT_SESSION_TIMEOUT = 120

# Reference: http://www.postgresql.org/docs/9.0/static/catalog-pg-largeobject.html
LOBLKSIZE = 2048

# 用于标记具有关键字名称的变量的后缀
EVALCODE_KEYWORD_SUFFIX = "_KEYWORD"

# Reference: http://www.cookiecentral.com/faq/#3.5
NETSCAPE_FORMAT_HEADER_COOKIES = "# Netscape HTTP Cookie File."

# 中缀用于自动识别携带反 CSRF 令牌的参数
CSRF_TOKEN_PARAMETER_INFIXES = ("csrf", "xsrf")

# 用于强力搜索Web服务器文档根目录的前缀
BRUTE_DOC_ROOT_PREFIXES = {
    OS.LINUX: ("/var/www", "/usr/local/apache", "/usr/local/apache2", "/usr/local/www/apache22", "/usr/local/www/apache24", "/usr/local/httpd", "/var/www/nginx-default", "/srv/www", "/var/www/%TARGET%", "/var/www/vhosts/%TARGET%", "/var/www/virtual/%TARGET%", "/var/www/clients/vhosts/%TARGET%", "/var/www/clients/virtual/%TARGET%"),
    OS.WINDOWS: ("/xampp", "/Program Files/xampp", "/wamp", "/Program Files/wampp", "/apache", "/Program Files/Apache Group/Apache", "/Program Files/Apache Group/Apache2", "/Program Files/Apache Group/Apache2.2", "/Program Files/Apache Group/Apache2.4", "/Inetpub/wwwroot", "/Inetpub/wwwroot/%TARGET%", "/Inetpub/vhosts/%TARGET%")
}

# 用于强力搜索Web服务器文档根目录的后缀
BRUTE_DOC_ROOT_SUFFIXES = ("", "html", "htdocs", "httpdocs", "php", "public", "src", "site", "build", "web", "www", "data", "sites/all", "www/build")

# 用于在使用暴力破解的Web服务器文档根目录中标记目标名称的字符串
BRUTE_DOC_ROOT_TARGET_MARK = "%TARGET%"

# 字符用作kb.chars中的边界（最好较不频繁的字母）
KB_CHARS_BOUNDARY_CHAR = 'q'

# 在kb.chars中使用的频率较低的字母
KB_CHARS_LOW_FREQUENCY_ALPHABET = "zqxjkvbp"

# HTML转储格式中使用的CSS样式
HTML_DUMP_CSS_STYLE = """<style>
table{
    margin:10;
    background-color:#FFFFFF;
    font-family:verdana;
    font-size:12px;
    align:center;
}
thead{
    font-weight:bold;
    background-color:#4F81BD;
    color:#FFFFFF;
}
tr:nth-child(even) {
    background-color: #D3DFEE
}
td{
    font-size:10px;
}
th{
    font-size:10px;
}
</style>"""
