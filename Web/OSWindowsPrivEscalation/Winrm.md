C:\Windows\System32>winrm /?
Windows 远程管理命令行工具

Windows 远程管理(WinRM)是 WS-Management 协议的 Microsoft 实现，
该协议为使用 Web 服务的本地计算机和远程计算机
之间的通信提供了一种安全的方式。

使用情况:
  winrm OPERATION RESOURCE_URI [-SWITCH:VALUE [-SWITCH:VALUE] ...]
        [@{KEY=VALUE[;KEY=VALUE]...}]

有关特定操作的帮助:
  winrm g[et] -?        检索管理信息。
  winrm s[et] -?        修改管理信息。
  winrm c[reate] -?     创建管理资源的新实例。
  winrm d[elete] -?     删除管理资源的实例。
  winrm e[numerate] -?  列出管理资源的所有实例。
  winrm i[nvoke] -?     执行管理资源上的方法。
  winrm id[entify] -?   确定 WS-Management 实现是否
                        正在远程计算机上运行。
  winrm quickconfig -?  对该计算机进行配置以接受其他计算机的
                          WS-Management　的请求。
  winrm configSDDL -?   修改 URI 的现有安全描述符。
  winrm helpmsg -?      显示错误消息的错误代码。

有关相关主题的帮助:
  winrm help uris       创建资源 URI 的方式。
  winrm help aliases    URI 的缩写。
  winrm help config     配置 WinRM 客户端和服务设置。
  winrm help certmapping 配置客户端证书访问。
  winrm help remoting   访问远程计算机的方式。
  winrm help auth       提供远程访问的凭据。
  winrm help input      提供输入以进行创建、设置和调用。
  winrm help switches   其他开关，例如格式化、选项等等。
  winrm help proxy      提供代理信息。

C:\Windows\System32>winrm g -?
Windows 远程管理命令行工具

winrm get RESOURCE_URI [-SWITCH:VALUE [-SWITCH:VALUE] ...]

使用指定的选项和键值对检索
 RESOURCE_URI 的实例。

示例: 用 XML 格式检索当前配置:
  winrm get winrm/config -format:pretty

示例: 检索 Win32_Service 类的 spooler 实例:
  winrm get wmicimv2/Win32_Service?Name=spooler

示例: 检索此计算机上的 certmapping 项:
  winrm get winrm/config/service/certmapping?Issuer=1212131238d84023982e381f2039
1a2935301923+Subject=*.example.com+URI=wmicimv2/*

C:\Windows\System32>winrm s -?
Windows 远程管理命令行工具

winrm set RESOURCE_URI [-SWITCH:VALUE [-SWITCH:VALUE] ...]
          [@{KEY="VALUE"[;KEY="VALUE"]}]
          [-file:VALUE]

通过键值对使用指定的开关和已更改的值的输入，
或通过输入文件使用已更新的对象
修改 RESOURCE_URI 中的设置。

示例: 修改 WinRM 的配置属性:
  winrm set winrm/config @{MaxEnvelopeSizekb="100"}

示例: 禁用该计算机上的侦听程序:
  winrm set winrm/config/Listener?Address=*+Transport=HTTPS @{Enabled="false"}

示例: 禁用此计算机上的 certmapping 项:
  Winrm set winrm/config/service/certmapping?Issuer=1212131238d84023982e381f2039
1a2935301923+Subject=*.example.com+URI=wmicimv2/* @{Enabled="false"}

C:\Windows\System32>winrm c -?
Windows 远程管理命令行工具

winrm create RESOURCE_URI [-SWITCH:VALUE [-SWITCH:VALUE] ...]
             [@{KEY="VALUE"[;KEY="VALUE"]}]
             [-file:VALUE]

使用指定的键值对或输入文件
生成 RESOURCE_URI 的实例。

示例: 创建 IPv6 地址上的 HTTP 侦听程序实例:
  winrm create winrm/config/Listener?Address=IP:3ffe:8311:ffff:f2c1::5e61+Transport=HTTP

示例: 创建所有 IP 上的 HTTPS 侦听程序实例:
  winrm create winrm/config/Listener?Address=*+Transport=HTTPS @{Hostname="HOST";CertificateThumbprint="XXXXXXXXXX"}
注意: XXXXXXXXXX 代表 40 位的十六进制字符串；请参阅 help config。

示例: 从 xml 创建 windows shell 命令实例:
  winrm create shell/cmd -file:shell.xml -remote:srv.corp.com

示例: 创建 CertMapping 项:
  winrm create winrm/config/service/certmapping?Issuer=1212131238d84023982e381f2
0391a2935301923+Subject=*.example.com+URI=wmicimv2/* @{UserName="USERNAME";Password="PASSWORD"} -remote:localhost

C:\Windows\System32>winrm quickconfig -?
Windows 远程管理命令行工具

winrm quickconfig [-quiet] [-transport:VALUE] [-force]

执行配置操作以使此计算机能够进行远程管理。
其中包括:
1. 启动 WinRM 服务
2. 将 WinRM 服务类型设置为自动启动
3. 创建侦听程序以接受任意 IP 地址上的请求
4. 为 WS-Management 通信启用防火墙例外(仅适用于 http)

-q[uiet]
--------
如果存在，quickconfig 将不提示确认。

-transport:VALUE
----------------
为特定传输执行 quickconfig。
可能的选项有 http 和 https。默认为 http。

-force
--------
如果存在，quickconfig 将不提示确认并启用
防火墙例外，而不考虑当前的网络配置文件设置。

另请参阅:
  winrm help config

C:\Windows\System32>winrm help config
Windows 远程管理命令行工具

使用 winrm 命令行或通过 GPO 管理 WinRM 的配置。
配置同时包括客户端和服务的全局配置。

WinRM 服务至少需要一个侦听程序以表示 IP 地址，
以接受该地址上的 WS-Management 请求。
例如，如果计算机具备多个网卡，则可将 WinRM 配置为仅接受
这些网卡其中之一的请求。

全局配置
  winrm get winrm/config
  winrm get winrm/config/client
  winrm get winrm/config/service
  winrm enumerate winrm/config/resource
  winrm enumerate winrm/config/listener
  winrm enumerate winrm/config/plugin
  winrm enumerate winrm/config/service/certmapping

网络侦听需要一个或多个侦听程序。
侦听程序由两个选择器识别: Address 和 Transport。

Address 必须是以下内容之一:
  *           - 侦听计算机上的所有 IP
  IP:1.2.3.4  - 仅侦听指定的 IP 地址
  MAC:...     - 仅侦听指定 MAC 的 IP 地址。

注意: 所有侦听受制于 IPv4Filter 和 IPv6Filter (在
config/service.
注意: IP 可能为 IPv4 地址或 IPv6 地址。


传输必须为以下内容之一:
  HTTP - 侦听 HTTP (默认端口为 5985)上的请求
  HTTPS - 侦听 HTTPS (默认端口为 5986)上的请求

注意: 默认情况下 HTTP 流量仅允许
用 Negotiate 或 Kerberos SSP 加密的消息。


配置 HTTPS 时，使用以下属性:
  Hostname - 该计算机的名称；必须与证书中的 CN 匹配。
  CertificateThumbprint - 适用于服务器身份验证的证书
    的十六进制指纹。
注意: 如果仅提供 Hostname，则 WinRM 将试图找到对应的
证书。

示例: 侦听计算机上所有 IP 的 HTTP 请求:
  winrm create winrm/config/listener?Address=*+Transport=HTTP

示例: 禁用给定的侦听程序
  winrm set winrm/config/listener?Address=IP:1.2.3.4+Transport=HTTP @{Enabled
alse"}

示例: 启用客户端而非服务上的基本身份验证:
  winrm set winrm/config/client/auth @{Basic="true"}

示例: 为所有工作组计算机启用 Negotiate。
  winrm set winrm/config/client @{TrustedHosts="<local>"}

另请参阅:
  winrm help uris
  winrm help aliases
  winrm help certmapping
  winrm help input
  winrm help switches

C:\Windows\System32>winrm help uris
Windows 远程管理命令行工具

统一资源标识符(URI)指定要用于操作的
管理资源。

选择器和值在 URI 之后用以下格式传递:
  RESOURCE_URI?NAME=VALUE[+NAME=VALUE]...

WMI 中所有信息的 URI 均为以下格式:
  WMI path = \\root\NAMESPACE[\NAMESPACE]\CLASS
  URI      = http://schemas.microsoft.com/wbem/wsman/1/wmi/root/NAMESPACE[/NAMESPACE]/CLASS
  ALIAS    = wmi/root/NAMESPACE[/NAMESPACE]/CLASS

示例: 使用单一选择器获取有关 WMI 的 WinRM 服务的信息
  WMI path = \\root\cimv2\Win32_Service
  URI      = http://schemas.microsoft.com/wbem/wsman/1/wmi/root/cimv2/Win32_Serv
ice?Name=WinRM
  ALIAS    = wmi/root/cimv2/Win32_Service?Name=WinRM

使用 WQL 筛选器枚举 WMI 实例时，
CLASS 必须为 "*" (星号)并且不应指定任何选择器。
示例:
URI = http://schemas.microsoft.com/wbem/wsman/1/wmi/root/cimv2/*

访问 WMI singleton 实例时，不应指定任何选择器。
示例:
URI = http://schemas.microsoft.com/wbem/wsman/1/wmi/root/cimv2/Win32_Service

注意: RESOURCE_URI 的某些部份可能区分大小写。使用 create 或
invoke 时，资源 URI 的最后部份必须与期望的 XML 的顶级元素
的大小写匹配。

另请参阅:
  winrm help uris
  winrm help aliases
  winrm help input
  winrm help switches

C:\Windows\System32>winrm help aliases
Windows 远程管理命令行工具

别名允许使用缩写代替完整资源 URI。
可用的别名以及它们代替的 URI 为:

wmi      = http://schemas.microsoft.com/wbem/wsman/1/wmi
wmicimv2 = http://schemas.microsoft.com/wbem/wsman/1/wmi/root/cimv2
cimv2    = http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2
winrm    = http://schemas.microsoft.com/wbem/wsman/1
wsman    = http://schemas.microsoft.com/wbem/wsman/1
shell    = http://schemas.microsoft.com/wbem/wsman/1/windows/shell

示例: 使用完整资源 URI:
  winrm get http://schemas.microsoft.com/wbem/wsman/1/wmi/root/cimv2/Win32_Servi
ce?Name=WinRM

示例: 使用别名:
  winrm get wmicimv2/Win32_Service?Name=WinRM

C:\Windows\System32>winrm help remoting
Windows 远程管理命令行工具

winrm OPERATION -remote:VALUE [-unencrypted] [-usessl]

-r[emote]:VALUE
---------------
指定远程终点/系统的标识符。
可以是简单主机名或完整 URL。

  [TRANSPORT://]HOST[:PORT][/PREFIX]

传输: HTTP 或 HTTPS 之一；默认值为 HTTP。
主机: 格式可以为 DNS 名称、NetBIOS 名称或 IP 地址。
端口: 如果没有指定端口，则将应用下列默认规则:
        * 如果指定通过 HTTP 进行传输，则将使用端口 80。
        * 如果指定通过 HTTPS 进行传输，则将使用端口 443。
        * 如果没有指定传输，也没有指定 -usessl，
          则将使用端口 5985 进行 HTTP 连接。
        * 如果没有指定传输，而指定了 -usessl，
          则将使用端口 5986 进行 HTTPS 连接。
前缀: 默认值为 wsman。

注意: IPv6 地址必须包括在括号中。
注意: 使用 HTTPS 时，计算机名称必须与服务器的证书公用名称(CN)
      相匹配，除非使用 -skipCNcheck。
注意: 端口和前缀的默认值可以在本地配置中进行更改。

示例: 通过 http 连接到 srv.corp.com:
  winrm get uri -r:srv.corp.com

示例: 通过 https 连接到本地计算机 machine1:
  winrm get uri -r:https://machine1

示例: 通过 http 连接到 IPv6 计算机:
  winrm get uri -r:[1:2:3::8]

示例: 通过非默认端口和 URL 上的 https 连接到 IPv6 计算机:
  winrm get uri -r:https://[1:2:3::8]:444/path

-un[encrypted]
--------------
指定通过 HTTP 执行远程操作时不使用任何加密。
默认情况下不允许未加密的流量，
并且必须在本地配置中启用这项。

-[use]ssl
---------
指定在执行远程操作时将使用 SSL 连接。
不应指定远程选项中的传输。

若要对该计算机进行远程管理，请参阅:
  winrm help config

另请参阅:
  winrm help uris
  winrm help aliases
  winrm help input
  winrm help switches

C:\Windows\System32>winrm help input
Windows 远程管理命令行工具

输入可以是在命令行上直接提供键/值对
或从文件中读取 XML。

  winrm OPERATION -file:VALUE
  winrm OPERATION @{KEY="VALUE"[;KEY="VALUE"]}

适用于设置、创建和调用操作。
使用 @{KEY=VALUE} 或者使用来自 XML 文件的输入，但不同时使用这两者。

-file:VALUE
-----------
指定用作输入的文件的名称。
VALUE 可以是绝对路径、相对路径或不带路径的文件名。
包含空格的名称或路径必须用引号括起来。

@{KEY="VALUE"[;KEY="VALUE"]}
----------------------------
关键字不唯一。
值必须在引号中。
$null 是一个特殊值。

示例:
  @{key1="value1";key2="value2"}
  @{key1=$null;key2="value2"}

另请参阅:
  winrm set -?
  winrm create -?
  winrm invoke -?

C:\Windows\System32>winrm help certmapping
Windows 远程管理命令行工具

使用客户端证书将远程访问映射到 WinRM 的证书
存储在以下资源 URI 所标识的
证书映射表中:

 winrm/config/service/CertMapping

此表中的每个项目都包含五个属性:
 Issuer -  颁发者证书的指纹。
 Subject - 客户端证书的使用者字段。
 URI - 应用此映射的 URI 或 URI 前缀。
 Username - 用于处理请求的本地用户名。
 Password - 用于处理请求的本地密码。
 Enabled - 如果为 true，在处理时使用该选项。

对于要应用的客户端证书，颁发者证书必须
可以在本地使用，并且与项目的颁发者属性中的指纹相匹配

对于要应用的客户端证书，其 DNS 或主体名称
(来自 SubjectAlternativeName 字段)必须与 Subject 属性相匹配。
值可以以通配符 '*' 开始。
URI 标识所示客户端证书
应该映射的资源。
值可以以通配符 "*" 结束。

如果客户端证书与该项匹配并且已启用，
在确保用户有权访问 URI 安全表定义的资源以后，
使用给定用户名和密码在本地帐户下
处理请求。

创建新项目或更改现有项目的密码时，
由于 WinRM 服务必须存储密码以供将来使用，因此必须
使用 -r 开关。

示例: 查看当前 CertMapping 配置
  winrm enumerate winrm/config/service/CertMapping

示例: 创建 CertMapping 项:
  winrm create winrm/config/service/certmapping?Issuer=1212131238d84023982e381f2
0391a2935301923+Subject=*.example.com+URI=wmicimv2/* @{UserName="USERNAME";Passw
ord="PASSWORD"} -remote:localhost

C:\Windows\System32>winrm help switches
Windows 远程管理命令行工具

-timeout:MS
-----------
超时(毫秒)。限制相应操作的持续时间。
可以按以下格式配置默认超时:
  winrm set winrm/config @{MaxTimeoutms="XXXXXX"}
其中 XXXXXX 是表示毫秒的整数。

-skipCAcheck
------------
指定证书颁发者不必是受信任的根授权机构。
仅在使用 HTTPS 的远程操作中使用(参见 -remote 选项)。
应仅对受信任的计算机使用此选项。

-skipCNcheck
------------
指定服务器的证书公用名(CN)不必与
服务器的主机名匹配。
仅在使用 HTTPS 的远程操作中使用(参见 -remote 选项)。
应仅对受信任的计算机使用此选项。

-skipRevocationcheck
-------------------
指定不检查服务器证书的吊销状态。
仅在使用 HTTPS 的远程操作中使用(参见 -remote 选项)。
应仅对受信任的计算机使用此选项。

-defaultCreds
-------------------
指定当使用协商时允许隐式凭据。
仅在使用 HTTPS 的远程操作中才允许(参见 - remote 选项)。

-dialect:VALUE
--------------
用于枚举或片断的筛选器表达式的方言。
示例: 使用 WQL 查询
  -dialect:http://schemas.microsoft.com/wbem/wsman/1/WQL
示例: 将 XPATH 用于使用枚举或碎片 get/set 进行的筛选。
  -dialect:http://www.w3.org/TR/1999/REC-xpath-19991116

-fragment:VALUE
---------------
指定位于实例 XML 中的部份，该实例 XML 将要为给定操作
进行更新或检索。
示例: 获取后台打印程序服务的状态
  winrm get wmicimv2/Win32_Service?name=spooler -fragment:Status/text()

-options:{KEY="VALUE"[;KEY="VALUE"]}
------------------------------------
特定提供程序选项的键/值对。
若要将 NULL 指定为一个值，请使用 $null

示例:
  -options:{key1="value1";key2="value2"}
  -options:{key1=$null;key2="value2"}

-SPNPort
--------
将端口号附加到远程服务器的服务主体名称(SPN)上。
使用 Negotiate 或 Kerberos 身份验证机制时
会使用服务主体名称。

-encoding:VALUE
---------------
指定与远程计算机通讯时使用的编码类型(请参阅 -remote
选项)。可能的选项有 "utf-8" 和 "utf-16"。
默认值为 utf-8。
示例:
  -encoding:utf-8
  -encoding:utf-16

-f[ormat]:FORMAT
----------------
指定输出的格式。
FORMAT 可以是 "xml"、"pretty" (格式更好的 XML)或 "text"。
示例:
  -format:xml
  -format:pretty
  -format:text