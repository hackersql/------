        ___
       __H__
 ___ ___[)]_____ ___ ___  {1.1.7.21#dev}
|_ -| . ["]     | .'| . |
|___|_  [,]_|_|_|__,|  _|
      |_|V          |_|   欢迎使用sqlmap中文版

Usage: python sqlmap.py [options]

Options:
  -h, --help            Show this help message and exit
  -hh                   显示高级帮助消息并退出
  --version             显示程序版本号并退出
  -v VERBOSE            详细程度: 0-6 (默认 1)

  目标:
    至少提供下列一个选项作为注入目标

    -d DIRECT           直接连接数据库  (例如：mysql://USER:PASSWORD@DBMS_IP:DBMS_PORT/D
                        ATABASE_NAME)
    -u URL, --url=URL   目标网址(例如:http://www.site.com/vuln.php?id=1)
    -l LOGFILE          从Burp或WebScarab代理日志文件解析目标
    -x SITEMAPURL       从远程站点地图（.xml）文件解析目标
    -m BULKFILE         扫描文本文件中给出的多个目标
    -r REQUESTFILE      从文件加载HTTP请求
    -g GOOGLEDORK       将Google dork搜索结果作为目标，这个选项使得sqlmap可以通过和搜索引擎通信,通过google
                        dork搜索可能存在sql注入的网站 ,然后sqlmap会提取前100个结果
                        ,并询问用户是否针对这些目标进行检测   (例如：python sqlmap.py -g
                        "inurl:".php?id=1"")
    -c CONFIGFILE       加载sqlmap.conf文件里面的相关配置

  请求:
    该选项指定以何种方式连接到目标URL

    --method=METHOD     强制使用指定的HTTP请求方法(例如：GET PUT)
    --data=DATA         以POST方式提交数据
    --param-del=PARA..  用于分割参数值的字符
    --cookie=COOKIE     HTTP Cookie header value
    --cookie-del=COO..  用于分割cookie值的字符
    --load-cookies=L..  包含Netscape/wget格式的Cookie的文件
    --drop-set-cookie   从响应response中忽略Set-Cookie header
    --user-agent=AGENT  自定义修改HTTP请求头中User-Agent值
    --random-agent      使用随机选择的HTTP User-Agent header值
    --host=HOST         HTTP Host header value
    --referer=REFERER   sqlmap可以在请求中伪造HTTP中的referer,当--
                        level参数设定为3或者3以上的时候会尝试对referer注入。
    -H HEADER, --hea..  Extra header (例如: "X-Forwarded-For: 127.0.0.1")
    --headers=HEADERS   Extra headers (例如: "Accept-Language: fr\nETag: 123")
    --auth-type=AUTH..  HTTP认证类型(Basic, Digest, NTLM or PKI)
    --auth-cred=AUTH..  HTTP身份验证凭证(用户名:密码)
    --auth-file=AUTH..  HTTP认证PEM认证/私钥文件
    --ignore-401        忽略HTTP错误401（未经授权）
    --ignore-proxy      忽略系统默认代理设置
    --ignore-redirects  忽略重定向尝试
    --ignore-timeouts   忽略连接超时
    --proxy=PROXY       使用代理连接到目标URL
python sqlmap.py --proxy=127.0.0.1:80 --batch -u "http://www.sallatykka.com/web/index.php?id=31"
    --proxy-cred=PRO..  代理认证凭证(用户名:密码)
    --proxy-file=PRO..  从文件加载代理列表
    --tor               使用Tor匿名网络
    --tor-port=TORPORT  设置tor的端口，如果不是默认端口的话
    --tor-type=TORTYPE  设置Tor代理类型(HTTP, SOCKS4 or SOCKS5 (default))
    --check-tor         检查Tor是否可用
    --delay=DELAY       每个HTTP请求之间的延迟秒数
    --timeout=TIMEOUT   设置超时时间，默认30秒
    --retries=RETRIES   设置连接超时时重试次数，默认3次
    --randomize=RPARAM  随机更改给定参数的值
    --safe-url=SAFEURL  有的web程序会在多次错误访问后屏蔽所有请求，这样就导致之后所有的测试无法进行，绕过这个策略可以使用
                        --safe-url，每隔一段时间去访问一个正常的页面。
    --safe-post=SAFE..  发送POST数据到一个安全的URL
    --safe-req=SAFER..  从文件加载安全的HTTP请求
    --safe-freq=SAFE..  提供一个安全无错误的连接，在测试URL和安全链接之间交叉访问
    --skip-urlencode    根据参数位置，他的值默认将会被URL编码，但是有些时候后端的web服务器不遵守RFC标准，只接受不经过URL
                        编码的值，这时候就需要用--skip-urlencode参数,跳过Payload数据的URL编码
    --csrf-token=CSR..  设置CSRF的token
    --csrf-url=CSRFURL  访问URL地址提取anti-CSRF token
    --force-ssl         强制使用SSL/HTTPS
    --hpp               使用HTTP参数污染方法绕过WAF的检测机制
    --eval=EVALCODE     发送请求之前，先运行这段python代码，比如下面的hash参数就是id的md5值 (python
                        sqlmap.py -u "http://www.target.com/vuln.php?id=1&hash
                        =c4ca4238a0b923820dcc509a6f75849b" --eval = "import
                        hashlib;hash=hashlib.md5(id).hexdigest()")

  优化:
    这些选项可用于优化sqlmap的性能

    -o                  开启所有优化选项
    --predict-output    预测常见查询输出
    --keep-alive        使用持久的HTTP(s)连接
    --null-connection   检索页面长度,排除实际的 HTTP 响应内容
    --threads=THREADS   最大并发HTTP(s)请求数（默认为1）

  注入:
    这些选项可用于指定要测试的参数,提供自定义注入Payload和篡改脚本

    -p TESTPARAMETER    手动指定要测试的参数，默认情况下sqlmap会测试所有的GET和POST参数(例如: -p "id")
    --skip=SKIP         跳过你不想进行注入测试的参数
    --skip-static       跳过那些不是动态的测试参数，对静态参数进行注入测试是徒劳的
    --param-exclude=..  使用正则表达式来排除不需要测试的参数 (例如:"ses")
    --dbms=DBMS         指定后端的数据库类型（如mysql，oracle等）
    --dbms-cred=DBMS..  数据库认证凭证(user:password)
    --os=OS             手动指定后端DBMS操作系统(Windows，linux)
    --invalid-bignum    指定无效的大数字id=13,sqlmap会变成id=-13来报错,你也可以指定比如id=9999999来报错
    --invalid-logical   指定无效的逻辑,可以指定id=13把原来的id=-13的报错改成id=13 AND 18=19
    --invalid-string    使用随机字符串无效值来给参数赋值
    --no-cast           关闭payload构造机制
    --no-escape         关闭字符串转义机制
    --prefix=PREFIX     设置注入的前缀，比如单引号注入点，就设置前缀为单引号
    --suffix=SUFFIX     设置注入payload的后缀
    --tamper=TAMPER     使用tamper脚本修改请求从而逃避WAF的规则检测

  探测:
    这些选项可用于指定检测目标的等级

    --level=LEVEL       探测等级(1-5,默认1级)
    --risk=RISK         风险等级 (1-3, 默认1级)
    --string=STRING     设置原始页面与条件为真情况下页面中都存在的字符串，而错误页面中不存在，如果页面返回这个字符串，说明我们的注入
                        判断语句是正确的
    --not-string=NOT..  设置一段在原始页面与真条件页面中都不存在的字符串，而错误页面中存在的字符串
    --regexp=REGEXP     利用正则匹配页面返回内容，如果存在匹配字符串，则可能存在注入点
    --code=CODE         用HTTP响应码来判断注入语句是否正确，例如，响应200的时候为真，响应401的时候为假，可以添加参数--
                        code=200
    --text-only         基于文本内容比较页面
    --titles            基于标题比较页面

  注入技术:
    这些选项可用于指定具体的SQL注入技术的测试

    --technique=TECH    要使用的SQL注入技术(默认 "BEUSTQ")
    --time-sec=TIMESEC  设定延迟注入的时间，当使用基于时间的盲注时，时刻使用--time-sec参数设定延时时间，默认是5秒
    --union-cols=UCOLS  设定SQL注入时UNION查询字段数范围，如：12-16，是测试12-16个字段数
    --union-char=UCHAR  设定UNION查询使用的字符，用于爆破字段数目的字符,默认使用NULL字符，但是有些情况下会造成页面返回失败
                        ，而一个随机整数是成功的，这时你可以用--union-char指定UNION查询的字符
    --union-from=UFROM  在UNION查询SQL注入中填充FORM的表格
    --dns-domain=DNS..  用于DNS渗透攻击的域名
    --second-order=S..  有些时候注入点输入的数据返回结果的时候并不是当前的页面，而是另外的一个页面，这时候就需要你指定到那个页面来获
                        取响应结果判断真假。--second-order后面跟一个判断页面的URL地址。

  指纹识别:
    -f, --fingerprint   利用数据库特有的指纹信息识别其数据库类型和版本号

  检索数据:
    这些选项可用于枚举表中包含的DBMS信息结构和数据。此外，您可以运行自己的SQL语句

    -a, --all           检索所有内容
    -b, --banner        检索数据库管理系统的标识（如mysql，oracle）
    --current-user      检索当前连接数据库的用户CURRENT_USER()
    --current-db        检索当前连接的数据库DATABASE()
    --hostname          检索服务器的主机名@@HOSTNAME
    --is-dba            判断当前用户是否为管理，是的话会返回True
    --users             枚举数据库用户，当前用户有权限读取包含所有用户的表的权限时，就可以列出所有管理用户
    --passwords         枚举数据库用户密码的哈希值并尝试破解
    --privileges        枚举数据库用户的权限
    --roles             枚举数据库用户的角色
    --dbs               列出所有的数据库
    --tables            列举数据库中的所有表
    --columns           列举数据库表中的字段，同时也会列出字段的数据类型
    --schema            列举数据库系统的架构，包含所有的数据库，表和字段，以及各自的类型
    --count             检索表的条目数
    --dump              获取整个表的数据
    --dump-all          获取所有数据库表中的内容
    --search            搜索字段，表，数据库，配合下面的-D,-C,-T
    --comments          枚举数据库的注释
    -D DB               要进行枚举的数据库名
    -T TBL              要进行枚举的数据库表
    -C COL              要进行枚举的数据库字段
    -X EXCLUDECOL       指定不枚举那个字段
    -U USER             枚举数据库用户
    --exclude-sysdbs    枚举表时排除系统数据库
    --pivot-column=P..  行转列名称
    --where=DUMPWHERE   使用WHERE条件查询/获取指定表中的内容
    --start=LIMITSTART  指定开始从第几行开始输出，如--start=3，前两行就不输出了
    --stop=LIMITSTOP    指定从第几行开始停止输出
    --first=FIRSTCHAR   指定从第几个字符之后开始输出
    --last=LASTCHAR     指定输出到第几个字符后停止输出，盲注才有效，亲测，跟上面的配合指定范围，如 ：--first 3
                        --last 5  只输出3到5位置的字符
    --sql-query=QUERY   指定执行我们的sql语句
    --sql-shell         返回一个sql的shell
    --sql-file=SQLFILE  从文件中读取执行sql语句

  爆破:
    这些选项可用于执行爆破检查

    --common-tables     检测常见的表名，暴力破解表名
    --common-columns    检测常见的字段名，暴力破解列名

  使用用户自定义的功能进行注入:
    --udf-inject        注入用户自定义的功能
    --shared-lib=SHLIB  共享库的本地路径

  文件系统访问:
    这些选项可用于访问基础文件系统的后端DBMS

    --file-read=RFILE   从数据库服务器中读取文件
    --file-write=WFILE  把文件写入/上传到数据库服务器中
    --file-dest=DFILE   写入数据库服务器的绝对路径

  操作系统访问:
    这些选项可用于访问基础操作系统的后端DBMS

    --os-cmd=OSCMD      执行操作系统命令
    --os-shell          返回一个shell
    --os-pwn            调出一个带外shell/meterpreter/VNC
    --os-smbrelay       一键调出OOB shell/meterpreter/VNC
    --os-bof            存储过程缓冲区溢出利用
    --priv-esc          对当前连接数据库进程的用户进行权限提升
    --msf-path=MSFPATH  安装Metasploit Framework的本地路径
    --tmp-path=TMPPATH  临时文件目录的远程绝对路径

  Windows注册表访问:
    这些选项可用于访问后端数据库管理系统Windows注册表

    --reg-read          读取Windows注册表项值
    --reg-add           写入注册表值
    --reg-del           删除注册表值
    --reg-key=REGKEY    指定键，配合之前三个参数使用，例如：python sqlmap.py -u
                        http://192.168.136.129/sqlmap/pgsql/get_int.aspx?id=1
                        --reg-add --reg-
                        key="HKEY_LOCAL_MACHINE\SOFTWARE\sqlmap" --reg-
                        value=Test --reg-type=REG_SZ --reg-data=1
    --reg-value=REGVAL  指定键值
    --reg-data=REGDATA  指定键值的数据
    --reg-type=REGTYPE  指定键值的类型

  通用:
    一些常用选项

    -s SESSIONFILE      从（.sqlite）文件中读取session会话
    -t TRAFFICFILE      保存HTTP(S)日志，这个参数需要跟一个文本文件，sqlmap会把HTTP(S)请求与响应的日志保存到那里
    --batch             非交互模式，用此参数，不需要用户输入，将会使用sqlmap提示的默认值一直运行下去
    --binary-fields=..  Result fields having binary values (例如： "digest")
    --charset=CHARSET   强制指定字符编码（如：--charset=GBK）
    --check-internet    访问"http://ipinfo.io/"确认是否连接到互联网
    --crawl=CRAWLDEPTH  爬行网站URL，sqlmap可以收集潜在的可能存在漏洞的连接，后面跟的参数是爬行的深度--batch
                        --crawl=3
    --crawl-exclude=..  使用正则表达式排除网页中我们不想抓取的内容 (例如我们不想爬行日志内容： "logout")
    --csv-del=CSVDEL    当保存为CSV格式时（--dump-format=CSV），需要一个分隔符(默认是逗号：
                        ",")，用户也可以改为别的,如分号：--csv-del=";"
    --dump-format=DU..  输出数据的格式（CSV，HTML或SQLITE）默认输出CSV格式
    --eta               计算注入数据的剩余时间，sqlmap先输出长度，预计完成时间，显示百分比，输出字符17%
                        [========>                  ] 11/64  ETA 00:19
    --flush-session     刷新session文件，如果不想用之前缓存这个目标的session文件，可以使用这个参数。
                        会清空之前的session，重新测试该目标。
    --forms             在目标网址上解析和测试表单
    --fresh-queries     忽略存储在会话文件中的查询结果
    --har=HARFILE       将所有HTTP流量记录到HAR文件中
    --hex               使用DBMS十六进制功能进行数据检索
    --output-dir=OUT..  自定义输出目录路径
    --parse-errors      从响应中解析并显示DBMS错误消息
    --save=SAVECONFIG   将选项保存到配置文件中INI
    --scope=SCOPE       利用正则表达式从提供的代理日志中过滤目标
    --test-filter=TE..  通过Payload和/或标题选择测试 (例如:ROW)
    --test-skip=TEST..  跳过Payload和/或标题测试 (例如:BENCHMARK)
    --update            更新sqlmap

  解忧杂货铺:
    -z MNEMONICS        使用简短的助记符 (例如: "flu,bat,ban,tec=EU")
    --alert=ALERT       发现SQL注入时运行主机操作系统命令
    --answers=ANSWERS   设置问题的答案 (例如: "quit=N,follow=N")
    --beep              检测到注入点时发出蜂鸣声提示
    --cleanup           清除sqlmap注入时产生的udf与表
    --dependencies      检查sqlmap是否缺少第三方库
    --disable-coloring  禁用控制台输出着色
    --gpage=GOOGLEPAGE  默认sqlmap使用前100个URL地址作为注入测试，结合此选项，可以对指定页码的URL测试
    --identify-waf      对WAF/IPS/IDS保护进行全面测试
    --mobile            通过HTTP User-Agent header模拟智能手机,有时服务端只接收移动端的访问
                        ，此时可以设定一个手机的User-Agent来模仿手机登陆
    --offline           离线模式工作(仅使用会话数据)
    --purge-output      从输出目录中安全删除所有内容,有时需要删除结果文件，而不被恢复，原有文件将会被随机的一些文件覆盖
    --skip-waf          跳过启发式检测WAF/IPS/IDS保护
    --smart             启发式判断注入,有时对目标非常多的URL进行测试，为节省时间，只对能够快速判断为注入的报错点进行注入
    --sqlmap-shell      交互式sqlmap shell
    --tmp-dir=TMPDIR    用于存储临时文件的本地目录
    --web-root=WEBROOT  Web服务器文件根目录(例如 "/var/www")
    --wizard            简单的向导界面，用于初级用户
        ___
       __H__
 ___ ___["]_____ ___ ___  {1.1.7.21#dev}
|_ -| . ["]     | .'| . |
|___|_  [)]_|_|_|__,|  _|
      |_|V          |_|   欢迎使用sqlmap中文版

Usage: python sqlmap.py [options]

Options:
  -h, --help            Show this help message and exit
  -hh                   显示高级帮助消息并退出
  --version             显示程序版本号并退出
  -v VERBOSE            详细程度: 0-6 (默认 1)

  目标:
    至少提供下列一个选项作为注入目标

    -d DIRECT           直接连接数据库  (例如：mysql://USER:PASSWORD@DBMS_IP:DBMS_PORT/D
                        ATABASE_NAME)
    -u URL, --url=URL   目标网址(例如:http://www.site.com/vuln.php?id=1)
    -l LOGFILE          从Burp或WebScarab代理日志文件解析目标
    -x SITEMAPURL       从远程站点地图（.xml）文件解析目标
    -m BULKFILE         扫描文本文件中给出的多个目标
    -r REQUESTFILE      从文件加载HTTP请求
    -g GOOGLEDORK       将Google dork搜索结果作为目标，这个选项使得sqlmap可以通过和搜索引擎通信,通过google
                        dork搜索可能存在sql注入的网站 ,然后sqlmap会提取前100个结果
                        ,并询问用户是否针对这些目标进行检测   (例如：python sqlmap.py -g
                        "inurl:".php?id=1"")
    -c CONFIGFILE       加载sqlmap.conf文件里面的相关配置

  请求:
    该选项指定以何种方式连接到目标URL

    --method=METHOD     强制使用指定的HTTP请求方法(例如：GET PUT)
    --data=DATA         以POST方式提交数据
    --param-del=PARA..  用于分割参数值的字符
    --cookie=COOKIE     HTTP Cookie header value
    --cookie-del=COO..  用于分割cookie值的字符
    --load-cookies=L..  包含Netscape/wget格式的Cookie的文件
    --drop-set-cookie   从响应response中忽略Set-Cookie header
    --user-agent=AGENT  自定义修改HTTP请求头中User-Agent值,只有--level等级为3以上设置才会生效
    --random-agent      使用随机选择的HTTP User-Agent header值
    --host=HOST         自定义修改HTTP请求头中的Host值,只有在--level值为5的时候设置才会生效
    --referer=REFERER   sqlmap可以在请求中伪造HTTP中的referer,当--
                        level参数设定为3或者3以上的时候会尝试对referer注入。
    -H HEADER, --hea..  Extra header (例如: "X-Forwarded-For: 127.0.0.1")
    --headers=HEADERS   Extra headers (例如: "Accept-Language: fr\nETag: 123")
    --auth-type=AUTH..  HTTP认证类型(Basic, Digest, NTLM or PKI)
    --auth-cred=AUTH..  HTTP身份验证凭证(用户名:密码)
    --auth-file=AUTH..  HTTP认证PEM认证/私钥文件
    --ignore-401        忽略HTTP错误401（未经授权）
    --ignore-proxy      忽略系统默认代理设置
    --ignore-redirects  忽略重定向尝试
    --ignore-timeouts   忽略连接超时
    --proxy=PROXY       使用代理连接到目标URL
    --proxy-cred=PRO..  代理认证凭证(用户名:密码)
    --proxy-file=PRO..  从文件加载代理列表
    --tor               使用Tor匿名网络
    --tor-port=TORPORT  设置tor的端口，如果不是默认端口的话
    --tor-type=TORTYPE  设置Tor代理类型(HTTP, SOCKS4 or SOCKS5 (default))
    --check-tor         检查Tor是否可用
    --delay=DELAY       每个HTTP请求之间的延迟秒数
    --timeout=TIMEOUT   设置超时时间，默认30秒
    --retries=RETRIES   设置连接超时时重试次数，默认3次
    --randomize=RPARAM  随机更改给定参数的值
    --safe-url=SAFEURL  有的web程序会在多次错误访问后屏蔽所有请求，这样就导致之后所有的测试无法进行，绕过这个策略可以使用
                        --safe-url，每隔一段时间去访问一个正常的页面。
    --safe-post=SAFE..  发送POST数据到一个安全的URL
    --safe-req=SAFER..  从文件加载安全的HTTP请求
    --safe-freq=SAFE..  提供一个安全无错误的连接，在测试URL和安全链接之间交叉访问
    --skip-urlencode    根据参数位置，他的值默认将会被URL编码，但是有些时候后端的web服务器不遵守RFC标准，只接受不经过URL
                        编码的值，这时候就需要用--skip-urlencode参数,跳过Payload数据的URL编码
    --csrf-token=CSR..  设置CSRF的token
    --csrf-url=CSRFURL  访问URL地址提取anti-CSRF token
    --force-ssl         强制使用SSL/HTTPS
    --hpp               使用HTTP参数污染方法绕过WAF的检测机制，HTTP参数污染是一种可以绕过WAF/IPS/IDS的方法，这
                        在面对ASP/IIS 或者是ASP.NET/IIS
                        组合的时候非常有用，如果你怀疑目标使用了某种保护(WAF/IDS/IPS) 那么你可以试试这个选项
    --eval=EVALCODE     发送请求之前，先运行这段python代码，比如下面的hash参数就是id的md5值 (python
                        sqlmap.py -u "http://www.target.com/vuln.php?id=1&hash
                        =c4ca4238a0b923820dcc509a6f75849b" --eval = "import
                        hashlib;hash=hashlib.md5(id).hexdigest()")

  优化:
    这些选项可用于优化sqlmap的性能

    -o                  开启所有优化选项
    --predict-output    预测常见查询输出
    --keep-alive        使用持久的HTTP(s)连接
    --null-connection   检索页面长度,排除实际的 HTTP 响应内容
    --threads=THREADS   最大并发HTTP(s)请求数（默认为1）

  注入:
    这些选项可用于指定要测试的参数,提供自定义注入Payload和篡改脚本

    -p TESTPARAMETER    手动指定要测试的参数，默认情况下sqlmap会测试所有的GET和POST参数(例如: -p "id")
    --skip=SKIP         跳过你不想进行注入测试的参数
    --skip-static       跳过那些不是动态的测试参数，对静态参数进行注入测试是徒劳的
    --param-exclude=..  使用正则表达式来排除不需要测试的参数 (例如:"ses")
    --dbms=DBMS         指定后端的数据库类型（如mysql，oracle等）
    --dbms-cred=DBMS..  数据库认证凭证(user:password)
    --os=OS             手动指定后端DBMS操作系统(Windows，linux)
    --invalid-bignum    指定无效的大数字id=13,sqlmap会变成id=-13来报错,你也可以指定比如id=9999999来报错
    --invalid-logical   指定无效的逻辑,可以指定id=13把原来的id=-13的报错改成id=13 AND 18=19
    --invalid-string    使用随机字符串无效值来给参数赋值
    --no-cast           关闭payload构造机制
    --no-escape         关闭字符串转义机制
    --prefix=PREFIX     设置注入的前缀，比如单引号注入点，就设置前缀为单引号
    --suffix=SUFFIX     设置注入payload的后缀
    --tamper=TAMPER     使用tamper脚本修改请求从而逃避WAF的规则检测

  探测:
    这些选项可用于指定检测目标的等级

    --level=LEVEL       探测等级(1-5,默认1级)
    --risk=RISK         风险等级(1-3, 默认1级)
    --string=STRING     设置原始页面与条件为真情况下页面中都存在的字符串，而错误页面中不存在，如果页面返回这个字符串，说明我们的注入
                        判断语句是正确的
    --not-string=NOT..  设置一段在原始页面与真条件页面中都不存在的字符串，而错误页面中存在的字符串
    --regexp=REGEXP     利用正则匹配页面返回内容，如果存在匹配字符串，则可能存在注入点
    --code=CODE         用HTTP响应码来判断注入语句是否正确，例如，响应200的时候为真，响应401的时候为假，可以添加参数--
                        code=200
    --text-only         基于文本内容比较页面,如果在HTTP响应中存在大量脚本、或者是各种内嵌的东西 ,可以通过使用--text-
                        only来进行筛选只显示文本内容
    --titles            基于标题比较页面,如果使用者知道正常、错误响应之间的HTML标题的区别
                        (例如Welcom为正常，Forbidden为错误)那么他可以通过使用--
                        titles来比较HTML标题的不同来提示sqlmap是否能够注入

  注入技术:
    这些选项可用于指定具体的SQL注入技术的测试

    --technique=TECH    要使用的SQL注入技术(默认 "BEUSTQ")
    --time-sec=TIMESEC  设定延迟注入的时间，当使用基于时间的盲注时，时刻使用--time-sec参数设定延时时间，默认是5秒
    --union-cols=UCOLS  设定SQL注入时UNION查询字段数范围，如：12-16，是测试12-16个字段数
    --union-char=UCHAR  设定UNION查询使用的字符，用于爆破字段数目的字符,默认使用NULL字符，但是有些情况下会造成页面返回失败
                        ，而一个随机整数是成功的，这时你可以用--union-char指定UNION查询的字符
    --union-from=UFROM  在某些UNION查询SQL注入情况下，需要在FROM子句中强制使用有效且可访问的表名。
                        例如，Microsoft Access需要使用这样的表。
                        如果不提供一个UNION查询，SQL注入将无法正确执行(例如 --union-from = users)
    --dns-domain=DNS..  用于DNS渗透攻击的域名
    --second-order=S..  二阶注入是攻击者首先提交恶意的请求，在数据库保存成功后 再提交另外一个用于检索之前的恶意请求的请求，如果攻击
                        成功，那么响应会在第二次响应中返回结果，使用这个选项的时候后面跟着的是显示结果页面的URL。有些时候注入点输
                        入的数据返回结果的时候并不是当前的页面，而是另外的一个页面，这时候就需要你指定到哪个页面来获取响应结果判断真
                        假。--second-order后面跟一个判断页面的URL地址。

  指纹识别:
    -f, --fingerprint   利用数据库特有的指纹信息识别其数据库类型和版本号

  检索数据:
    这些选项可用于枚举表中包含的DBMS信息结构和数据。此外，您可以运行自己的SQL语句

    -a, --all           检索所有内容
    -b, --banner        检索数据库管理系统的标识（如mysql，oracle）
    --current-user      检索当前连接数据库的用户CURRENT_USER()
    --current-db        检索当前连接的数据库DATABASE()
    --hostname          检索服务器的主机名@@HOSTNAME
    --is-dba            判断当前用户是否为管理，是的话会返回True
    --users             枚举数据库用户，当前用户有权限读取包含所有用户的表的权限时，就可以列出所有管理用户
    --passwords         枚举数据库用户密码的哈希值并尝试破解
    --privileges        枚举数据库用户的权限
    --roles             枚举数据库用户的角色
    --dbs               列出所有的数据库
    --tables            列举数据库中的所有表
    --columns           列举数据库表中的字段，同时也会列出字段的数据类型
    --schema            列举数据库系统的架构，包含所有的数据库，表和字段，以及各自的类型
    --count             检索表的条目数
    --dump              获取整个表的数据
    --dump-all          获取所有数据库表中的内容
    --search            搜索字段，表，数据库，配合下面的-D,-C,-T
    --comments          枚举数据库的注释
    -D DB               要进行枚举的数据库名
    -T TBL              要进行枚举的数据库表
    -C COL              要进行枚举的数据库字段
    -X EXCLUDECOL       指定不枚举那个字段
    -U USER             枚举数据库用户
    --exclude-sysdbs    枚举表时排除系统数据库
    --pivot-column=P..  行转列名称
    --where=DUMPWHERE   使用WHERE条件查询/获取指定表中的内容
    --start=LIMITSTART  指定开始从第几行开始输出，如--start=3，前两行就不输出了
    --stop=LIMITSTOP    指定从第几行开始停止输出
    --first=FIRSTCHAR   指定从第几个字符之后开始输出
    --last=LASTCHAR     指定输出到第几个字符后停止输出，盲注才有效，亲测，跟上面的配合指定范围，如 ：--first 3
                        --last 5  只输出3到5位置的字符
    --sql-query=QUERY   指定执行我们的sql语句
    --sql-shell         返回一个sql的shell
    --sql-file=SQLFILE  从文件中读取执行sql语句

  爆破:
    这些选项可用于执行爆破检查

    --common-tables     检测常见的表名，暴力破解表名
    --common-columns    检测常见的字段名，暴力破解列名

  使用用户自定义的功能进行注入:
    --udf-inject        注入用户自定义的功能
    --shared-lib=SHLIB  共享库的本地路径

  文件系统访问:
    这些选项可用于访问基础文件系统的后端DBMS

    --file-read=RFILE   从数据库服务器中读取文件
    --file-write=WFILE  把文件写入/上传到数据库服务器中
    --file-dest=DFILE   写入数据库服务器的绝对路径

  操作系统访问:
    这些选项可用于访问基础操作系统的后端DBMS

    --os-cmd=OSCMD      执行操作系统命令
    --os-shell          返回一个shell
    --os-pwn            调出一个带外shell/meterpreter/VNC
    --os-smbrelay       一键调出OOB shell/meterpreter/VNC
    --os-bof            存储过程缓冲区溢出利用
    --priv-esc          对当前连接数据库进程的用户进行权限提升
    --msf-path=MSFPATH  安装Metasploit Framework的本地路径
    --tmp-path=TMPPATH  临时文件目录的远程绝对路径

  Windows注册表访问:
    这些选项可用于访问后端数据库管理系统Windows注册表

    --reg-read          读取Windows注册表项值
    --reg-add           写入注册表值
    --reg-del           删除注册表值
    --reg-key=REGKEY    指定键，配合之前三个参数使用，例如：python sqlmap.py -u
                        http://192.168.136.129/sqlmap/pgsql/get_int.aspx?id=1
                        --reg-add --reg-
                        key="HKEY_LOCAL_MACHINE\SOFTWARE\sqlmap" --reg-
                        value=Test --reg-type=REG_SZ --reg-data=1
    --reg-value=REGVAL  指定键值
    --reg-data=REGDATA  指定键值的数据
    --reg-type=REGTYPE  指定键值的类型

  通用:
    一些常用选项

    -s SESSIONFILE      从（.sqlite）文件中读取session会话
    -t TRAFFICFILE      保存HTTP(S)日志，这个参数需要跟一个文本文件，sqlmap会把HTTP(S)请求与响应的日志保存到那里
    --batch             非交互模式，用此参数，不需要用户输入，将会使用sqlmap提示的默认值一直运行下去
    --binary-fields=..  Result fields having binary values (例如： "digest")
    --charset=CHARSET   强制指定字符编码（如：--charset=GBK）
    --check-internet    访问"http://ipinfo.io/"确认是否连接到互联网
    --crawl=CRAWLDEPTH  爬行网站URL，sqlmap可以收集潜在的可能存在漏洞的连接，后面跟的参数是爬行的深度--batch
                        --crawl=3
    --crawl-exclude=..  使用正则表达式排除网页中我们不想抓取的内容 (例如我们不想爬行url中包含logout的页面，可以这样写
                        --crawl-exclude=logout)
    --csv-del=CSVDEL    当保存为CSV格式时（--dump-format=CSV），需要一个分隔符(默认是逗号：
                        ",")，用户也可以改为别的,如分号：--csv-del=";"
    --dump-format=DU..  输出数据的格式（CSV，HTML或SQLITE）默认输出CSV格式
    --eta               计算注入数据的剩余时间，sqlmap先输出长度，预计完成时间，显示百分比，输出字符17%
                        [========>                  ] 11/64  ETA 00:19
    --flush-session     刷新session文件，如果不想用之前缓存这个目标的session文件，可以使用这个参数。
                        会清空之前的session，重新测试该目标。
    --forms             在目标网址上解析和测试表单，如果你想通过form表单来测试SQL注入或者是弱密码(名字加密码)
                        ，你可以通过使用-r把请求保存在文件中进行测试 或者--data发送POST数据
                        或者让sqlmap自动选择个选项对HTML响应中的<;form>;或者是<;input>;这样的标签进行测试
                        ，通过给sqlmap提供目标地址参数-u以及使用--
                        form参数，它会自动请求对应的目标地址并且对form表单的输入进行测试
    --fresh-queries     忽略存储在会话文件中的查询结果
    --har=HARFILE       将所有HTTP流量记录到HAR文件中
    --hex               使用DBMS十六进制功能进行数据检索，很多情况下你检索的数据可能是非ASCII码的，
                        解决这个问题的一个办法是使用DBMS十六进制功能。
                        在这个开关打开的情况下，数据在被检索之前被编码为十六进制形式，然后被编码为原始形式。
    --output-dir=OUT..  自定义输出目录路径
    --parse-errors      从响应中解析并显示DBMS错误消息
    --save=SAVECONFIG   将选项保存到配置文件中INI
    --scope=SCOPE       利用正则表达式从提供的代理日志中过滤目标
    --test-filter=TE..  通过Payload和/或标题选择测试 (例如:ROW)
    --test-skip=TEST..  跳过Payload和/或标题测试 (例如:BENCHMARK)
    --update            更新sqlmap

  解忧杂货铺:
    -z MNEMONICS        使用简短的助记符 (例如: "flu,bat,ban,tec=EU")
    --alert=ALERT       发现SQL注入时运行主机操作系统命令
    --answers=ANSWERS   设置问题的答案，在使用--batch的时候可以通过使用--
                        answers来指定某个回答所需要的答案，如果是多个的话 可以通过使用,来进行分隔 (例如:
                        "quit=N,follow=N")
    --beep              检测到注入点时发出蜂鸣声提示
    --cleanup           清除sqlmap注入时产生的udf与表
    --dependencies      检查sqlmap是否缺少第三方库，sqlmap在某些特定的情况下需要用到第三方的库 (例如 -d --os-
                        pwn用到的icmpsh 通道 --auth-type 用到的NTLM HTTP认证类型)
                        在这些情况下都会有警告，建议使用--dependencies来进行检查
    --disable-coloring  禁用控制台输出着色
    --gpage=GOOGLEPAGE  默认sqlmap使用前100个URL地址作为注入测试，结合此选项，可以对指定页码的URL测试
    --identify-waf      对WAF/IPS/IDS保护进行全面测试
    --mobile            通过HTTP User-Agent header模拟智能手机,有时服务端只接收移动端的访问
                        ，此时可以设定一个手机的User-Agent来模仿手机登陆
    --offline           离线模式工作(仅使用会话数据)
    --purge-output      从输出目录中安全删除所有内容,有时需要删除结果文件，而不被恢复，原有文件将会被随机的一些文件覆盖
    --skip-waf          跳过启发式检测WAF/IPS/IDS保护
    --smart             启发式判断注入,有时对目标非常多的URL进行测试，为节省时间，只对能够快速判断为注入的报错点进行注入
    --sqlmap-shell      交互式sqlmap shell
    --tmp-dir=TMPDIR    用于存储临时文件的本地目录
    --web-root=WEBROOT  Web服务器文件根目录(例如 "/var/www")
    --wizard            简单的向导界面，用于初级用户
