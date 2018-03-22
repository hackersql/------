##只能有一个
----------------------
在这个挑战中，我们有两项任务：

* 一是插入我们自己的数据标签`winrar`。

* 二，防止原始数据标签被解析。

我们的原始XML数据如下所示：
```
<xmlfile>
 <hooray attrib="Inject2">
  <ilovepie>Inject1</ilovepie>
 </hooray>
 <data>
	<![CDATA[Inject3]]>
 </data>
</xmlfile>
```
我们的注射字符串将取代`Inject2`。首先，我们需要打破属性和`hooray`标签。所以，我们的注入字符串开始于：

`"></hooray>`

接下来，我们必须用数据"winrar"定义我们的数据标签，它完成了第一项任务，并将我们带到这个注入字符串：

`"></hooray><data><![CDATA[winrar]]></data>`

不幸的是，这给我们留下了结构被打散的XML和两个数据标签。 但是，XML解析器`libxml`是用本机代码编写的。 另外，XML在被送入解析器之前被构造为一个字符串。 因此，我们可以使用空字节过早地结束XML并防止读取原始数据标记，从而完成第二个任务。 我们需要确保我们的其他标签正确关闭，因此我们添加一个结束标签`</xmlfile>`来结束`<xmlfile>`节点。 我们的最终注入字符串如下所示：

`"></hooray><data><![CDATA[winrar]]></data></xmlfile>%00`
