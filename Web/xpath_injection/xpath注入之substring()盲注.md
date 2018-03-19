##xpath注入之substring()盲注

在这个挑战中，我们没有来自查询的输出，只表明查询是否返回结果。在之前的挑战中，我们可以一次检索一个值，但必须使用盲注技术来理解数据的结构。我们首先以与前面的挑战相同的方式列举结构。我们现在必须使用盲注技术来提取数据，而不是像前面的例子那样检索每个值。

我们可以使用的技术包括substring()函数。仅当根的第一个子节点中的第一个字符等于`a`时，以下查询才会返回结果：

`/*[substring(/*[1],1,1)='a']`

我们可以使用已知的用户名值或使用 `or`关键字来完成此操作。

```
With: /xmlfile/users/user[username='jsmiley' and substring(/*[1],1,1)='a']/username
Without: /xmlfile/users/user[username='' or 1=1 and substring(/*[1],1,1)='a']/username
```

 `without`版本更有用，因为我们不需要知道现有值。

通过迭代要检索的值中每个字符的可能字符的字符集，我们可以慢慢确定该值。

使用工具`BXPI`和`XPath Blind Explorer`可以自动执行此过程。在编写本文时，XPath Blind Explorer对GET或POST数据中的&字符进行URL编码，因此无法正确处理需要设置多个参数的页面，如XMLmao。这可以通过使用Burp Proxy将任何`%26`转换回`&`来解决。