# 特征

在 sqlmap 里实现的特征包括:

## 一般特征

* 全面支持 **MySQL**, **Oracle**, **PostgreSQL**, **Microsoft SQL Server**, **Microsoft Access**, **IBM DB2**, **SQLite**, **Firebird**, **Sybase**, **SAP MaxDB** 和 **HSQLDB** 数据库管理系统.
* 全面支持五种 SQL 注入技术: **boolean-based blind**, **time-based blind**, **error-based**, **UNION query** 和 **stacked queries**.
* 支持 **直接连接数据库** 无需通过 SQL 注入, 通过提供 DBMS 凭据, IP 地址, 端口和数据库名称.
* 它可以提供一个单一的目标 URL, 获得来自 [Burp proxy](http://portswigger.net/suite/)的目标列表或者 [WebScarab proxy](http://www.owasp.org/index.php/Category:OWASP_WebScarab_Project) 请求日志文件 , 从文本文件中得到完整的 HTTP 请求或者得到目标列表 通过给 sqlmap 提供一个 Google dork 用于查询 [Google](http://www.google.com) 搜索引擎并解析其结果页. 您还可以定义一个基于正则表达式的范围，用于标识要测试的解析地址中的哪一个.
* 测试提供  **GET** 因素, **POST** 因素, HTTP **Cookie** 报头值, HTTP **用户代理** 报头值和 HTTP **引用** 报头值来识别和利用 SQL 注入漏洞. 还可以指定一个逗号分隔的特定参数列表来测试.
* 选项以指定 **最大的并发HTTP请求（多线程）** 来加快盲目的SQL注入技术. 反之亦然, 还可以指定要在每个HTTP请求之间保持的秒数. 其他加速开发的优化开关也被实施.
* **HTTP `Cookie` header** 字符串支持, 用于当Web应用程序需要基于cookie的身份验证时并且您有这样的数据，或者您只是想在这样的报头值上测试并利用SQL注入. 您还可以指定始终URL编码 Cookie.
* 自动从应用程序中处理 **HTTP `设置Cookie` header**, 重新设置会话如果会话过期.也支持对这些值的测试和利用. 反之亦然，您也可以强制忽略任何 `设置Cookie` header.
* HTTP 协议 **基本, 整理, NTLM 和证书认证 ** 支持.
* **HTTP(S) 代理** 支持将请求传递给与HTTPS请求和经过认证的代理服务器一起工作的目标应用程序.
* 选择由用户指定或随机选取的文本文件来伪造 **HTTP `Referer` header** 值和 **HTTP `用户代理` header** 值.
* 支持增加 **输出信息的冗长程度**:  冗长分为**七级**.
* 支持 **解析HTML表单** 从目标URL和针对这些页面的伪造HTTP请求来测试针对漏洞的表单参数.
* **粒度和灵活性** 在用户交换机和功能方面.
* **预计到达时间** 支持每个查询，实时更新，向用户提供检索查询输出需要多长时间的概述.
* 自动保存会话（查询及其输出，即使部分检索）在文本文件中并实时获取数据和 通过解析会话文件**重新注入** .
* 支持从配置INI文件中读取选项而不是每次指定命令行上的所有开关. 还支持根据提供的命令行开关生成配置文件.
* 支持**复制的后端数据库表结构和条目**** 在一个本地的 SQLite 3 数据库.
* 选择将 sqlmap 从较低版本库更新到最新开发的版本.
c* 支持解析HTTP响应并向用户显示任何 DBMS 错误消息.
* 与其他IT安全开放源代码项目的集成, [Metasploit](http://metasploit.com) 和 [w3af](http://w3af.sourceforge.net).

## 指纹和计数特征

* 基于 **广泛的后台数据库软件版本和底层操作系统指纹 ** 
e[错误消息](http://bernardodamele.blogspot.com/2007/06/database-management-system-fingerprint.html),
[标语解析](http://bernardodamele.blogspot.com/2007/06/database-management-system-fingerprint.html),
[功能输出比较](http://bernardodamele.blogspot.com/2007/07/more-on-database-management-system.html) 和 [具体特点](http://bernardodamele.blogspot.com/2007/07/more-on-database-management-system.html) 比如MySQL注释注入. 如果你已经知道后台数据库管理系统名称也可以强制它.
* 基本web服务器软件与web应用技术指纹 .
* 支持检索 DBMS **标语**, **会话用户** 和 **当前数据库** 信息. 这个工具还可以检查会话用户是否是一个 **数据库管理员** (DBA).
* 支持列举 **用户，密码，权限，角色，数据库，表和列**.
* 密码格式自动识别并且支持用基于词典的攻击破解他们.
* 支持 **强力表和列名**. 这一点非常有用当会话用户不能读取包含构架信息的系统表或数据库管理系统没在任何地方存储此信息时 (e.g. MySQL < 5.0).
* 支持完整 **转储数据库表** , 根据用户的选择设置一系列条目或特定列. 用户也可以选择从每个列的条目中转储一系列字符.
* 支持自动 **转储所有数据库**'模式和条目. 系统数据库中可能排斥转储.
* 支持 **搜索特定数据库名称、所有数据库中的特定表或所有数据库表中的特定列**. 这很有用 , 比如说, 为了识别包含自定义应用程序凭据的表，表的相关列的名称中包含字符串 **name** 和 **pass**.
* 支持在连接到后台数据库的交互式SQL客户端中 **运行自定义SQL语句** . sqlmap 自动剖析提供的声明, 以此决定哪种技术最适合注入它以及如何打包SQL有效载荷.

## 接管的特点

这些技术中的一些是在白皮书中详述的
[完全控制操作系统的高级SQL注入 ](http://www.slideshare.net/inquis/advanced-sql-injection-to-operating-system-full-control-whitepaper-4633857) 和在滑梯的甲板上 [从数据库扩展对操作系统的控制 ](http://www.slideshare.net/inquis/expanding-the-control-over-the-operating-system-from-the-database).

* 支持 **注入自定义用户定义函数**: 用户可以编译一个共享库，然后用sqlmap在后端DBMS用户定义函数范围内中创建已编译的共享库文件. 这些UDF可以通过sqlmap执行，或者选择性删除. 当数据库软件是 MySQL 或 PostgreSQL可以支持这一功能.
* 支持从数据库服务器底层文件系统 **下载和上传任何文件** 如果数据库软件是 MySQL, PostgreSQL 或 Microsoft SQL Server.
* 支持在数据库服务器底层文件系统 **执行任意命令并检索其标准输出** 如果数据库软件是 MySQL, PostgreSQL 或 Microsoft SQL Server.
* 在 MySQL 和 PostgreSQL 中通过用户定义的函数注入和执行.
* 在 Microsoft SQL Server 通过 `xp_cmdshell()` 存储过程.
此外, 储存的过程将重启在它发生故障时，或者在被从DBA中移除时从头创建.
* 支持 **在攻击者机器和数据库服务器之间建立一个带外状态的TCP连接**底层操作系统. 这个通道按照用户的选择，可以是一个交互式命令提示符，一个Meterpreter会话或图形用户界面（VNC）会话.
sqlmap 依靠 Metasploit 来创建恶意代码和实现在数据库上执行四种不同的技术. 这些技术是:
* 数据库 **在内存中执行 Metasploit 的恶意代码** 通过 sqlmap 自身用户定义函数 `sys_bineval()`. 支持 MySQL 和 PostgreSQL.
* 上传并执行一个 Metasploit 的 **独立的有效载荷的老手** 通过 sqlmap 自身用户定义函数 `sys_exec()` 在 MySQL 和 PostgreSQL上 或者通过 `xp_cmdshell()` 在 Microsoft SQL Server上.
* 执行 Metasploit's 恶意代码进行一个 **SMB 反射攻击** ([MS08-068](http://www.microsoft.com/technet/security/Bulletin/MS08-068.mspx) 用UNC路径请求从数据库服务器到攻击者的机器 Metasploit `smb_relay` 服务利用听. 支持当在 Linux/Unix 上以高权限(`uid=0`)运行 sqlmap 和在 Windows 上作为管理者运行的目标DBMS. 
* 内存数据库执行 Metasploit的恶意代码通过利用 **Microsoft SQL Server 2000 和 2005 `sp_replwritetovarbin` 存储的过程堆型缓冲溢出错误** ([MS09-004](http://www.microsoft.com/technet/security/bulletin/ms09-004.mspx)). sqlmap可以自己利用自动DEP内存保护旁路来触发漏洞，但它依赖于 Metasploit 生成恶意代码来执行在成功利用之前.
* 支持 **数据库进程的用户权限升级** 通过 Metasploit的 `getsystem` 命令，其中包括[kitrap0d](http://archives.neohapsis.com/archives/fulldisclosure/2010-01/0346.html) 技术 ([MS10-015](http://www.microsoft.com/technet/security/bulletin/ms10-015.mspx)).
* 支持访问（读取/添加/删除）Windows注册表.
## Demo

你可以观看演示视频在 [Bernardo](http://www.youtube.com/user/inquisb/videos) 和 [Miroslav](http://www.youtube.com/user/stamparm/videos) YouTube 页面.您还可以找到许多针对公开可用的易受攻击的Web应用程序的示例来进行合法的Web评估 [这里](http://unconciousmind.blogspot.com/search/label/sqlmap).
