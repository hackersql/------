#!/usr/bin/env python
#coding=utf-8
"""
Copyright (c) 2006-2017 sqlmap developers (http://sqlmap.org/)
See the file 'doc/COPYING' for copying permission
"""

import os
import re
import shlex
import sys
reload(sys)
sys.setdefaultencoding('utf8')

from optparse import OptionError
from optparse import OptionGroup
from optparse import OptionParser
from optparse import SUPPRESS_HELP

from lib.core.common import checkDeprecatedOptions
from lib.core.common import checkSystemEncoding
from lib.core.common import dataToStdout
from lib.core.common import expandMnemonics
from lib.core.common import getUnicode
from lib.core.data import cmdLineOptions
from lib.core.data import conf
from lib.core.data import logger
from lib.core.defaults import defaults
from lib.core.enums import AUTOCOMPLETE_TYPE
from lib.core.exception import SqlmapShellQuitException
from lib.core.exception import SqlmapSyntaxException
from lib.core.settings import BASIC_HELP_ITEMS
from lib.core.settings import DUMMY_URL
from lib.core.settings import IS_WIN
from lib.core.settings import MAX_HELP_OPTION_LENGTH
from lib.core.settings import VERSION_STRING
from lib.core.shell import autoCompletion
from lib.core.shell import clearHistory
from lib.core.shell import loadHistory
from lib.core.shell import saveHistory

def cmdLineParser(argv=None):
    """
    此函数解析命令行参数和参数
    """

    if not argv:
        argv = sys.argv

    checkSystemEncoding()

    # Reference: https://stackoverflow.com/a/4012683 (Note: previously used "...sys.getfilesystemencoding() or UNICODE_ENCODING")
    _ = getUnicode(os.path.basename(argv[0]), encoding=sys.stdin.encoding)

    usage = "%s%s [options]" % ("python " if not IS_WIN else "", \
            "\"%s\"" % _ if " " in _ else _)

    parser = OptionParser(usage=usage)

    try:
        parser.add_option("--hh", dest=u"advancedHelp",
                          action="store_true",
                          help=u"显示高级帮助消息并退出")
        # dest ： 用于保存临时变量，其值可以作为options的属性进行访问。存储的内容就是如-f,-n 等紧挨着的那个参数内容。
        parser.add_option("--version", dest=u"showVersion",
                          action="store_true",
                          help=u"显示程序版本号并退出")
        # type 参数类型
        parser.add_option("-v", dest="verbose", type="int",
                          help=u"详细程度: 0-6 (默认 %d)" % defaults.verbose)

        # 目标选项
        target = OptionGroup(parser, u"目标", u"至少提供下列一个选项作为注入目标")
        #例如：mysql://数据库用户名:数据库密码@数据库ip地址:数据库端口号/数据库名)
        target.add_option("-d", dest="direct",
                          help=u"直接连接数据库\r\n(例如：mysql://USER:PASSWORD@DBMS_IP:DBMS_PORT/DATABASE_NAME)")

        target.add_option("-u", "--url", dest="url", help=u"目标网址(例如:http://www.site.com/vuln.php?id=1)")

        target.add_option("-l", dest="logFile", help=u"从Burp或WebScarab代理日志文件解析目标")

        target.add_option("-x", dest="sitemapUrl", help=u"从远程站点地图（.xml）文件解析目标")

        target.add_option("-m", dest="bulkFile", help=u"扫描文本文件中给出的多个目标")

        target.add_option("-r", dest="requestFile",
                          help=u"从文件加载HTTP请求")

        target.add_option("-g", dest="googleDork",
                          help=u"将Google dork搜索结果作为目标，这个选项使得sqlmap可以通过和搜索引擎通信,"
                               u"通过google dork搜索可能存在sql注入的网站 ,然后sqlmap会提取前100个结果 ,"
                               u"并询问用户是否针对这些目标进行检测 "
                               u"\r\n(例如：python sqlmap.py -g \"inurl:\".php?id=1\"\")")

        target.add_option("-c", dest="configFile",
                          help=u"加载sqlmap.conf文件里面的相关配置")

        # 请求选项
        request = OptionGroup(parser, u"请求", u"该选项指定以何种方式连接到目标URL")

        request.add_option("--method", dest="method",
                           help=u"强制使用指定的HTTP请求方法(例如：GET PUT)")

        request.add_option("--data", dest="data",
                           help=u"以POST方式提交数据")

        request.add_option("--param-del", dest="paramDel",
                           help=u"用于分割参数值的字符")

        request.add_option("--cookie", dest="cookie",
                           help=u"HTTP Cookie header value")

        request.add_option("--cookie-del", dest="cookieDel",
                           help=u"用于分割cookie值的字符")

        request.add_option("--load-cookies", dest="loadCookies",
                           help=u"包含Netscape/wget格式的Cookie的文件")

        request.add_option("--drop-set-cookie", dest="dropSetCookie",
                           action="store_true",
                           help=u"从响应response中忽略Set-Cookie header")

        request.add_option("--user-agent", dest="agent",
                           help=u"自定义修改HTTP请求头中User-Agent值,只有--level等级为3以上设置才会生效")

        request.add_option("--random-agent", dest="randomAgent",
                           action="store_true",
                           help=u"使用随机选择的HTTP User-Agent header值")

        request.add_option("--host", dest="host",
                           help=u"自定义修改HTTP请求头中的Host值,只有在--level值为5的时候设置才会生效")

        request.add_option("--referer", dest="referer",
                           help=u"sqlmap可以在请求中伪造HTTP中的referer,"
                                u"当--level参数设定为3或者3以上的时候会尝试对referer注入。")

        request.add_option("-H", "--header", dest="header",
                           help=u"Extra header (例如: \"X-Forwarded-For: 127.0.0.1\")")

        request.add_option("--headers", dest="headers",
                           help=u"Extra headers (例如: \"Accept-Language: fr\\nETag: 123\")")

        request.add_option("--auth-type", dest="authType",
                           help=u"HTTP认证类型(Basic, Digest, NTLM or PKI)")

        request.add_option("--auth-cred", dest="authCred",
                           help=u"HTTP身份验证凭证(用户名:密码)")

        request.add_option("--auth-file", dest="authFile",
                           help=u"HTTP认证PEM认证/私钥文件")

        request.add_option("--ignore-401", dest="ignore401", action="store_true",
                          help=u"忽略HTTP错误401（未经授权）")

        request.add_option("--ignore-proxy", dest="ignoreProxy", action="store_true",
                           help=u"忽略系统默认代理设置")

        request.add_option("--ignore-redirects", dest="ignoreRedirects", action="store_true",
                          help=u"忽略重定向尝试")

        request.add_option("--ignore-timeouts", dest="ignoreTimeouts", action="store_true",
                          help=u"忽略连接超时")

        request.add_option("--proxy", dest="proxy",
                           help=u"使用代理连接到目标URL")

        request.add_option("--proxy-cred", dest="proxyCred",
                           help=u"代理认证凭证(用户名:密码)")

        request.add_option("--proxy-file", dest="proxyFile",
                           help=u"从文件加载代理列表")

        request.add_option("--tor", dest="tor",
                                  action="store_true",
                                  help=u"使用Tor匿名网络")

        request.add_option("--tor-port", dest="torPort",
                                  help=u"设置tor的端口，如果不是默认端口的话")

        request.add_option("--tor-type", dest="torType",
                                  help=u"设置Tor代理类型(HTTP, SOCKS4 or SOCKS5 (default))")

        request.add_option("--check-tor", dest="checkTor",
                                  action="store_true",
                                  help=u"检查Tor是否可用")

        request.add_option("--delay", dest="delay", type="float",
                           help=u"每个HTTP请求之间的延迟秒数")

        request.add_option("--timeout", dest="timeout", type="float",
                           help=u"设置超时时间，默认%d秒" % defaults.timeout)

        request.add_option("--retries", dest="retries", type="int",
                           help=u"设置连接超时时重试次数，默认%d次" % defaults.retries)

        request.add_option("--randomize", dest="rParam",
                           help=u"随机更改给定参数的值")

        request.add_option("--safe-url", dest="safeUrl",
                           help=u"有的web程序会在多次错误访问后屏蔽所有请求，这样就导致之后所有的测试无法进行，"
                                u"绕过这个策略可以使用--safe-url，每隔一段时间去访问一个正常的页面。")

        request.add_option("--safe-post", dest="safePost",
                           help=u"发送POST数据到一个安全的URL")

        request.add_option("--safe-req", dest="safeReqFile",
                           help=u"从文件加载安全的HTTP请求")

        request.add_option("--safe-freq", dest="safeFreq", type="int",
                           help=u"提供一个安全无错误的连接，在测试URL和安全链接之间交叉访问")

        request.add_option("--skip-urlencode", dest="skipUrlEncode",
                           action="store_true",
                           help=u"根据参数位置，他的值默认将会被URL编码，但是有些时候后端的web服务器不遵守RFC标准，"
                                u"只接受不经过URL编码的值，这时候就需要用--skip-urlencode参数,跳过Payload数据的URL编码")

        request.add_option("--csrf-token", dest="csrfToken",
                           help=u"设置CSRF的token")

        request.add_option("--csrf-url", dest="csrfUrl",
                           help=u"访问URL地址提取anti-CSRF token")

        request.add_option("--force-ssl", dest="forceSSL",
                           action="store_true",
                           help=u"强制使用SSL/HTTPS")

        request.add_option("--hpp", dest="hpp",
                                  action="store_true",
                                  help=u"使用HTTP参数污染方法绕过WAF的检测机制，HTTP参数污染是一种可以绕过WAF/IPS/IDS的方法，这在面对ASP/IIS 或者是ASP.NET/IIS 组合的时候非常有用，如果你怀疑目标使用了某种保护(WAF/IDS/IPS) 那么你可以试试这个选项")

        request.add_option("--eval", dest="evalCode",
                           help=u"发送请求之前，先运行这段python代码，比如下面的hash参数就是id的md5值 "
                                u"(python sqlmap.py -u \"http://www.target.com/vuln.php?id=1&hash=c4ca4238a0b923820dcc509a6f75849b\" "
                                u"--eval = \"import hashlib;hash=hashlib.md5(id).hexdigest()\")")

        # 优化选项
        optimization = OptionGroup(parser, u"优化", u"这些选项可用于优化sqlmap的性能")

        optimization.add_option("-o", dest="optimize",
                                 action="store_true",
                                 help=u"开启所有优化选项")

        optimization.add_option("--predict-output", dest="predictOutput", action="store_true",
                          help=u"预测常见查询输出")

        optimization.add_option("--keep-alive", dest="keepAlive", action="store_true",
                           help=u"使用持久的HTTP(s)连接")

        optimization.add_option("--null-connection", dest="nullConnection", action="store_true",
                          help=u"检索页面长度,排除实际的 HTTP 响应内容")

        optimization.add_option("--threads", dest="threads", type="int",
                           help=u"最大并发HTTP(s)请求数（默认为%d）" % defaults.threads)

        # 注入选项
        injection = OptionGroup(parser, u"注入", u"这些选项可用于指定要测试的参数,提供自定义注入Payload和篡改脚本")

        injection.add_option("-p", dest="testParameter",
                             help=u"手动指定要测试的参数，默认情况下sqlmap会测试所有的GET和POST参数(例如: -p \"id\")")

        injection.add_option("--skip", dest="skip",
                             help=u"跳过你不想进行注入测试的参数")

        injection.add_option("--skip-static", dest="skipStatic", action="store_true",
                             help=u"跳过那些不是动态的测试参数，对静态参数进行注入测试是徒劳的")

        injection.add_option("--param-exclude", dest="paramExclude",
                           help=u"使用正则表达式来排除不需要测试的参数 (例如:\"ses\")")

        injection.add_option("--dbms", dest="dbms",
                             help=u"指定后端的数据库类型（如mysql，oracle等）")

        injection.add_option("--dbms-cred", dest="dbmsCred",
                            help=u"数据库认证凭证(user:password)")

        injection.add_option("--os", dest="os",
                             help=u"手动指定后端DBMS操作系统(Windows，linux)")

        injection.add_option("--invalid-bignum", dest="invalidBignum",
                             action="store_true",
                             help=u"指定无效的大数字id=13,sqlmap会变成id=-13来报错,你也可以指定比如id=9999999来报错")

        injection.add_option("--invalid-logical", dest="invalidLogical",
                             action="store_true",
                             help=u"指定无效的逻辑,可以指定id=13把原来的id=-13的报错改成id=13 AND 18=19")

        injection.add_option("--invalid-string", dest="invalidString",
                             action="store_true",
                             help=u"使用随机字符串无效值来给参数赋值")

        injection.add_option("--no-cast", dest="noCast",
                             action="store_true",
                             help=u"关闭payload构造机制")

        injection.add_option("--no-escape", dest="noEscape",
                             action="store_true",
                             help=u"关闭字符串转义机制")

        injection.add_option("--prefix", dest="prefix",
                             help=u"设置注入的前缀，比如单引号注入点，就设置前缀为单引号")
        """
        注入payload
        参数：--prefix, --suffix
        在有些环境中，需要在注入的payload的前面或者后面加一些字符，来保证payload的正常执行。
        例如，代码中是这样调用数据库的：
        $query = "SELECT * FROM users WHERE id=(’". $_GET[’id’]."’) LIMIT 0, 1";
        这时你就需要--prefix和--suffix参数了：
        python sqlmap.py -u "http://xxx.com/sqlmap/mysql/get_str_brackets.php?id=1" -p id --prefix "’)" --suffix "AND (’abc’=’abc"
        这样执行的SQL语句变成：
        $query = "SELECT * FROM users WHERE id=('1') <PAYLOAD> AND ('abc'='abc') LIMIT 0, 1";
        """
        injection.add_option("--suffix", dest="suffix",
                             help=u"设置注入payload的后缀")

        injection.add_option("--tamper", dest="tamper",
                             help=u"使用tamper脚本修改请求从而逃避WAF的规则检测")

        # 探测选项
        detection = OptionGroup(parser, u"探测", u"这些选项可用于指定检测目标的等级")

        detection.add_option("--level", dest="level", type="int",
                             help=u"探测等级(1-5,默认%d级)" % defaults.level)

        detection.add_option("--risk", dest="risk", type="int",
                             help=u"风险等级(1-3, 默认%d级)" % defaults.risk)

        detection.add_option("--string", dest="string",
                             help=u"设置原始页面与条件为真情况下页面中都存在的字符串，而错误页面中不存在，如果页面返回这个字符串，说明我们的注入判断语句是正确的")

        detection.add_option("--not-string", dest="notString",
                             help=u"设置一段在原始页面与真条件页面中都不存在的字符串，而错误页面中存在的字符串")

        detection.add_option("--regexp", dest="regexp",
                             help=u"利用正则匹配页面返回内容，如果存在匹配字符串，则可能存在注入点")

        detection.add_option("--code", dest="code", type="int",
                             help=u"用HTTP响应码来判断注入语句是否正确，"
                                  u"例如，响应200的时候为真，响应401的时候为假，可以添加参数--code=200")
        detection.add_option("--text-only", dest="textOnly",
                             action="store_true",
                             help=u"基于文本内容比较页面,如果在HTTP响应中存在大量脚本、或者是各种内嵌的东西 ,可以通过使用--text-only来进行筛选只显示文本内容")

        detection.add_option("--titles", dest="titles",
                             action="store_true",
                             help=u"基于标题比较页面,如果使用者知道正常、错误响应之间的HTML标题的区别 (例如Welcom为正常，Forbidden为错误)那么他可以通过使用--titles来比较HTML标题的不同来提示sqlmap是否能够注入")

        # 注入技术
        techniques = OptionGroup(parser, u"注入技术", u"这些选项可用于指定具体的SQL注入技术的测试")

        techniques.add_option("--technique", dest="tech",
                              help=u"要使用的SQL注入技术(默认 \"%s\")" % defaults.tech)

        techniques.add_option("--time-sec", dest="timeSec",
                              type="int",
                              help=u"设定延迟注入的时间，"
                                   u"当使用基于时间的盲注时，时刻使用--time-sec参数设定延时时间，默认是%d秒" % defaults.timeSec)

        techniques.add_option("--union-cols", dest="uCols",
                              help=u"设定SQL注入时UNION查询字段数范围，如：12-16，是测试12-16个字段数")

        techniques.add_option("--union-char", dest="uChar",
                              help=u"设定UNION查询使用的字符，用于爆破字段数目的字符,默认使用NULL字符，但是有些情况下会造成页面返回失败，而一个随机整数是成功的，这时你可以用--union-char指定UNION查询的字符")

        techniques.add_option("--union-from", dest="uFrom",
                              help=u"在某些UNION查询SQL注入情况下，需要在FROM子句中强制使用有效且可访问的表名。 例如，Microsoft Access需要使用这样的表。 如果不提供一个UNION查询，SQL注入将无法正确执行(例如 --union-from = users)")

        techniques.add_option("--dns-domain", dest="dnsDomain",
                              help=u"用于DNS渗透攻击的域名")

        techniques.add_option("--second-order", dest="secondOrder",
                             help=u"二阶注入是攻击者首先提交恶意的请求，在数据库保存成功后 再提交另外一个用于检索之前的恶意请求的请求，如果攻击成功，那么响应会在第二次响应中返回结果，使用这个选项的时候后面跟着的是显示结果页面的URL。有些时候注入点输入的数据返回结果的时候并不是当前的页面，而是另外的一个页面，这时候就需要你指定到哪个页面来获取响应结果判断真假。--second-order后面跟一个判断页面的URL地址。")

        # 指纹识别选项
        fingerprint = OptionGroup(parser, u"指纹识别")

        fingerprint.add_option("-f", "--fingerprint", dest="extensiveFp",
                               action="store_true",
                               help=u"利用数据库特有的指纹信息识别其数据库类型和版本号")

        # 枚举选项
        enumeration = OptionGroup(parser, u"检索数据", u"这些选项可用于枚举表中包含的DBMS信息结构和数据。此外，您可以运行自己的SQL语句")

        enumeration.add_option("-a", "--all", dest="getAll",
                               action="store_true", help=u"检索所有内容")

        enumeration.add_option("-b", "--banner", dest="getBanner",
                               action="store_true", help=u"检索数据库管理系统的标识（如mysql，oracle）")

        enumeration.add_option("--current-user", dest="getCurrentUser",
                               action="store_true",
                               help=u"检索当前连接数据库的用户CURRENT_USER()")

        enumeration.add_option("--current-db", dest="getCurrentDb",
                               action="store_true",
                               help=u"检索当前连接的数据库DATABASE()")

        enumeration.add_option("--hostname", dest="getHostname",
                               action="store_true",
                               help=u"检索服务器的主机名@@HOSTNAME")

        enumeration.add_option("--is-dba", dest="isDba",
                               action="store_true",
                               help=u"判断当前用户是否为管理，是的话会返回True")

        enumeration.add_option("--users", dest="getUsers", action="store_true",
                               help=u"枚举数据库用户，"
                                    u"当前用户有权限读取包含所有用户的表的权限时，就可以列出所有管理用户")

        enumeration.add_option("--passwords", dest="getPasswordHashes",
                               action="store_true",
                               help=u"枚举数据库用户密码的哈希值并尝试破解")

        enumeration.add_option("--privileges", dest="getPrivileges",
                               action="store_true",
                               help=u"枚举数据库用户的权限")

        enumeration.add_option("--roles", dest="getRoles",
                               action="store_true",
                               help=u"枚举数据库用户的角色")

        enumeration.add_option("--dbs", dest="getDbs", action="store_true",
                               help=u"列出所有的数据库")

        enumeration.add_option("--tables", dest="getTables", action="store_true",
                               help=u"列举数据库中的所有表")

        enumeration.add_option("--columns", dest="getColumns", action="store_true",
                               help=u"列举数据库表中的字段，同时也会列出字段的数据类型")

        enumeration.add_option("--schema", dest="getSchema", action="store_true",
                               help=u"列举数据库系统的架构，包含所有的数据库，表和字段，以及各自的类型")

        enumeration.add_option("--count", dest="getCount", action="store_true",
                               help=u"检索表的条目数")

        enumeration.add_option("--dump", dest="dumpTable", action="store_true",
                               help=u"获取整个表的数据")

        enumeration.add_option("--dump-all", dest="dumpAll", action="store_true",
                               help=u"获取所有数据库表中的内容")

        enumeration.add_option("--search", dest="search", action="store_true",
                               help=u"搜索字段，表，数据库，配合下面的-D,-C,-T")

        enumeration.add_option("--comments", dest="getComments", action="store_true",
                               help=u"枚举数据库的注释")

        enumeration.add_option("-D", dest="db",
                               help=u"要进行枚举的数据库名")

        enumeration.add_option("-T", dest="tbl",
                               help=u"要进行枚举的数据库表")

        enumeration.add_option("-C", dest="col",
                               help=u"要进行枚举的数据库字段")

        enumeration.add_option("-X", dest="excludeCol",
                               help=u"指定不枚举那个字段")

        enumeration.add_option("-U", dest="user",
                               help=u"枚举数据库用户")

        enumeration.add_option("--exclude-sysdbs", dest="excludeSysDbs",
                               action="store_true",
                               help=u"枚举表时排除系统数据库")

        enumeration.add_option("--pivot-column", dest="pivotColumn",
                               help=u"行转列名称")

        enumeration.add_option("--where", dest="dumpWhere",
                               help=u"使用WHERE条件查询/获取指定表中的内容")

        enumeration.add_option("--start", dest="limitStart", type="int",
                               help=u"指定开始从第几行开始输出，如--start=3，前两行就不输出了")

        enumeration.add_option("--stop", dest="limitStop", type="int",
                               help=u"指定从第几行开始停止输出")

        enumeration.add_option("--first", dest="firstChar", type="int",
                               help=u"指定从第几个字符之后开始输出")

        enumeration.add_option("--last", dest="lastChar", type="int",
                               help=u"指定输出到第几个字符后停止输出，盲注才有效，亲测，跟上面的配合指定范围，"
                                    u"如 ：--first 3 --last 5  只输出3到5位置的字符")

        enumeration.add_option("--sql-query", dest="query",
                               help=u"指定执行我们的sql语句")

        enumeration.add_option("--sql-shell", dest="sqlShell",
                               action="store_true",
                               help=u"返回一个sql的shell")

        enumeration.add_option("--sql-file", dest="sqlFile",
                               help=u"从文件中读取执行sql语句")

        # 爆破选项
        brute = OptionGroup(parser, u"爆破", u"这些选项可用于执行爆破检查")

        brute.add_option("--common-tables", dest="commonTables", action="store_true",
                               help=u"检测常见的表名，暴力破解表名")

        brute.add_option("--common-columns", dest="commonColumns", action="store_true",
                               help=u"检测常见的字段名，暴力破解列名")

        # 用户自定义的功能选项
        udf = OptionGroup(parser, u"使用用户自定义的功能进行注入")

        udf.add_option("--udf-inject", dest="udfInject", action="store_true",
                       help=u"注入用户自定义的功能")

        udf.add_option("--shared-lib", dest="shLib",
                       help=u"共享库的本地路径")

        # 文件系统访问"", "这些选项可用于访问基础文件系统的后端数据库管理系统"
        filesystem = OptionGroup(parser, u"文件系统访问", u"这些选项可用于访问基础文件系统的后端DBMS")

        filesystem.add_option("--file-read", dest="rFile",
                              help=u"从数据库服务器中读取文件")

        filesystem.add_option("--file-write", dest="wFile",
                              help=u"把文件写入/上传到数据库服务器中")

        filesystem.add_option("--file-dest", dest="dFile",
                              help=u"写入数据库服务器的绝对路径")

        # Takeover options
        takeover = OptionGroup(parser, u"操作系统访问", u"这些选项可用于访问基础操作系统的后端DBMS")

        takeover.add_option("--os-cmd", dest="osCmd",
                            help=u"执行操作系统命令")

        takeover.add_option("--os-shell", dest="osShell",
                            action="store_true",
                            help=u"返回一个shell")

        takeover.add_option("--os-pwn", dest="osPwn",
                            action="store_true",
                            help=u"调出一个带外shell/meterpreter/VNC")

        takeover.add_option("--os-smbrelay", dest="osSmb",
                            action="store_true",
                            help=u"一键调出OOB shell/meterpreter/VNC")

        takeover.add_option("--os-bof", dest="osBof",
                            action="store_true",
                            help=u"存储过程缓冲区溢出利用")

        takeover.add_option("--priv-esc", dest="privEsc",
                            action="store_true",
                            help=u"对当前连接数据库进程的用户进行权限提升")

        takeover.add_option("--msf-path", dest="msfPath",
                            help=u"安装Metasploit Framework的本地路径")

        takeover.add_option("--tmp-path", dest="tmpPath",
                            help=u"临时文件目录的远程绝对路径")

        # Windows registry options
        windows = OptionGroup(parser, u"Windows注册表访问", u"这些选项可用于访问后端数据库管理系统Windows注册表")

        windows.add_option("--reg-read", dest="regRead",
                            action="store_true",
                            help=u"读取Windows注册表项值")

        windows.add_option("--reg-add", dest="regAdd",
                            action="store_true",
                            help=u"写入注册表值")

        windows.add_option("--reg-del", dest="regDel",
                            action="store_true",
                            help=u"删除注册表值")

        windows.add_option("--reg-key", dest="regKey",
                            help=u"指定键，配合之前三个参数使用，"
                                 u"例如：python sqlmap.py -u http://192.168.136.129/sqlmap/pgsql/get_int.aspx?id=1"
                                 u" --reg-add --reg-key=\"HKEY_LOCAL_MACHINE\SOFTWARE\sqlmap\" --reg-value=Test" \
                                u" --reg-type=REG_SZ --reg-data=1")

        windows.add_option("--reg-value", dest="regVal",
                            help=u"指定键值")

        windows.add_option("--reg-data", dest="regData",
                            help=u"指定键值的数据")

        windows.add_option("--reg-type", dest="regType",
                            help=u"指定键值的类型")

        # 常用选项
        general = OptionGroup(parser, u"通用", u"一些常用选项")

        general.add_option("-s", dest="sessionFile",
                            help=u"从（.sqlite）文件中读取session会话")

        general.add_option("-t", dest="trafficFile",
                            help=u"保存HTTP(S)日志，这个参数需要跟一个文本文件，sqlmap会把HTTP(S)请求与响应的日志保存到那里")

        general.add_option("--batch", dest="batch",
                            action="store_true",
                            help=u"非交互模式，用此参数，不需要用户输入，将会使用sqlmap提示的默认值一直运行下去")

        general.add_option("--binary-fields", dest="binaryFields",
                          help=u"Result fields having binary values (例如： \"digest\")")

        general.add_option("--charset", dest="charset",
                            help=u"强制指定字符编码（如：--charset=GBK）")

        general.add_option("--check-internet", dest="checkInternet",
                            action="store_true",
                            help=u"访问\"http://ipinfo.io/\"确认是否连接到互联网")

        general.add_option("--crawl", dest="crawlDepth", type="int",
                            help=u"爬行网站URL，sqlmap可以收集潜在的可能存在漏洞的连接，后面跟的参数是爬行的深度--batch --crawl=3")

        general.add_option("--crawl-exclude", dest="crawlExclude",
                           help=u"使用正则表达式排除网页中我们不想抓取的内容 (例如我们不想爬行url中包含logout的页面，可以这样写--crawl-exclude=logout)")

        general.add_option("--csv-del", dest="csvDel",
                                  help=u"当保存为CSV格式时（--dump-format=CSV），需要一个分隔符(默认是逗号： \"%s\")，"
                                       u"用户也可以改为别的,如分号：--csv-del=\";\" " % defaults.csvDel)

        general.add_option("--dump-format", dest="dumpFormat",
                                  help=u"输出数据的格式（CSV，HTML或SQLITE）默认输出CSV格式")

        general.add_option("--eta", dest="eta",
                            action="store_true",
                            help=u"计算注入数据的剩余时间，sqlmap先输出长度，预计完成时间，显示百分比，输出字符"
                                 u"17% [========>                  ] 11/64  ETA 00:19")

        general.add_option("--flush-session", dest="flushSession",
                            action="store_true",
                            help=u"刷新session文件，如果不想用之前缓存这个目标的session文件，可以使用这个参数。 "
                                 u"会清空之前的session，重新测试该目标。")

        general.add_option("--forms", dest="forms",
                                  action="store_true",
                                  help=u"在目标网址上解析和测试表单，如果你想通过form表单来测试SQL注入或者是弱密码(名字加密码) ，你可以通过使用-r把请求保存在文件中进行测试 或者--data发送POST数据 或者让sqlmap自动选择个选项对HTML响应中的<;form>;或者是<;input>;这样的标签进行测试，通过给sqlmap提供目标地址参数-u以及使用--form参数，它会自动请求对应的目标地址并且对form表单的输入进行测试")

        general.add_option("--fresh-queries", dest="freshQueries",
                            action="store_true",
                            help=u"忽略存储在会话文件中的查询结果")

        general.add_option("--har", dest="harFile",
                           help=u"将所有HTTP流量记录到HAR文件中")

        general.add_option("--hex", dest="hexConvert",
                            action="store_true",
                            help=u"使用DBMS十六进制功能进行数据检索，很多情况下你检索的数据可能是非ASCII码的， 解决这个问题的一个办法是使用DBMS十六进制功能。 在这个开关打开的情况下，数据在被检索之前被编码为十六进制形式，然后被编码为原始形式。")

        general.add_option("--output-dir", dest="outputDir",
                            action="store",
                            help=u"自定义输出目录路径")

        general.add_option("--parse-errors", dest="parseErrors",
                                  action="store_true",
                                  help=u"从响应中解析并显示DBMS错误消息")

        general.add_option("--save", dest="saveConfig",
                            help=u"将选项保存到配置文件中INI")

        general.add_option("--scope", dest="scope",
                           help=u"利用正则表达式从提供的代理日志中过滤目标")

        general.add_option("--test-filter", dest="testFilter",
                           help=u"通过Payload和/或标题选择测试 (例如:ROW)")

        general.add_option("--test-skip", dest="testSkip",
                           help=u"跳过Payload和/或标题测试 (例如:BENCHMARK)")

        general.add_option("--update", dest="updateAll",
                            action="store_true",
                            help=u"更新sqlmap")

        # 杂项
        miscellaneous = OptionGroup(parser, u"解忧杂货铺")

        miscellaneous.add_option("-z", dest="mnemonics",
                               help=u"使用简短的助记符 (例如: \"flu,bat,ban,tec=EU\")")

        miscellaneous.add_option("--alert", dest="alert",
                                  help=u"发现SQL注入时运行主机操作系统命令")

        miscellaneous.add_option("--answers", dest="answers",
                                  help=u"设置问题的答案，在使用--batch的时候可以通过使用--answers来指定某个回答所需要的答案，如果是多个的话 可以通过使用,来进行分隔 (例如: \"quit=N,follow=N\")")

        miscellaneous.add_option("--beep", dest="beep", action="store_true",
                                  help=u"检测到注入点时发出蜂鸣声提示")

        miscellaneous.add_option("--cleanup", dest="cleanup",
                                  action="store_true",
                                  help=u"清除sqlmap注入时产生的udf与表")

        miscellaneous.add_option("--dependencies", dest="dependencies",
                                  action="store_true",
                                  help=u"检查sqlmap是否缺少第三方库，sqlmap在某些特定的情况下需要用到第三方的库 (例如 -d --os-pwn用到的icmpsh 通道 --auth-type 用到的NTLM HTTP认证类型) 在这些情况下都会有警告，建议使用--dependencies来进行检查")

        miscellaneous.add_option("--disable-coloring", dest="disableColoring",
                                  action="store_true",
                                  help=u"禁用控制台输出着色")

        miscellaneous.add_option("--gpage", dest="googlePage", type="int",
                                  help=u"默认sqlmap使用前100个URL地址作为注入测试，结合此选项，可以对指定页码的URL测试")

        miscellaneous.add_option("--identify-waf", dest="identifyWaf",
                                  action="store_true",
                                  help=u"对WAF/IPS/IDS保护进行全面测试")

        miscellaneous.add_option("--mobile", dest="mobile",
                                  action="store_true",
                                  help=u"通过HTTP User-Agent header模拟智能手机,"
                                       u"有时服务端只接收移动端的访问，此时可以设定一个手机的User-Agent来模仿手机登陆")

        miscellaneous.add_option("--offline", dest="offline",
                                  action="store_true",
                                  help=u"离线模式工作(仅使用会话数据)")

        miscellaneous.add_option("--purge-output", dest="purgeOutput",
                                  action="store_true",
                                  help=u"从输出目录中安全删除所有内容,有时需要删除结果文件，而不被恢复，原有文件将会被随机的一些文件覆盖")

        miscellaneous.add_option("--skip-waf", dest="skipWaf",
                                  action="store_true",
                                  help=u"跳过启发式检测WAF/IPS/IDS保护")

        miscellaneous.add_option("--smart", dest="smart",
                                  action="store_true",
                                  help=u"启发式判断注入,有时对目标非常多的URL进行测试，为节省时间，只对能够快速判断为注入的报错点进行注入")

        miscellaneous.add_option("--sqlmap-shell", dest="sqlmapShell", action="store_true",
                                  help=u"交互式sqlmap shell")

        miscellaneous.add_option("--tmp-dir", dest="tmpDir",
                                  help=u"用于存储临时文件的本地目录")

        miscellaneous.add_option("--web-root", dest="webRoot",
                                  help=u"Web服务器文件根目录(例如 \"/var/www\")")

        miscellaneous.add_option("--wizard", dest="wizard",
                                  action="store_true",
                                  help=u"简单的向导界面，用于初级用户")

        # Hidden and/or experimental options
        parser.add_option("--dummy", dest="dummy", action="store_true",
                          help=SUPPRESS_HELP)

        parser.add_option("--murphy-rate", dest="murphyRate", type="int",
                          help=SUPPRESS_HELP)

        parser.add_option("--disable-precon", dest="disablePrecon", action="store_true",
                          help=SUPPRESS_HELP)

        parser.add_option("--disable-stats", dest="disableStats", action="store_true",
                          help=SUPPRESS_HELP)

        parser.add_option("--profile", dest="profile", action="store_true",
                          help=SUPPRESS_HELP)

        parser.add_option("--force-dns", dest="forceDns", action="store_true",
                          help=SUPPRESS_HELP)

        parser.add_option("--force-threads", dest="forceThreads", action="store_true",
                          help=SUPPRESS_HELP)

        parser.add_option("--smoke-test", dest="smokeTest", action="store_true",
                          help=SUPPRESS_HELP)

        parser.add_option("--live-test", dest="liveTest", action="store_true",
                          help=SUPPRESS_HELP)

        parser.add_option("--stop-fail", dest="stopFail", action="store_true",
                          help=SUPPRESS_HELP)

        parser.add_option("--run-case", dest="runCase", help=SUPPRESS_HELP)

        # API选项
        parser.add_option("--api", dest="api", action="store_true",
                          help=SUPPRESS_HELP)

        parser.add_option("--taskid", dest="taskid", help=SUPPRESS_HELP)

        parser.add_option("--database", dest="database", help=SUPPRESS_HELP)

        parser.add_option_group(target)
        parser.add_option_group(request)
        parser.add_option_group(optimization)
        parser.add_option_group(injection)
        parser.add_option_group(detection)
        parser.add_option_group(techniques)
        parser.add_option_group(fingerprint)
        parser.add_option_group(enumeration)
        parser.add_option_group(brute)
        parser.add_option_group(udf)
        parser.add_option_group(filesystem)
        parser.add_option_group(takeover)
        parser.add_option_group(windows)
        parser.add_option_group(general)
        parser.add_option_group(miscellaneous)

        # Dirty hack可以显示更长的选项，而不会分成两行
        def _(self, *args):
            retVal = parser.formatter._format_option_strings(*args)
            # sqlmap参数的最大长度
            # MAX_HELP_OPTION_LENGTH = 18
            if len(retVal) > MAX_HELP_OPTION_LENGTH:
                retVal = ("%%.%ds.." % (MAX_HELP_OPTION_LENGTH - parser.formatter.indent_increment)) % retVal
            return retVal

        parser.formatter._format_option_strings = parser.formatter.format_option_strings
        parser.formatter.format_option_strings = type(parser.formatter.format_option_strings)(_, parser, type(parser))

        # Dirty hack for making a short option '-hh'简短选项
        option = parser.get_option("--hh")
        option._short_opts = ["-hh"]
        option._long_opts = []

        # Dirty hack for inherent help message of switch '-h'固有的帮助信息
        option = parser.get_option("-h")
        option.help = option.help.capitalize().replace("此帮助", "基本的帮助")

        _ = []
        prompt = False
        advancedHelp = True
        extraHeaders = []

        # Reference: https://stackoverflow.com/a/4012683 (Note: previously used "...sys.getfilesystemencoding() or UNICODE_ENCODING")
        for arg in argv:
            _.append(getUnicode(arg, encoding=sys.stdin.encoding))

        argv = _
        checkDeprecatedOptions(argv)

        prompt = "--sqlmap-shell" in argv

        if prompt:
            parser.usage = ""
            cmdLineOptions.sqlmapShell = True

            _ = ["x", "q", "exit", "quit", "clear"]

            for option in parser.option_list:
                _.extend(option._long_opts)
                _.extend(option._short_opts)

            for group in parser.option_groups:
                for option in group.option_list:
                    _.extend(option._long_opts)
                    _.extend(option._short_opts)

            autoCompletion(AUTOCOMPLETE_TYPE.SQLMAP, commands=_)

            while True:
                command = None

                try:
                    command = raw_input("sqlmap-shell> ").strip()
                    command = getUnicode(command, encoding=sys.stdin.encoding)
                except (KeyboardInterrupt, EOFError):
                    print
                    raise SqlmapShellQuitException

                if not command:
                    continue
                elif command.lower() == "clear":
                    clearHistory()
                    dataToStdout(u"[i] 清除历史记录\n")
                    saveHistory(AUTOCOMPLETE_TYPE.SQLMAP)
                elif command.lower() in ("x", "q", "exit", "quit"):
                    raise SqlmapShellQuitException
                elif command[0] != '-':
                    dataToStdout(u"[!] 提供无效选项\n")
                    dataToStdout(u"[i] 正确的例子: '-u http://www.site.com/vuln.php?id=1 --banner'\n")
                else:
                    saveHistory(AUTOCOMPLETE_TYPE.SQLMAP)
                    loadHistory(AUTOCOMPLETE_TYPE.SQLMAP)
                    break

            try:
                for arg in shlex.split(command):
                    argv.append(getUnicode(arg, encoding=sys.stdin.encoding))
            except ValueError, ex:
                raise SqlmapSyntaxException, u"命令行解析时出错 ('%s')" % ex.message

        for i in xrange(len(argv)):
            if argv[i] == "-hh":
                argv[i] = "-h"
            elif len(argv[i]) > 1 and all(ord(_) in xrange(0x2018, 0x2020) for _ in ((argv[i].split('=', 1)[-1].strip() or ' ')[0], argv[i][-1])):
                dataToStdout("[!] 从互联网上复制粘贴非法(非控制台)引号字符是非法的(%s)\n" % argv[i])
                raise SystemExit
            elif len(argv[i]) > 1 and u"\uff0c" in argv[i].split('=', 1)[-1]:
                dataToStdout("[!] 从互联网复制粘贴非法(非控制台)逗号字符是非法的(%s)\n" % argv[i])
                raise SystemExit
            elif re.search(r"\A-\w=.+", argv[i]):
                dataToStdout("[!] 检测到潜在的错误(非法的 '=') 短选项 ('%s')\n" % argv[i])
                raise SystemExit
            elif argv[i] == "-H":
                if i + 1 < len(argv):
                    extraHeaders.append(argv[i + 1])
            elif re.match(r"\A\d+!\Z", argv[i]) and argv[max(0, i - 1)] == "--threads" or re.match(r"\A--threads.+\d+!\Z", argv[i]):
                argv[i] = argv[i][:-1]
                conf.skipThreadCheck = True
            elif argv[i] == "--version":
                print VERSION_STRING.split('/')[-1]
                raise SystemExit
            elif argv[i] in ("-h", "--help"):
                advancedHelp = False
                for group in parser.option_groups[:]:
                    found = False
                    for option in group.option_list:
                        if option.dest not in BASIC_HELP_ITEMS:
                            option.help = SUPPRESS_HELP
                        else:
                            found = True
                    if not found:
                        parser.option_groups.remove(group)

        for verbosity in (_ for _ in argv if re.search(r"\A\-v+\Z", _)):
            try:
                if argv.index(verbosity) == len(argv) - 1 or not argv[argv.index(verbosity) + 1].isdigit():
                    conf.verbose = verbosity.count('v') + 1
                    del argv[argv.index(verbosity)]
            except (IndexError, ValueError):
                pass

        try:
            (args, _) = parser.parse_args(argv)
        except UnicodeEncodeError, ex:
            dataToStdout("\n[!] %s\n" % ex.object.encode("unicode-escape"))
            raise SystemExit
        except SystemExit:
            if "-h" in argv and not advancedHelp:
                dataToStdout(u"\n[!] 运行'-hh'选项查看完整的参数列表\n")
            raise

        if extraHeaders:
            if not args.headers:
                args.headers = ""
            delimiter = "\\n" if "\\n" in args.headers else "\n"
            args.headers += delimiter + delimiter.join(extraHeaders)

        # 展开给定的助记符选项 (例如: -z "ign,flu,bat")
        for i in xrange(len(argv) - 1):
            if argv[i] == "-z":
                expandMnemonics(argv[i + 1], parser, args)

        if args.dummy:
            args.url = args.url or DUMMY_URL

        if not any((args.direct, args.url, args.logFile, args.bulkFile, args.googleDork, args.configFile, \
            args.requestFile, args.updateAll, args.smokeTest, args.liveTest, args.wizard, args.dependencies, \
            args.purgeOutput, args.sitemapUrl)):
            errMsg = u"缺少一个强制性选项 (-d, -u, -l, -m, -r, -g, -c, -x, --wizard, --update, --purge-output or --dependencies), "
            errMsg += u"使用-h或-hh选项来查看一些基本操作或高级帮助\n"
            parser.error(errMsg)

        return args

    except (OptionError, TypeError), e:
        parser.error(e)

    except SystemExit:
        # 防止Windows虚拟双击
        if IS_WIN:
            dataToStdout(u"\n按Enter继续...")
            raw_input()
        raise

    debugMsg = u"解析命令行"
    logger.debug(debugMsg)
