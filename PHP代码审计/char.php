<?php
$a = $_GET['a'];
var_dump(bin2hex($a));
$sql = "insert into shadow(name,shadow) values('$a', 'zzz')";
$conn = mysql_connect("localhost", "root", "");
$result = mysql_query('show variables like "char"') or die(mysql_error());
echo "----------------------<br />";
while ($row = mysql_fetch_array($result)) {
	echo $row[0] . ' : ' . $row[1] . "<br />";
}
mysql_query('show variables like "char%"') or die(mysql_error());
while ($row=mysql_fetch_array($result)) {
	echo $row[0] . ' : ' . $row[1] . "<br />";
}
mysql_select_db("test", $conn);
mysql_query($sql, $conn) or die(mysql_error());
?>

