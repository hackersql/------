wmic /?

查看volume的属性
wmic volume get /?

一直使用/?来帮助你

动词：
/INTERACTIVE - 交互式
/NOINTERACTIVE - 非交互式
where
assoc 相关联的
create
delete
get
set

wmic nteventlog where "logfilename='security'" call cleareventlog

wmic nteventlog list brief

关闭进程
wmic process where processid=3532 delete
wmic process where processid=3096 call terminate

wmic path WIN32_USERACCOUNT where name="sshd"
Path是一个WMIC命令，可让您直接访问WMI命名空间中的一个或多个实例，
而不是通过别名访问它们。当您想要完成的系统管理任务不存在别名时，
Path命令特别有用。您可以使用新的别名和新角色来扩展WMIC，
但是如果您牢牢掌握WMI名称空间，则使用Path命令会更容易。

WMIC还支持Class，Context，Quit和Exit命令。使用Class命令可以直接访问WMI模式中的类或创建现有类的实例。Path和Class命令之间的区别在于Path命令作用于实例及其属性（例如，检索管理数据），而Class命令作用于类定义。
例如，要检索WIN32_SOFTWAREELEMENT类的所有属性，可以键入
wmic class WIN32_SOFTWAREELEMENT get
