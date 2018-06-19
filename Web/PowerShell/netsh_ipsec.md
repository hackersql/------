阻止445端口连接
创建一个策略
1.netsh ipsec static add policy name=BlockPort assign=yes
创建一个空的筛选器列表
2.netsh ipsec static add filterlist name=FilterList_TCP135
3.netsh ipsec static add filterlist name=FilterList_UDP137
4.netsh ipsec static add filterlist name=FilterList_UDP138
5.netsh ipsec static add filterlist name=FilterList_TCP139
6.netsh ipsec static add filterlist name=FilterList_TCP445
将筛选器添加到筛选器列表
7.netsh ipsec static add filter filterlist=FilterList_TCP135 srcaddr=any dstaddr=me mirrored=yes protocol=TCP srcport=0 dstport=135
8.netsh ipsec static add filter filterlist=FilterList_UDP137 srcaddr=any dstaddr=me mirrored=yes protocol=UDP srcport=0 dstport=137
9.netsh ipsec static add filter filterlist=FilterList_UDP138 srcaddr=any dstaddr=me mirrored=yes protocol=UDP srcport=0 dstport=138
10.netsh ipsec static add filter filterlist=FilterList_TCP139 srcaddr=any dstaddr=me mirrored=yes protocol=TCP srcport=0 dstport=139
11.netsh ipsec static add filter filterlist=FilterList_TCP445 srcaddr=any dstaddr=me mirrored=yes protocol=TCP srcport=0 dstport=445
创建一个筛选器操作
12.netsh ipsec static add filteraction name=Block action=block
为指定策略创建一个规则
13.netsh ipsec static add rule name=BlockRule135 policy=BlockPort filterlist=FilterList_TCP135 filteraction=Block conntype=all activate=yes
14.netsh ipsec static add rule name=BlockRule137 policy=BlockPort filterlist=FilterList_UDP137 filteraction=Block conntype=all activate=yes
15.netsh ipsec static add rule name=BlockRule138 policy=BlockPort filterlist=FilterList_UDP138 filteraction=Block conntype=all activate=yes
16.netsh ipsec static add rule name=BlockRule139 policy=BlockPort filterlist=FilterList_TCP139 filteraction=Block conntype=all activate=yes
17.netsh ipsec static add rule name=BlockRule445 policy=BlockPort filterlist=FilterList_TCP445 filteraction=Block conntype=all activate=yes


netsh ipsec static add policy name=BlockPort assign=yes

netsh ipsec static add filterlist name=FilterList_TCP135
netsh ipsec static add filterlist name=FilterList_UDP137
netsh ipsec static add filterlist name=FilterList_UDP138
netsh ipsec static add filterlist name=FilterList_TCP139
netsh ipsec static add filterlist name=FilterList_TCP445

netsh ipsec static add filter filterlist=FilterList_TCP135 srcaddr=any dstaddr=me mirrored=yes protocol=TCP srcport=0 dstport=135
netsh ipsec static add filter filterlist=FilterList_UDP137 srcaddr=any dstaddr=me mirrored=yes protocol=UDP srcport=0 dstport=137
netsh ipsec static add filter filterlist=FilterList_UDP138 srcaddr=any dstaddr=me mirrored=yes protocol=UDP srcport=0 dstport=138
netsh ipsec static add filter filterlist=FilterList_TCP139 srcaddr=any dstaddr=me mirrored=yes protocol=TCP srcport=0 dstport=139
netsh ipsec static add filter filterlist=FilterList_TCP445 srcaddr=any dstaddr=me mirrored=yes protocol=TCP srcport=0 dstport=445

netsh ipsec static add filteraction name=Block action=block

netsh ipsec static add rule name=BlockRule135 policy=BlockPort filterlist=FilterList_TCP135 filteraction=Block conntype=all activate=yes
netsh ipsec static add rule name=BlockRule137 policy=BlockPort filterlist=FilterList_UDP137 filteraction=Block conntype=all activate=yes
netsh ipsec static add rule name=BlockRule138 policy=BlockPort filterlist=FilterList_UDP138 filteraction=Block conntype=all activate=yes
netsh ipsec static add rule name=BlockRule139 policy=BlockPort filterlist=FilterList_TCP139 filteraction=Block conntype=all activate=yes
netsh ipsec static add rule name=BlockRule445 policy=BlockPort filterlist=FilterList_TCP445 filteraction=Block conntype=all activate=yes

顺序：
1.策略add policy--->
2.筛选器列表add filterlist--->
3.将筛选器添加到筛选器列表add filter--->
4.创建一个筛选器操作add filteraction--->
5.为指定策略创建一个规则add rule--->


C:\Users\Administrator>netsh ipsec static

下列指令有效:

此上下文中的命令:
?              - 显示命令列表。
add            - 创建新的策略和有关信息。
delete         - 删除策略和相关信息。
dump           - 显示一个配置脚本。
exportpolicy   - 从证书存储中导出所有策略。
help           - 显示命令列表。
importpolicy   - 从文件导入策略到证书存储。
set            - 更改现存策略和相关信息。
show           - 显示策略和相关信息的详细信息。

C:\Users\Administrator>netsh ipsec static show

下列指令有效:

此上下文中的命令:
show all       - 显示所有策略的详细信息及相关信息。
show filteraction - 显示筛选器操作详细信息。
show filterlist - 显示筛选器列表详细信息。
show gpoassignedpolicy - 显示组分配的策略的详细信息。
show policy    - 显示策略详细信息。
show rule      - 显示规则的详细信息。
show store     - 显示当前策略存储。

C:\Users\Administrator>netsh ipsec static add

下列指令有效:

此上下文中的命令:
add filter     - 将筛选器添加到筛选器列表。
add filteraction - 创建一个筛选器操作。
add filterlist - 创建一个空的筛选器列表。
add policy     - 用默认响应规则创建策略。
add rule       - 为指定策略创建一个规则。

C:\Users\Administrator>netsh ipsec static add filter

用法:
  filter [ filterlist = ] <string>
         [ srcaddr = ] (ipv4 | ipv6 | ipv4-ipv4 | ipv6-ipv6 | dns | server)
         [ dstaddr = ] (ipv4 | ipv6 | ipv4-ipv4 | ipv6-ipv6 | dns | server)
         [ [ description = ] <string> ]
         [ [ protocol = ] (ANY | ICMP | TCP | UDP | RAW | <integer>) ]
         [ [ mirrored = ] (yes  |  no) ]
         [ [ srcmask = ] (mask | prefix) ]
         [ [ dstmask = ] (mask | prefix) ]
         [ [ srcport = ] <port> ]
         [ [ dstport = ] <port> ]

  将筛选器添加到指定的筛选器列表。

参数:

  标记           值
  filterlist    -筛选器要添加到其中的筛选器列表的名称。
  srcaddr       -源 ip 地址(ipv4 或 ipv6)、地址范围、dns 名称或服务器类型。
  dstaddr       -目标 ip 地址(ipv4 或 ipv6)、dns 名称或服务器类型。
  description   -筛选器的简介信息。
  protocol      -可以是 ANY，ICMP，TCP，UDP，RAW，或者一个整数。
  mirrored      -值为 'Yes' 将创建两个筛选器，每个方向均有一个。
  srcmask       -源地址掩码或一个 1 到 32 的前缀。如果 srcaddr 设置为某一范围，则不适用。
  dstmask       -目标地址掩码或一个 1 到 32 的前缀。如果 dstaddr 设置为某一范围，则不适用。
  srcport       -数据包的源端口。值为 0 表示任意端口。
  dstport       -数据包的目标端口。值为 0 表示任意端口。

注释:  1. 如果筛选器列表不存在，将创建它。
       2. 要指定当前计算机地址，请设置 srcaddr/dstaddr=me
          要指定所有计算机地址，请设置 srcaddr/dstaddr=any
       3. 服务器类型可以是 WINS、DNS、DHCP 或 GATEWAY。
       4. 如果源是一个服务器类型，则目标为 "me"，反之亦然。
       5. 如果指定了地址范围，终结点必须为特定地址(非列表或子网)和相同类型地
址(两者均应为 v4 或 v6)。

示例:      1. add filter filterlist=Filter1 192.145.168.0 192.145.168.45
          srcmask=24 dstmask=32
          2. add filter filterlist=Filter1 srcaddr=DHCP dstaddr=0.0.0.0
          protocol=ICMP srcmask=255.255.255.255 dstmask=255.255.255.255
          3. add filter filterlist=Filter1 srcaddr=me dstaddr=any
          4. add filter filterlist=Filter1 srcaddr= E3D7::51F4:9BC8:00A8:6420 dstaddr= ME
          5. add filter filterlist=Filter1 srcaddr= 192.168.2.1-192,168.2.10 dstaddr= ME

C:\Users\Administrator>netsh ipsec static add filteraction

用法:
  filteraction [ name = ] <string>
               [ [ description = ] <string> ]
               [ [ qmpfs = ] (yes | no) ]
               [ [ inpass  = ] (yes | no) ]
               [ [ soft = ] (yes | no) ]
               [ [ action = ] (permit | block | negotiate) ]
               [ [ qmsecmethods = ] (neg#1 neg#2 ... neg#n) ]

  创建一个筛选器操作。

参数:

  标记          值
  name         -筛选器操作的名称。
  description  -筛选器操作类别的简短信息。
  qmpfs        -设置快速模式完全向前保密的选项。
  inpass       -接受不安全的通讯，但是始终用 IPsec响应。
                这接受 yes 或 no。
  soft         -允许与没有 IPsec 的计算机进行不安全的通讯。
                可以是 yes 或 no。
  action       -可以是 permit，block 或 negotiate。
  qmsecmethods -IPsec 提供是下列格式之一:
                ESP[ConfAlg,AuthAlg]:k/s
                AH[HashAlg]:k/s
                AH[HashAlg]+ESP[ConfAlg,AuthAlg]:k/s
                其中 ConfAlg 可以是 DES 或 3DES 或 None
                其中 AuthAlg 可以是 MD5 或 SHA1 或 None
                其中 HashAlg 是 MD5 或 SHA1。
                其中 k 是 Lifetime(千字节)。
                其中 s 是 Lifetime(秒)。

注释: 1. 如果操作不是 negotiate，快速模式安全方法将被忽略
          2. 不推荐使用 DES 和 MD5。提供这些算法
             仅用于向下兼容。

示例: add filteraction name=FilterA qmpfs=yes soft=y action=negotiate
          qmsec="AH[MD5]:204800k/300s ESP[DES,SHA1]:30000k/480s"

C:\Users\Administrator>netsh ipsec static add filterlist

用法:
  filterlist [ name = ] <string>
             [ [ description = ] <string> ]

  用指定名称创建一个空的筛选器列表。

参数:

  标记          值
  name         -筛选器列表的名称。
  description  -筛选器列表的简短信息。

注释:

示例: add filterlist Filter1

C:\Users\Administrator>netsh ipsec static add policy

用法:
  policy [ name = ] <string>
         [ [ description = ] <string> ]
         [ [ mmpfs = ] (yes | no) ]
         [ [ qmpermm = ] <integer> ]
         [ [ mmlifetime = ] <integer> ]
         [ [ activatedefaultrule = ] (yes | no) ]
         [ [ pollinginterval = ] <integer> ]
         [ [ assign = ] (yes | no) ]
         [ [ mmsecmethods = ] (sec#1 sec#2 ... sec#n) ]

  用指定名称创建一个策略。

参数:

  标记                  值
  name                 -策略的名称。
  description          -策略的简短信息。
  mmpfs                -设置主完全向前保密的选项。
  qmpermm              -每一 IKE 主模式会话的快速模式会话数目。
  mmlifetime           -为 IKE 的主模式重新生成密钥所需时间(以分钟计)。
  activatedefaultrule  -激活或禁用默认响应规则。 只在 Windows Vista 之前的
                        Windows 版本上有效。
  pollinginterval      -轮询间隔，策略代理在策略存储中
                        查找更改的间隔时间(以分钟计)。
  assign               -指定策略为活动或非活动。
  mmsecmethods         -一个或多个由空格分隔开的安全方法列表，安全方法的格式为
                        ConfAlg-HashAlg-GroupNum，其中 ConfAlg 可以是 DES 或
                        3DES，HashAlg 是 MD5 或 SHA1。
                        GroupNum 可以是 1 (低)、2 (中)、3 (DH2048)。

注释:     1. 如果指定了 mmpfs，qmpermm 将设置为 1。
          2. 如果存储为 "domain"，则 "assign" 将不起作用。
          3. 不推荐使用 DES 和 MD5。提供这些算法仅用于向下兼容。

示例:      add policy Policy1 mmpfs= yes assign=yes
          mmsec="3DES-SHA1-3 DES-MD5-3 3DES-MD5-2"

C:\Users\Administrator>netsh ipsec static add rule

用法:
  rule [ name = ] <string>
       [ policy = ] <string>
       [ filterlist = ] <string>
       [ filteraction = ] <string>
       [ [ tunnel = ] (ip | dns) ]
       [ [ conntype = ] (lan | dialup | all) ]
       [ [ activate = ] (yes | no) ]
       [ [ description = ] <string> ]
       [ [ kerberos = ] (yes | no) ]
       [ [ psk = ] <preshared key> ]
       [ [ rootca = ] "<certificate> certmap:(yes | no) excludecaname:(yes | no)" ]

  用指定的筛选器列表和筛选器操作创建一个规则。

参数:

  标记           值
  name          -规则的名称。
  policy        -规则所属的策略的名称。
  filterlist    -要使用的筛选器列表的名称。
  filteraction  -要使用的筛选器操作的名称。
  tunnel        -隧道终结点 IP 地址。
  conntype      -连接类型可以是 lan，dialup 或 all。
  activate      -如果指定了 yes，则激活策略中的规则。
  description   -规则的简短信息。
  kerberos      -如果指定了 yes，则提供 Kerberos 身份验证。
  psk           -用预共享密钥提供身份验证。
  rootca        -用指定的根证书提供身份验证，如果指定了
                 certmap:Yes，将尝试映射此证书
                 如果指定了 excludecaname:Yes，将排除 CA 名称

注释:     1. 证书，映射和 CA 名称设置要在引号中引起来，内嵌的引号将
             被“\'”所代替。
          2. 证书映射只对域成员有效。
          3. 可以多次使用 rootca 参数来提供多重证书。
          4. 每种身份验证方法的优先级由在命令中的顺序来决定。
          5. 如果没有指定身份验证方法，将使用动态默认。
          6. 排除根证书颁发机构(CA)名称防止将名称作为证书请求的一部分
             发送。

示例:     add rule name=Rule policy=Policy filterlist=Filterlist
          filteraction=FilterAction kerberos=yes psk="my key"
          rootca="C=US,O=MSFT,CN=Microsoft Authenticode(tm) Root Authority"
          rootca="C=US,O=MSFT,CN=\’Microsoft North, South, East, and West Root
          Authority\’ certmap:yes excludecaname:no"

C:\Users\Administrator>netsh ipsec static set

下列指令有效:

此上下文中的命令:
set batch      - 设置批更新模式。
set defaultrule - 更改默认响应规则。
set filteraction - 更改筛选器操作。
set filterlist - 更改筛选器列表。
set policy     - 更改策略。
set rule       - 更改规则。
set store      - 设置当前策略存储。

C:\Users\Administrator>netsh ipsec static delete

下列指令有效:

此上下文中的命令:
delete all     - 删除所有策略，筛选器列表和筛选器操作。
delete filter  - 从筛选器列表中删除一个筛选器。
delete filteraction - 删除一个筛选器操作。
delete filterlist - 删除一个筛选器列表。
delete policy  - 删除一个策略和它的规则。
delete rule    - 从策略中删除一个规则。

