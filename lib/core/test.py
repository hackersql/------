#!/usr/bin/env python
#coding=utf-8

"""ANSI输出端口的颜色格式。"""

from __future__ import print_function
from optparse import OptionParser
import os


__ALL__ = [ 'colored', 'cprint' ]

VERSION = (1, 1, 0)

ATTRIBUTES = dict(
        list(zip([
            'bold',
            'dark',
            '',
            'underline',
            'blink',
            '',
            'reverse',
            'concealed'
            ],
            list(range(1, 9))
            ))
        )
del ATTRIBUTES['']


HIGHLIGHTS = dict(
        list(zip([
            'on_grey',
            'on_red',
            'on_green',
            'on_yellow',
            'on_blue',
            'on_magenta',
            'on_cyan',
            'on_white'
            ],
            list(range(40, 48))
            ))
        )


COLORS = dict(
        list(zip([
            'grey',
            'red',
            'green',
            'yellow',
            'blue',
            'magenta',
            'cyan',
            'white',
            ],
            list(range(30, 38))
            ))
        )


RESET = '\033[0m'


def colored(text, color=None, on_color=None, attrs=None):
    """着色文字。

     可用文字颜色：
         红色，绿色，黄色，蓝色，洋红色，青色，白色。

     可用的文字亮点：
         on_red，on_green，on_yellow，on_blue，on_magenta，on_cyan，on_white。

     可用属性：
         粗体，  黑色，  下划线，     闪烁，    背景，      隐藏
                'bold', dark', 'underline', 'blink', 'reverse', 'concealed'
    Example:
        colored('Hello, World!', 'red', 'on_grey', ['blue', 'blink'])
        colored('Hello, World!', 'green')
    """
    if os.getenv('ANSI_COLORS_DISABLED') is None:
        fmt_str = '\033[%dm%s'
        if color is not None:
            text = fmt_str % (COLORS[color], text)

        if on_color is not None:
            text = fmt_str % (HIGHLIGHTS[on_color], text)

        if attrs is not None:
            for attr in attrs:
                text = fmt_str % (ATTRIBUTES[attr], text)

        text += RESET
    return text


def cprint(text, color=None, on_color=None, attrs=None, **kwargs):
    """打印彩色文字。

     它接受打印功能的参数
    """

    print((colored(text, color, on_color, attrs)), **kwargs)


if __name__ == '__main__':
    print('当前终端类型: %s' % os.getenv('TERM'))
    print('测试基本颜色:')
    cprint('灰色', 'grey')
    cprint('红色', 'red')
    cprint('绿色', 'green')
    cprint('黄色', 'yellow')
    cprint('蓝色', 'blue')
    cprint('洋红色', 'magenta')
    cprint('青色', 'cyan')
    cprint('白色', 'white')
    print(('-' * 78))

    print('测试背景:')
    cprint('黑色背景', on_color='on_grey')
    cprint('红色背景', on_color='on_red')
    cprint('绿色背景', on_color='on_green')
    cprint('黄色背景', on_color='on_yellow')
    cprint('蓝色背景', on_color='on_blue')
    cprint('洋红色背景', on_color='on_magenta')
    cprint('青色背景', on_color='on_cyan')
    cprint('灰白色背景', color='grey', on_color='on_white')
    print('-' * 78)

    print('测试属性:')
    cprint('粗体黑色', 'grey', attrs=['bold'])
    cprint('深红色', 'red', attrs=['dark'])
    cprint('深红色', 'red')
    cprint('绿色下划线', 'green', attrs=['underline'])
    cprint('闪烁黄色', 'yellow', attrs=['blink'])
    cprint('蓝色背景', 'blue', attrs=['reverse'])
    cprint('洋红色字', 'magenta', attrs=['concealed'])
    cprint('洋红色背景', 'magenta', attrs=['reverse'])
    cprint('粗体下划线青色背景', 'cyan', attrs=['bold', 'underline', 'reverse'])
    cprint('黑白闪烁', 'white', attrs=['dark', 'blink', 'concealed'])
    print(('-' * 78))

    print('混合测试:')
    cprint('红色下划线，红色字，黑色背景', 'red', 'on_grey', ['underline'])
    cprint('红色字体-绿色背景', 'green', 'on_red', ['reverse'])

usage = "myprog[ -f <filename>][-s <xyz>] arg1[,arg2..]"
optParser = OptionParser(usage)
optParser.add_option("-f","--file",action = "store",type="string",dest = "fileName")
optParser.add_option("-v","--vison", action="store_false", dest="verbose",default='None',
                     help="make lots of noise [default]")
fakeArgs = ['-f','file.txt','-v','good luck to you', 'arg2', 'arge']
options, args = optParser.parse_args(fakeArgs)
print (options.fileName)
print (options.verbose)
print (options)
print (args)
print (optParser.print_help())

#coding=utf-8
 2 import threading
 3
 4 class scanner(threading.Thread):
 5     tlist=[] #用来存储队列的线程
 6     maxthreads=100 # int(sys.argv[2])最大的并发数量，此处我设置为100，测试下系统最大支持1000多个
 7     evnt=threading.Event()#用事件来让超过最大线程设置的并发程序等待
 8     lck=threading.Lock() #线程锁
 9     def __init__(self):
10         threading.Thread.__init__(self)
11     def run(self):
12         try:
13             pass
14         except Exception,e:
15             print e.message
16         #以下用来将完成的线程移除线程队列
17         scanner.lck.acquire()
18         scanner.tlist.remove(self)
19         #如果移除此完成的队列线程数刚好达到99，则说明有线程在等待执行，那么我们释放event，让等待事件执行
20         if len(scanner.tlist)==scanner.maxthreads-1:
21             scanner.evnt.set()
22             scanner.evnt.clear()
23         scanner.lck.release()
24     def newthread(proxy,counter):
25         scanner.lck.acquire()#上锁
26         sc=scanner()
27         scanner.tlist.append(sc)
28         scanner.lck.release()#解锁
29         sc.start()
30     #将新线程方法定义为静态变量，供调用
31     newthread=staticmethod(newthread)
32
33 def runscan():
34     for i in 1 .. 100:
35         scanner.lck.acquire()
36         #如果目前线程队列超过了设定的上线则等待。
37         if len(scanner.tlist)>=scanner.maxthreads:
38             scanner.lck.release()
39             scanner.evnt.wait()#scanner.evnt.set()遇到set事件则等待结束
40         else:
41             scanner.lck.release()
42         scanner.newthread(proxy,counter)
43
44     for t in scanner.tlist:
45         t.join()#join的操作使得后面的程序等待线程的执行完成才继续
46
47 if __name__=="__main__":
48     runscan()