##xml注原理之闭合语句

在这个挑战中，我们有一个XML注入场景：我们的数据被放置到XML文档的上下文中而没有对输入进行过滤。因此，我们可以影响XML文档的内容以造成恶作剧。在这个特定的场景中，我们正在向文档注入一个新的“数据”节点。

未改变的XML文档如下所示：

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

我们的注入字符串正在替换出现`Inject3`的数据节点的内容。 `CDATA`标签表示内部数据将被解释为文字。在该标签内部，不会出现XML提示。首先，我们用字符序列`]]>`打破该标签。不幸的是，这给我们留下了格式不正确的XML文档。 XML解析器通常是严格的，所以我们只会得到一个错误和不快乐。我们将在稍后讨论。现在，我们的注入字符串如下所示：
`foo]]>`
我们也在现有的数据节点中，所以我们需要摆脱这一点。我们可以通过注入一个结束数据标签来做到这一点，使我们的注入字符串如下所示：

`foo]]></data>`

现在我们准备打开一个新的数据标签：

`foo]]></data><data>`

剩下的唯一事情就是打开一个新的CDATA标签并将其返回给格式良好的文档：

`foo]]></data><data><![CDATA[bar`

这里是我们修改后的文档（为了便于阅读，进行格式化）：

```
<xmlfile>
 <hooray attrib="Inject2">
  <ilovepie>Inject1</ilovepie>
 </hooray>
 <data>
	<![CDATA[foo]]>
 </data>
 <data>
    <![CDATA[bar]]>
 </data>
</xmlfile>
```