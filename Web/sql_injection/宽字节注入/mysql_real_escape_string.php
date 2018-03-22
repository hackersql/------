<?php 
	echo "(1)use addslashes</br>";
	$t = addslashes(urldecode("%e5%5c%27"));
	echo iconv("GBK", "UTF-8",$t) . "</br>";
	echo "--------------------------------</br>";
	echo "(2)use mysql_real_escape_string+mysql_set_charset</br>";
	$conn = mysql_connect("localhost",'root','root');
	mysql_set_charset("GBK");
	$t = mysql_real_escape_string(urldecode("%e5%5c%27"),$conn);
	echo iconv("GBK", "UTF-8",$t) . "</br>";
	mysql_close($conn);
 ?> 
