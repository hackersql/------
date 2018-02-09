linux 终端快捷键

重定向是 > ，默认是覆盖写，如果想要追加，使用 >> 。

1 约定
三个控制键分别用 CTRL ALT SHIFT 表示， CTRL a 表示 CTRL 和 a 键的组合，先摁控制键。 4个方向键分别用 LEFT RIGHT TOP DOWN 表示 Backspace键用 BS 表示，Delete键用 DEL 表示

2 快速移动光标
CTRL a 移动光标到行首
CTRL e 移动光标到行位
CTRL b 向左移动光标，一次一个字符，相当于 LEFT
CTRL f 向右移动光标，一次一个字符，相当于 RIGHT
ALT b 向左移动光标，一次一个单词
ALT f 向右移动光标，一次一个单词

3 快速编辑命令
CTRL k 删除光标左边的所有字符
CTRL u 删除光标右边的所有字符
CTRL d 相当于 DEL 。如果命令行空了，还摁 CTRL d ，那就相当于 exit 命令了。
ALT BS 删除光标左边的单词
ALT d 删除光标右边的单词
ALT u 光标右边的单词转成大写，例如 status ，光标位于u， ALT u 后变成 statUS
ALT l 光标右边的单词转成小写

4 查找历史命令
CTRL p 上一条命令，相当于TOP
CTRL n 下一条命令，相当于DOWN
CTRL r 开启搜索模式，输入部分命令，搜索历史命令，继续 CTRL r 向前搜索
!! 重复上一条命令，也可以 !n 执行任意历史命令。n 是 history 命令输出的命令号

5 屏幕相关
CTRL s 锁定屏幕，如果命令输出较多，屏幕在滚动，你可以用 CTRL s 锁定屏幕，屏幕不再滚动。用windows写程序，又习惯 CTRL s 的注意啦！
CTRL q 解除锁定，如果你摁了 CTRL s ，那么除非解除锁定，否则你敲啥命令都不好使，好像死机了一样。
CTRL l 清空屏幕
reset 这个是命令，如果屏幕曾经出乱码导致一些异常，可以用这个命令恢复。

6 其它
ALT SHIFT # 如果辛苦敲了好长一条命令A，但是发现执行之前，需要先执行一条命令B。你可以用CTRL c 终止A的编辑，也可以 CTRL u 删除A，无论哪种方式，命令A都不会出现在历史记录中，此时你需要 ALT SHIFT #
CTRL g 快捷键敲多了，难免有手抖的时候。例如你辛苦输入了好长的命令A，然后敲了没有任何意义的 ALT p ，命令A消失了，你可以尝试 CTRL g 发现命令A又出现了。

7 任务相关
CTRL c 终止命令执行
CTRL z 暂停命令执行，然后可以用bg把它放到后台
CTRL d 表示输入结束，例如当cat命令等待输入，输入完成时