sqlmap只在目标系统上调用lib_mysqludf_sys
而不会在运行sqlmap的系统上执行。 

https://github.com/sqlmapproject/udfhack

在MySQL中使用lib_mysqludf_sys调用外部命令

1.lib_mysqludf_sys简介

mysql中没有执行外部命令的函数，要调用外部的命令，可以通过开发MySQL UDF来实现，lib_mysqludf_sys 就是一个实现了此功能的UDF库。
下载地址：https://github.com/mysqludf/lib_mysqludf_sys

2.使用方法
2.1 安装部署
a) lib_mysqludf_sys.so复制到mysql/lib/plugin目录下。

b) 在mysql中创建函数(根据需要选取)：

Drop FUNCTION IF EXISTS lib_mysqludf_sys_info;
Drop FUNCTION IF EXISTS sys_get;
Drop FUNCTION IF EXISTS sys_set;
Drop FUNCTION IF EXISTS sys_exec;
Drop FUNCTION IF EXISTS sys_eval;
 
Create FUNCTION lib_mysqludf_sys_info RETURNS string SONAME 'lib_mysqludf_sys.so';
Create FUNCTION sys_get RETURNS string SONAME 'lib_mysqludf_sys.so';
Create FUNCTION sys_set RETURNS int SONAME 'lib_mysqludf_sys.so';
Create FUNCTION sys_exec RETURNS int SONAME 'lib_mysqludf_sys.so';
Create FUNCTION sys_eval RETURNS string SONAME 'lib_mysqludf_sys.so';

2.2 使用此函数
例：在select语句调用mkdir命令

Select sys_exec('mkdir -p /home/user1/aaa')
例：在触发器中调用外部的脚本(脚本需要可执行权限)

Create TRIGGER trig_test AFTER Insert ON <table1>
FOR EACH ROW 
BEGIN
    DECLARE ret INT;
    Select sys_exec('/home/user1/test.sh') INTO ret;
END