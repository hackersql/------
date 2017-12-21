To use safe2bin.py you need to pass it the original file,
and optionally the output file name.

Example:

$ python ./safe2bin.py -i output.txt -o output.txt.bin

This will create an binary decoded file output.txt.bin. For example, 
if the content of output.txt is: "\ttest\t\x32\x33\x34\nnewline" it will 
be decoded to: "	test	234
newline"

If you skip the output file name, general rule is that the binary
file names are suffixed with the string '.bin'. So, that means that 
the upper example can also be written in the following form:

$ python ./safe2bin.py -i output.txt
-------------------------------------------------------------------------
要使用safe2bin.py，您需要传递原始文件，以及可选的输出文件名。

例：

$ python ./safe2bin.py -i output.txt -o output.txt.bin

这将创建一个二进制解码文件output.txt.bin。 
例如，如果output.txt的内容是：“\ttest\t\x32\x33\x34\nnewline”，它将被解码为：“	test	234
newline”

如果跳过输出文件名，通用规则是二进制文件名后缀为'.bin'。 所以，这意味着上面的例子也可以写成如下形式：

$ python ./safe2bin.py -i output.txt