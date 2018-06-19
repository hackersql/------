# PowerShell WMI 备忘录

# 什么是CIM/WMI？
CIM：公共信息模型（CIM）是用于描述受管理资源（如存储，网络或软件组件）的结构和行为的DMTF标准[DSP0004]。

WMI：Windows Management Instrumentation（WMI）是一种在Windows上实现CIM标准的CIM服务器。

# 什么是WS-Man/WinRM？
WS-Man：WS-Management（WS-Man）协议是一种基于SOAP的防火墙友好协议，用于管理客户端与CIM服务器进行通信。
WinRM：Windows远程管理（WinRM）是Windows上的WS-Man协议的Microsoft实现。

# 什么是WQL?
管理客户端使用WMI查询语言（WQL）来查询WMI中的数据。

WQL与由DMTF定义的CIM查询语言（CQL）非常相似，但不完全相同。

# 什么是新的CIM Cmdlet？
PowerShell 2.0随WMI和WsMan cmdlet一起提供。 

#### 为什么要在3.0中有另一组cmdlet？

WMI cmdlet（如Get-WmiObject）可以在DCOM上运行，并且仅适用于WMI/Windows。

WsMan cmdlet（如Get-WsManInstance）通过WS-Man协议工作，但它们对于系统管理人员不是友好的。

新的Cim cmdlet提供了两全其美的功能

- 丰富的PowerShell体验，不再需要XML
- 通过WsMan（远程默认）和DCOM（本地默认）
- 使用实现WSMan协议的非Windows设备
- 简化WMI中类名称空间的发现

Win8中仍然支持旧的WMI和WsMan Cmdlet。 很容易将脚本更改为新的基于标准的CIM cmdlet。

获取CIM cmdlet的列表
Get-Command -Module CimCmdlets

# 什么是关联？
关联表示受管理资源的两个或多个实例（如磁盘和卷或目录和文件）之间的关系。 

给定一个类的实例，CIM服务器将返回与给定实例相关的所有实例。 

您也可以通过指定目标类或关联关系的名称来过滤结果。

# 什么是各种CIM操作？
CIM类应实现在其规范中明确定义的方法（称为外部方法）和一组标准的预定义方法。

预定义的方法称为内在的，它们是

- 枚举一个类的实例
- 枚举关联的实例
- 通过在服务器上执行查询来获取实例
- 获取一个类的特定实例
- 创建一个新的类实例
- 修改一个类的实例
- 删除一个类的实例
- 在类或实例上调用外部方法
- 枚举名称空间中的类
- 获取类架构
- 订阅指示
- 退订指示

您会注意到CIM cmdlet是基于CIM操作进行建模的。

# 什么是CIM指示？
CIM指示是受管理系统中事件的表示。 

CIM客户端可以通过提供指示类型和过滤表达式来订阅接收指示，该指示类型和过滤表达式选择将传送给客户端的事件。

# 什么是CimSession
CimSession表示与CIM服务器的连接。

CimSession并没有与服务器建立物理永久连接，所以CimSession是一个非常轻量级的客户端连接对象。

CimSession可以用来管理任何支持WsMan协议的服务器。

# 创建基于CIM的cmdlet
开发人员和高级IT专业人员可以使用CDXML来包装现有的CIM类，以提供更友好的PS任务抽象。

有关详细信息，请[参阅](https://social.msdn.microsoft.com/Search/en-US?query=cim&beta=0&rn=PowerShell+Team+Blog&rq=site:https://blogs.msdn.microsoft.com/powershell&ac=4)（原链接以失效）。

开发人员可以通过实现CIM类并编写CDXML来使用本地代码来创建cmdlet。

# 更多信息
WMI博客：[http://blogs.msdn.com/b/wmi/](http://blogs.msdn.com/b/wmi/)

PowerShell博客：[http://blogs.msdn.com/b/powershell/](http://blogs.msdn.com/b/powershell/)

脚本中心：[http://technet.microsoft.com/enus/scriptcenter/bb410849](http://technet.microsoft.com/enus/scriptcenter/bb410849)

脚本专家：[http://blogs.technet.com/b/heyscriptingguy/](http://blogs.technet.com/b/heyscriptingguy/)

# 在WMI中查找命名空间和类
## 在PowerShell 3.0中发布的新CIM Cmdlet使得发现WMI命名空间和类变得更加容易。
对`CIM Cmdlet`参数使用`Tab`完成（ISE中的`Tab + Space`显示下拉菜单）

### 查找顶级命名空间

`Get-CimInstance –Namespace <Tab> `
###使用`Tab`完成类名补全
###如果未指定命名空间, 则显示默认`root/cimv2`命名空间中的类
`Get-CimInstance -ClassName *Bios<Tab>`

`Get-CimInstance –Namespace root/Microsoft/Windows/smb –ClassName <tab>`

##### 注意：使用Tab补全仅适用于本地机器。

### 使用`Get-CimClass`进行高级类搜索

### 列出root/cimv2命名空间中的所有类
`Get-CimClass`
### 列出包含`Stop*`方法的类
`Get-CimClass -MethodName Stop*`
### 列出具有名为`Handle`属性的类
`Get-CimClass -PropertyName Handle `
### 查找以`*Partition`结尾具有`Association`限定符的类
`Get-CimClass -ClassName *Partition -QualifierName Association`

`Get-CimClass -Namespace root/Microsoft/Windows/smb -class *Smb* -QualifierName Indication`
### 注意：`Get-CimClass`仅适用于支持Schema检索操作的计算机

---
# 从WMI获取数据
### 查找Win32_Service类的实例
`Get-CimInstance -ClassName Win32_Service` 
Get-CimInstance通过Microsoft.Management.Infrastructure.CimInstance#<ClassName>输出

### 通过WQL查询获取数据
`Get-CimInstance -Query "Select * from Win32_Service Where Name like 'app%'"`
### 仅获取属性的子集 - 通常用于减少网络/内存占用量
`Get-CimInstance -ClassName Win32_Service -KeyOnly`

`Get-CimInstance -ClassName Win32_Service -Property Name,Status`
### 变量$A Cim实例中保存的是客户端上服务器对象状态的快照
`$a = Get-CimInstance -ClassName Win32_Process`
#### 注意：作为输入对象其传递的对象不会更改
`Get-CimInstance -InputObject $a[0] `
### 如果您有使用WMI cmdlet的脚本，则可以轻松将它们迁移到新的CIM Cmdlet

---
# Peeping into CimInstance
### CimInstance类具有以下属性
### `.CimInstanceProperties` - 这个类的属性列表
### `.CimClass` - CIM为这个类提供的模式
### `.CimClass.CimClassMethods` - 这个类支持的方法
### `.CimSystemProperties` - 类似命名空间的系统属性
#### 注意:为使Cim Schema准确，CIM Server必须支持类模式检索操作。
### CimInstance是可移植的 - 支持完整的序列化和反序列化
```
Get-CimInstance Win32_Service -Filter 'Name Like "app%"|export-clixml t1.xml

$x = import-clixml .\t1.xml

$x[0].pstypenames

diff ($x) (Get-CimInstance win32_service -Filter 'Name Like "app%"')
```
---
# Working with Associations
### 使用过滤条件`DriveType==3` (硬盘驱动器)获取`Win32_LogicalDisk`类的实例
`$disk1, $diskn = Get-CimInstance -class Win32_LogicalDisk -Filter 'DriveType = 3'`
### 获取关联的实例 disk1
`Get-CimAssociatedInstance -CimInstance $disk1`
### 给定一个Win32_LogicalDisk的实例，给出特定类型的关联实例
`Get-CimAssociatedInstance -CimInstance $disk1 -ResultClassName Win32_DiskPartition`

### 查找WinRM服务所依赖的服务
`$service = Get-CimInstance Win32_Service -Filter 'Name Like "winrm%"'`

`Get-CimAssociatedInstance -InputObject $service -Association Win32_DependentService`

---
# 调用CIM方法
### 查看一个类中有哪些方法
`$c = Get-CimClass Win32_Process`
### 你也可以使用`CimInstance`的`.CimClass`属性
`$c.CimClassMethods`
### 在实例上调用一个方法
`$a = Get-CimInstance Win32_Process -Filter "Name Like 'PowerShell%'"`
### $a绑定到InputObject参数
`$a | Invoke-CimMethod -MethodName GetOwner` 
### 调用类静态方法 - icim是Invoke-CimMethod的别名
`icim -ClassName Win32_Process -MethodName Create -Arguments @{CommandLine="calc.exe"}`

---
# 执行CIM操作
### 创建一个实例 - CIM内部支持创建、修改、删除实例方法
`New-CimInstance -Class Win32_Environment -Property @{Name="testvar"; VariableValue="testvalue"; UserName="fareast\osajid"}`
### 修改一个实例
`$a = Get-CimInstance -Class Win32_Environment -Filter "Name='testvar'" #; VariableValue="testvalue"; UserName="fareast\osajid"}`

`Set-CimInstance -InputObject $a -Property @{VariableValue="ChangedValue"} –PassThru`
### 相同的结果可以通过设置$a的VariableValue属性来实现
### 要更新服务器上的对象，请调用Set-CimInstance
`$a.VariableValue="ChangedValue"`

`Set-CimInstance -InputObject $a -PassThru`
### 删除一个实例
`Remove-CimInstance -InputObject $a`

---
# 事件 – CIM Indications
`$filter = "SELECT * FROM CIM_InstModification WHERE TargetInstance ISA 'Win32_LocalTime'"`
### 使用过滤器订阅事件
`Register-CimIndicationEvent -Query $filter -SourceIdentifier "Timer"`
### 使用PowerShell事件机制获取事件
`Get-Event -SourceIdentifier Timer`

`Unregister-Event -SourceIdentifier "Timer"`
### 订阅该事件
`$Action = {$process = $Event.SourceEventArgs.NewEvent;write-host New process Name = $process.ProcessName Id = $process.ProcessId }`

`Register-CimIndicationEvent -ClassName Win32_ProcessStartTrace -Action $Action -SourceIdentifier "ProcessWatch"`

`Unregister-Event -SourceIdentifier "ProcessWatch"`

---
# Working with remote servers
### CIM Cmdlet具有`-ComputerName`和`-CimSession`参数，用于管理远程服务器
`Get-CimInstance Win32_Service -ComputerName Server1`

默认情况下，在传递ComputerName时使用WsMan协议（包括localhost或127.0.0.1）

### 如果对同一台服务器执行多个操作，建议创建一个CimSession
`$s = New-CimSession -CN server1`

`gcim Win32_Service -CimSession $s`
### 管理低级别的Windows服务器
### 有两种方法可以管理低级别Windows服务器
### 安装Windows Management Framework 3.0（推荐）或使用DCOM协议
`$so = New-CimSessionOption -Protocol DCOM`
`$s = New-CimSession -CN server1 -SessionOption $so`
`Get-CimInstance Win32_Service -CimSession $s`
### CimInstance的PSComputerName属性显示源计算机名称
gcim Win32_Process -CN server1,server2 | Select Name, PsComputerName
### 如果传递CN（ComputerName）或CimSession来获取CimInstance，则不必为后续操作再次指定它。
`gcim Win32_Process -CN server1,server2 | icim -MethodName GetOwner`
