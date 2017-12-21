To use cloak.py you need to pass it the original file,
and optionally the output file name.

Example:

$ python ./cloak.py -i backdoor.asp -o backdoor.asp_

This will create an encrypted and compressed binary file backdoor.asp_.

Such file can then be converted to its original form by using the -d
functionality of the cloak.py program:

$ python ./cloak.py -d -i backdoor.asp_ -o backdoor.asp

If you skip the output file name, general rule is that the compressed
file names are suffixed with the character '_', while the original is
get by skipping the last character. So, that means that the upper
examples can also be written in the following form:

$ python ./cloak.py -i backdoor.asp

$ python ./cloak.py -d -i backdoor.asp_
---------------------------------------------------------
要使用cloak.py，您需要传递原始文件，以及可选的输出文件名。

例：

$ python ./cloak.py -i backdoor.asp -o backdoor.asp_

这将创建一个加密和压缩的二进制文件backdoor.asp_。

然后可以使用cloak.py程序的-d功能将此类文件转换为其原始格式：

$ python ./cloak.py -d -i backdoor.asp_ -o backdoor.asp

如果您跳过输出文件名，则通常的规则是压缩文件名称后缀为字符“_”，而原始文件名通过跳过最后一个字符来获得。 所以，这意味着上面的例子也可以写成如下形式：

$ python ./cloak.py -i backdoor.asp

$ python ./cloak.py -d -i backdoor.asp_