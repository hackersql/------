<?php
//连接数据库部分，注意使用了gbk编码
$conn = mysql_connect('localhost', 'root', 'root') or die('bad!');
mysql_query("SET NAMES 'gbk'");
mysql_select_db('test', $conn) OR emMsg("连接数据库失败，未找到您填写的数据库");
//执行sql语句
mysql_query("SET character_set_connection=gbk, character_set_results=gbk,character_set_client=binary", $conn); 
$id = isset($_GET['id']) ? addslashes($_GET['id']) : 1;
$id = iconv('utf-8', 'gbk', $id);
$sql = "SELECT * FROM news WHERE tid='{$id}'";
$result = mysql_query($sql, $conn) or die(mysql_error());
echo "<br>"."sql:".$sql."<br>"
?>
<!DOCTYPE html>
<html>
<head>
<meta charset="gbk" />
<title>gbk change utf-8</title>
</head>
<body>
<?php
$row = mysql_fetch_array($result, MYSQL_ASSOC);
echo "<h2>{$row['title']}</h2><p>{$row['content']}<p>\n";
mysql_free_result($result);
?>
</body>
</html>
