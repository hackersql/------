1.将waf文件夹复制到服务器任意位置，修改php.ini文件。
2.增加如下代码（假设waf.php文件在E盘根目录）
auto_prepend_file = "E:/waf.php"
然后重启apache即可