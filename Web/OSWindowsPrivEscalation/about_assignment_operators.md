简短的介绍
描述如何使用运算符为变量赋值。

详细描述
赋值运算符将一个或多个值分配给变量。他们可以在赋值之前对值执行数字操作。

Windows PowerShell支持以下赋值运算符。

操作者 描述
=       将变量的值设置为指定的值。
+=      将变量的值增加指定的值，或将指定值附加到现有值。
-=      按指定值减小变量的值。
*=      将变量的值乘以指定的值，或将指定值附加到现有值。
/=      将变量的值除以指定的值。
%=      将变量的值除以指定的值和然后将余数（模数）赋给变量。
++      增加变量，可指定属性或值的值数组元素由1。
-       减少变量，可分配属性或的值数组元素由1。

句法
赋值运算符的语法如下：

<assignable-expression> <assignment-operator> <value>

可分配表达式包括变量和属性。值可以是单个值，值数组或命令，表达式或语句。

递增和递减运算符是一元运算符。每个都有前缀和后缀版本。

<assignable-expression><operator> <operator><assignable-expression>

可分配表达式必须是数字，或者必须可转换为数字。

分配值
变量被命名为存储值的存储空间。您可以使用赋值运算符将值存储在变量中=。新值可以替换变量的现有值，也可以将新值附加到现有值。

基本赋值运算符是等号= (ASCII 61)。例如，以下语句将值为Windows PowerShell分配给$ MyShell变量：
$MyShell = "Windows PowerShell"
在Windows PowerShell中为变量赋值时，如果该变量尚不存在，则创建该变量。例如，以下两个分配语句中的第一个创建$ a变量并将值6赋值给$ a。第二个赋值语句为$ a赋值12。第一个语句创建一个新变量。第二个语句仅更改其值：
$a = 6
$a = 12
除非转换它们，否则Windows PowerShell中的变量没有特定的数据类型。当变量只包含一个对象时，该变量将采用该对象的数据类型。当变量包含对象集合时，该变量具有System.Object数据类型。因此，您可以将任何类型的对象分配给集合。以下示例显示您可以将流程对象，服务对象，字符串和整数添加到变量而不会生成错误：
$a = Get-Process
$a += Get-Service
$a += "string"
$a += 12
由于赋值运算符=的优先级低于管道运算符|，因此不需要括号将命令管道的结果分配给变量。例如，以下命令对计算机上的服务进行排序，然后将已排序的服务分配给$ a变量：
$a = Get-Service | Sort-Object -Property name
您还可以将语句创建的值分配给变量，如以下示例所示：
$a = if ($b -lt 0) { 0 } else { $b }
如果$ b的值小于零，则此示例将$ a赋值给零。如果$ b的值不小于零，它会将$ b的值分配给$ a。

分配操作员
赋值运算符=为变量赋值。如果变量已有值，则赋值运算符=将替换该值而不发出警告。

以下语句将整数值6分配给$ a变量：
$a = 6
要将字符串值赋给变量，请将字符串值括在引号中，如下所示：
$a = "baseball"
要为变量分配数组（多个值），请使用逗号分隔值，如下所示：
$a = "apple", "orange", "lemon", "grape"
要将哈希表分配给变量，请在Windows PowerShell中使用标准哈希表表示法。键入at符号，@后跟键/值对，用分号分隔;并括在大括号中{ }。例如，要将哈希表分配给$ a变量，请键入：
$a = @{one=1; two=2; three=3}
要将十六进制值分配给变量，请在值前面加上0x。Windows PowerShell将十六进制值（0x10）转换为十进制值（在本例中为16），并将该值分配给$ a变量。例如，要为$ a变量赋值0x10，请键入：
$a = 0x10
要为变量指定指数值，请键入根号，字母e和表示10的倍数的数字。例如，要将值3.1415分配给$ a变量的1,000的幂，请键入：
$a = 3.1415e3
Windows PowerShell还可以将千字节KB，兆字节MB和千兆字节GB转换为字节。例如，要为$ a变量分配一个10千字节的值，请输入：
$a = 10kb
由加法运算符赋值
加法运算符赋值+=可以增加变量的值，也可以将指定的值附加到现有值。该操作取决于变量是否具有数字或字符串类型以及变量是包含单个值（标量）还是包含多个值（集合）。

该+=运营商将两个操作。首先，它添加，然后它分配。因此，下列陈述是等同的：
$a += 2
$a = ($a + 2)
当变量包含单个数值时，+=操作员将现有值增加操作员右侧的数量。然后，操作员将结果值分配给变量。以下示例显示如何使用+=运算符来增加变量的值：
$a = 4
$a += 2
$a


6
当变量的值是一个字符串时，运算符右侧的值将附加到字符串，如下所示：
$a = "Windows"
$a += " PowerShell"
$a


Windows PowerShell
当变量的值是一个数组时，+=操作符将操作符右侧的值追加到数组中。除非通过强制转换显式地键入数组，否则可以向数组附加任何类型的值，如下所示：
$a = 1,2,3
$a += 2
$a


1
2
3
2
和
$a += "String"
$a


1
2
3
2
String
当变量的值是哈希表时，+=运算符将运算符右侧的值附加到哈希表。但是，因为可以添加到散列表的唯一类型是另一个散列表，所有其他分配都会失败。

例如，以下命令将哈希表分配给$ a变量。然后，它使用+=运算符将另一个散列表附加到现有散列表中，从而有效地将新的键/值对添加到现有散列表。该命令成功，如输出所示：
$a = @{a = 1; b = 2; c = 3}
$a += @{mode = "write"}
$a


Name                           Value
----                           -----
a                              1
b                              2
mode                           write
c                              3
以下命令尝试向$ a变量中的哈希表追加一个整数“1”。该命令失败：
$a = @{a = 1; b = 2; c = 3}
$a += 1


You can add another hash table only to a hash table.
At line:1 char:6
+ $a += <<<<  1
减法运算符的分配
减法运算符的赋值按照运算符-=右侧指定的值减少变量的值。此运算符不能与字符串变量一起使用，也不能用于从集合中删除元素。

该-=运营商将两个操作。首先，它减去，然后分配。因此，下列陈述是等同的：
$a -= 2
$a = ($a - 2)
以下示例显示如何使用-=运算符来减少变量的值：
$a = 8
$a -= 2
$a


6
您还可以使用-=赋值运算符来减少数值数组成员的值。为此，请指定要更改的数组元素的索引。在以下示例中，数组的第三个元素（元素2）的值减1：
$a = 1,2,3
$a[2] -= 1
$a


1
2
2
您不能使用-=运算符删除变量的值。要删除分配给变量的所有值，请使用 Clear-Item或 Clear-Variable cmdlet为变量赋值$null或""赋值。
$a = $null
要从数组中删除特定值，请使用数组符号将值分配给$null特定项目。例如，以下语句从数组中删除第二个值（索引位置1）：
$a = 1,2,3
$a


1
2
3$a[1] = $null
$a


1
3
要删除变量，请使用 Remove-Variable cmdlet。当变量显式转换为特定的数据类型并且您想要一个无类型的变量时，此方法非常有用。以下命令删除$ a变量：
Remove-Variable -Name a
乘法运算器的分配
乘法运算符赋值乘*=数值或附加指定数量的变量字符串值副本。

当变量包含单个数值时，该值将乘以运算符右侧的值。例如，以下示例显示如何使用*=运算符来乘以变量的值：
$a = 3
$a *= 4
$a


12
在这种情况下，*=操作员组合两个操作。首先，它乘以，然后它分配。因此，下列陈述是等同的：
$a *= 2
$a = ($a * 2)
当变量包含字符串值时，Windows PowerShell将指定数量的字符串附加到该值，如下所示：
$a = "file"
$a *= 4
$a


filefilefilefile
要乘数组的一个元素，使用索引来标识要乘的元素。例如，以下命令将数组中的第一个元素（索引位置0）乘以2：
$a[0] *= 2
分部运算符的分配
除法运算符的赋值/=将数值除以运算符右侧指定的值。运算符不能与字符串变量一起使用。

该/=运营商将两个操作。首先，它分开，然后分配。因此，以下两个陈述是等同的：
$a /= 2
$a = ($a / 2)
例如，以下命令使用/=运算符来划分变量的值：
$a = 8
$a /=2
$a


4
要划分数组的元素，请使用索引标识要更改的元素。例如，以下命令将数组中的第二个元素（索引位置1）除以2：
$a[1] /= 2
模量运算符的分配
模数运算符的赋值%=将变量的值除以运算符右侧的值。然后，%=操作员将余数（称为模数）分配给变量。只有当变量包含单个数值时，才可以使用此运算符。当变量包含字符串变量或数组时，不能使用此运算符。

该%=运营商将两个操作。首先，它划分并确定余数，然后将余数分配给变量。因此，下列陈述是等同的：
$a %= 2
$a = ($a % 2)
以下示例显示如何使用%=运算符来保存商的模数：
$a = 7
$a %= 4
$a


3
增量和减法运算符
递增运算符++将变量值增加1.当您在简单语句中使用递增运算符时，不会返回任何值。要查看结果，请显示变量的值，如下所示：
$a = 7
++$a
$a


8
要强制返回值，请将变量和运算符括在括号中，如下所示：
$a = 7
(++$a)


8
增量运算符可以放在变量前（前缀）或后（后缀）。操作符的前缀版本在语句中使用其值之前递增变量，如下所示：
$a = 7
$c = ++$a
$a


8$c


8
在语句中使用其值后，该运算符的后缀版本会增加一个变量。在以下示例中，$ c和$ a变量具有不同的值，因为在$ a更改之前将值分配给$ c：
$a = 7
$c = $a++
$a


8$c


7
递减运算符--将变量的值减1。与增量运算符一样，在简单语句中使用运算符时不会返回任何值。使用括号返回值，如下所示：
$a = 7
--$a
$a


6(--$a)


5
运算符的前缀版本在语句中使用其值之前递减变量，如下所示：
$a = 7
$c = --$a
$a


6$c


6
在语句中使用其值后，该运算符的后缀版本会减少该变量。在以下示例中，$ d和$ a变量具有不同的值，因为该值在$ a更改前分配给$ d：
$a = 7
$d = $a--
$a


6$d


7
MICROSOFT .NET框架类型
默认情况下，当一个变量只有一个值时，分配给该变量的值决定了该变量的数据类型。例如，以下命令将创建一个具有“Integer”（System.Int32）类型的变量：
$a = 6
若要查找变量的.NET Framework类型，请使用GetType方法及其FullName属性，如下所示。确保在GetType方法名称后面包括括号，即使方法调用没有参数：
$a = 6
$a.GetType().FullName


System.Int32
要创建一个包含字符串的变量，请为该变量分配一个字符串值。要表明该值是一个字符串，请将其用引号括起来，如下所示：
$a = "6"
$a.GetType().FullName


System.String
如果分配给变量的第一个值是字符串，则Windows PowerShell将所有操作视为字符串操作，并将新值转换为字符串。这在下面的例子中发生：
$a = "file"
$a += 3
$a


file3
如果第一个值是整数，则Windows PowerShell将所有操作视为整数操作，并将新值转换为整数。这在下面的例子中发生：
$a = 6
$a += "3"
$a


9
通过将类型名称放在变量名称或第一个赋值之前的括号中，可以将任何.NET Framework类型转换为新的标量变量。当您投射变量时，您可以确定可以存储在变量中的数据类型。而且，您可以确定变量在操作时的行为方式。

例如，以下命令将该变量转换为字符串类型：
[string]$a = 27
$a += 3
$a


273
以下示例将投射第一个值，而不是投射变量：
$a = [string]27
当您将变量转换为特定类型时，通用约定是投射变量而不是值。但是，如果现有变量的值无法转换为新的数据类型，则无法重新生成现有变量的数据类型。要更改数据类型，您必须替换它的值，如下所示：
$a = "string"
[int]$a


Cannot convert value "string" to type "System.Int32". Error: "Input
string was not in a correct format."
At line:1 char:8
+ [int]$a <<<<[int]$a = 3
此外，当您在变量名称前加上数据类型时，该变量的类型将被锁定，除非您通过指定其他数据类型显式覆盖该类型。如果您尝试分配与现有类型不兼容的值，并且未明确覆盖该类型，则Windows PowerShell将显示一个错误，如以下示例所示：
$a = 3
$a = "string"
[int]$a = 3
$a = "string"


Cannot convert value "string" to type "System.Int32". Error: "Input
string was not in a correct format."
At line:1 char:3
+ $a <<<<  = "string"[string]$a = "string"
在Windows PowerShell中，包含数组中多个项目的变量的数据类型与包含单个项目的变量的数据类型处理方式不同。除非数据类型专门分配给数组变量，否则数据类型始终为空System.Object []。这种数据类型是特定于数组的。

有时，您可以通过指定其他类型来覆盖默认类型。例如，以下命令将变量转换为string [] 数组类型：
[string []] $a = "one", "two", "three"
Windows PowerShell变量可以是任何.NET Framework数据类型。此外，您可以分配当前进程中可用的任何完全限定的.NET Framework数据类型。例如，以下命令指定System.DateTime数据类型：
[System.DateTime]$a = "5/31/2005"
该变量将被分配一个符合 System.DateTime数据类型的值。$ a变量的值如下所示：Tuesday, May 31, 2005 12:00:00 AM
分配多个变量
在Windows PowerShell中，您可以使用单个命令将值分配给多个变量。赋值的第一个元素分配给第一个变量，第二个元素分配给第二个变量，第三个元素分配给第三个变量，依此类推。例如，以下命令将值1分配给$ a变量，将值2分配给$ b变量，将值3分配给$ c变量：
$a, $b, $c = 1, 2, 3
如果赋值包含的元素多于变量，则剩余的所有值将分配给最后一个变量。例如，以下命令包含三个变量和五个值：
$a, $b, $c = 1, 2, 3, 4, 5
因此，Windows PowerShell将值1分配给$ a变量，将值2分配给$ b变量。它将值3，4和5分配给$ c变量。要将$ c变量中的值分配给其他三个变量，请使用以下格式：
$d, $e, $f = $c
此命令将值3分配给$ d变量，将值4分配给$ e变量，将值5分配给$ f变量。

您还可以通过链接变量将单个值分配给多个变量。例如，以下命令为所有四个变量赋值“3”：
$a = $b = $c = $d = "three"
可变相关的CMDLETS
除了使用赋值操作设置变量值之外，还可以使用 Set-Variable cmdlet。例如，以下命令用于Set-Variable将$ 1,2的数组分配给$ a变量。
Set-Variable -Name a -Value 1, 2, 3
也可以看看
about_Arrays

about_Hash_Tables

about_Variables

清除变量

删除变量

设置变量

注意

该内容的反馈系统将很快改变。旧评论不会被遗漏。如果评论主题中的内容对您很重要，请保存副本。有关即将进行的更改的更多信息，我们邀请您阅读我们的博客文章。

0条评论
签到3人在听
 

 
+关注
发表评论为......
选择Package
Power Shell 6

Filter by title
概观
示例脚本
参考
Cim Cmdlet
微软。动力壳。档案
微软。动力壳。核心
关于
参阅about_Aliases
about_Arithmetic_Operators
about_Arrays
about_Assignment_Operators
参阅about_Automatic_Variables
about_Break
about_Cim 会话
about_Classes
about_Command_Precedence
about_Command_Syntax
about_Comment_Based_Help
about_Common 参数
about_Comparison_Operators
about_Continue
about_Core_Commands
参阅about_Data_Sections
about_Debuggers
about_Do
about_Enum
about_Environment_Variables
参阅about_Execution_Policies
about_For
about_Foreach
about_Format。PS1XML
about_Functions
about_Functions_Advanced
about_Functions_Advanced_Methods
about_Functions_Advanced_Parameters
about_Functions_Cmdlet 绑定属性
about_Functions_Output 类型属性
about_Group_Policy_Settings
about_Hash_Tables
about_hidden
about_History
about_If
about_Job_Details
about_Jobs
about_Join
about_Language_Keywords
about_Language_Modes
about_Line_Editing
about_locations
about_Logging
about_logical_operators
about_Methods
about_Modules
about_Object_Creation
about_Objects
about_Operator_Precedence
about_Operators
about_PackageManagement
about_Parameters
about_Parameters_Default_Values
about_Parsing
about_Path_Syntax
about_pipelines
about_Preference_Variables
about_Profiles
about_Prompts
about_Properties
about_Providers
about_psconsolehostreadline
about_psreadline
about_PSSession_Details
about_PSSessions
about_pwsh
about_Quoting_Rules
about_Redirection
about_Ref
about_Regular_Expressions
about_Remote
about_Remote_Disconnected_Sessions
about_Remote_FAQ
about_Remote_Jobs
about_Remote_Output
about_Remote_Requirements
about_Remote_Troubleshooting
about_Remote_Variables
about_Requires
about_Reserved_Words
about_Return
about_Run_With_PowerShell
about_Scopes
about_Script_Blocks
about_Script_Internationalization
about_Scripts
about_Session_Configuration_Files
about_Session_Configurations
about_Signing
about_simplified_syntax
about_Special_Characters
about_Splatting
about_Split
about_Switch
about_Throw
about_Trap
about_Try_Catch_Finally
about_Type_Operators
about_Types.ps1xml
about_Updatable_Help
About_Using
about_Variables
about_While
about_Wildcards
Providers
Add-History
Clear-History
Clear-Host
Connect-PSSession
Debug-Job
Disable-PSSessionConfiguration
Disconnect-PSSession
Enable-PSSessionConfiguration
Enter-PSHostProcess
Enter-PSSession
Exit-PSHostProcess
Exit-PSSession
Export-ModuleMember
ForEach-Object
Get-Command
Get-Help
Get-History
Get-Job
Get-Module
Get-PSHostProcessInfo
Get-PSSession
Get-PSSessionCapability
Get-PSSessionConfiguration
Import-Module
Invoke-Command
Invoke-History
mkdir
New-Module
New-ModuleManifest
New-PSRoleCapabilityFile
New-PSSession
New-PSSessionConfigurationFile
New-PSSessionOption
New-PSTransportOption
oss
Out-Default
Out-Host
Out-Null
Receive-Job
Receive-PSSession
Register-ArgumentCompleter
Register-PSSessionConfiguration
Remove-Job
Remove-Module
Remove-PSSession
Save-Help
Set-PSDebug
Set-PSSessionConfiguration
Set-StrictMode
Start-Job
Stop-Job
Test-ModuleManifest
Test-PSSessionConfigurationFile
Unregister-PSSessionConfiguration
Update-Help
Wait-Job
Where-Object
微软。动力壳。诊断
微软。动力壳。主办
微软。动力壳。管理
微软。动力壳。安全
微软。动力壳。效用
微软。的WSMan。管理
包管理
Power Shell Get
PSDesired 状态配置
PSDiagnostics
PSRead 线

此页面有帮助吗？
是  没有
美国英语） 早期版本文档 博客 有助于 隐私和Cookie 使用条款 网站反馈 商标
