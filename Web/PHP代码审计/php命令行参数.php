php my_script.php
 
php -f  "my_script.php"
以上两种方法（使用或不使用 -f 参数）都能够运行给定的 my_script.php 文件。您可以选择任何文件来运行，您指定的 PHP 脚本并非必须要以 .php 为扩展名，它们可以有任意的文件名和扩展名。

在命令行直接运行 PHP 代码。

php -r "print_r(get_defined_constants());"
在使用这种方法时，请您注意外壳变量的替代及引号的使用。

注: 请仔细阅读以上范例，在运行代码时没有开始和结束的标记符！加上 -r 参数后，这些标记符是不需要的，加上它们会导致语法错误。

注: 使用这种形式的 PHP 时，应个别注意避免和外壳环境进行的命令行参数替换相冲突。

显示语法解析错误的范例

$ php -r "$foo = get_defined_constants();"
Command line code(1) : Parse error - parse error, unexpected '='
这里的问题在于即时使用了双引号 "，sh/bash 仍然实行了参数替换。由于 $foo 没有被定义，被替换后它所在的位置变成了空字符，因此在运行时，实际被 PHP 读取的代码为：

$ php -r " = get_defined_constants();"
正确的方法是使用单引号 '。在用单引号引用的字符串中，变量不会被 sh/bash 还原成其原值。

$ php -r '$foo = get_defined_constants(); var_dump($foo);'
array(370) {
  ["E_ERROR"]=>
  int(1)
  ["E_WARNING"]=>
  int(2)
  ["E_PARSE"]=>
  int(4)
  ["E_NOTICE"]=>
  int(8)
  ["E_CORE_ERROR"]=>
  [...]
如果您使用的外壳不是 sh/bash，您可能会碰到其它的问题。请报告您碰到的 bug，或者发邮件到 phpdoc@lists.php.net。

当您试图将外壳的环境变量引入到马或者用反斜线来转义字符时也可能碰到各种各样的问题，请您在使用时注意！