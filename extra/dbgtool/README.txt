To use dbgtool.py you need to pass it the MS-DOS executable binary file,
and optionally the output debug.exe script file name.

Example:

$ python ./dbgtool.py -i ./nc.exe -o nc.scr

This will create a ASCII text file with CRLF line terminators called
nc.scr.

Such file can then be converted to its original portable executable with
the Windows native debug.exe, that is installed by default in all Windows
systems:

> debug.exe < nc.scr

To be able to execute it on Windows you have to rename it to end with
'.com' or '.exe':

> ren nc_exe nc.exe
------------------------------------------------------------------------------------------
要使用dbgtool.py，您需要将其传递给MS-DOS可执行文件，并且可选地输出debug.exe脚本文件名。

例：

$ python ./dbgtool.py -i ./nc.exe -o nc.scr

这将创建一个名为nc.scr的CRLF行终止符的ASCII文本文件。

然后可以使用Windows本机debug.exe将此类文件转换为原始的可移植可执行文件，默认情况下在所有Windows系统中都安装该文件。

> debug.exe <nc.scr

为了能够在Windows上执行它，你必须重命名它以'.com'或'.exe'结尾：

> ren nc_exe nc.exe