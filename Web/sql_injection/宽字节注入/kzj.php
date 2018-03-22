<?php
//连接数据库部分，注意使用了gbk编码
$conn = mysql_connect('localhost', 'root', 'root') or die('bad!');
mysql_query("SET NAMES 'gbk'");
mysql_select_db('test', $conn) OR emMsg("连接数据库失败，未找到您填写的数据库");
//执行sql语句
$id = isset($_GET['id']) ? addslashes($_GET['id']) : 1;
$sql = "SELECT * FROM news WHERE tid='{$id}'";
$result = mysql_query($sql, $conn) or die(mysql_error());
echo "<br>"."执行的sql语句是:".$sql."<br>"
?>
<!DOCTYPE html>
<html>
<head>
<meta charset="gbk" />
<title>宽字节测试</title>
</head>
<body>
<?php
$row = mysql_fetch_array($result, MYSQL_ASSOC);
echo "<h2>{$row['title']}</h2><p>{$row['content']}<p>\n";
mysql_free_result($result);
?>
<?php 
	echo "(1)use addslashes\n";
	$t = addslashes(urldecode("%e5%5c%27"));
	echo iconv("GBK", "UTF-8",$t) . "\n";
	echo "--------------------------------\n";
	echo "\n(2)use mysql_real_escape_string+mysql_set_charset\n";
	$conn = mysql_connect("localhost",'root','root');
	mysql_set_charset("GBK");
	$t = mysql_real_escape_string(urldecode("%e5%5c%27"),$conn);
	echo iconv("GBK", "UTF-8",$t) . "\n";
	mysql_close($conn);
 ?>
</body>
</html>

