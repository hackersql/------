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