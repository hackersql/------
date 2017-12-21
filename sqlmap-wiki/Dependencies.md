# 依赖性

sqlmap 是用 [Python](http://www.python.org) 开发的, 这是一个动态的, 面向对象的, 解释性程序设计语言，可以从 [http://python.org/download/](http://python.org/download/) 自由的获取. 这使得 sqlmap 成为一个独立于操作系统的跨平台应用程序. sqlmap 需要 Python 版本为 **2.6.x** 或 **2.7.x**. 为了使它更加容易, 许多 GNU/Linux 发行者推出了安装有 Python 的盒子. 其他如 Unixes 和 Mac OSX 也提供了 Python 安装包并且已可以准备安装了. Windows 用户可以下载并且安装 Python 安装程序适用于 x86, AMD64 and Itanium.

sqlmap 依靠 [Metasploit Framework](http://metasploit.com)来支撑它一些后开发接收的特点. 你可以从 [download](http://metasploit.com/download/) 页面获取复制一份框架 - 需要版本为 **3.5** 或更高. 对于 ICMP tunneling out-of-band takeover 技术, sqlmap 也需要 [Impacket](https://code.google.com/p/impacket/)程序库.

如果您想要直接连接到数据库服务器（交换机“D”）, 而不用经过web应用程序 , 你需要为你想要攻击的数据库管理系统安装 Python 绑定:

* DB2: [python ibm-db](https://code.google.com/p/ibm-db/)
* Firebird: [python-kinterbasdb](http://kinterbasdb.sourceforge.net/)
* Microsoft Access: [python-pyodbc](https://code.google.com/p/pyodbc/)
* Microsoft SQL Server: [python-pymssql](http://code.google.com/p/pymssql/)
* MySQL: [python pymysql](https://github.com/PyMySQL/PyMySQL/)
* Oracle: [python cx_Oracle](http://cx-oracle.sourceforge.net/)
* PostgreSQL: [python-psycopg2](http://initd.org/psycopg/)
* SQLite: [python-pysqlite2](https://code.google.com/p/pysqlite/)
* Sybase: [python-pymssql](http://code.google.com/p/pymssql/)

如果你打算攻击一个在NTLM身份验证背后的web应用程序，你需要安装 [python-ntlm](http://code.google.com/p/python-ntlm/)程序库.

或者, 如果你在 Windows 上运行 sqlmap , 你可能希望安装 [PyReadline](http://ipython.scipy.org/moin/PyReadline/Intro) 程序库来充分利用 SQL shell 和 OS shell 中的 sqlmap TAB 完成和历史支持功能. 请注意这些功能都可以通过标准 Python [readline](http://docs.python.org/library/readline.html) 程序库在其他操作系统上实现.
