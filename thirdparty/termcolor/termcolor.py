#coding=utf-8

"""ANSI输出端口的颜色格式。"""

from __future__ import print_function
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
         红色，绿色，黄色，蓝色，品红色，青色，白色。

     可用的文字亮点：
         on_red，on_green，on_yellow，on_blue，on_magenta，on_cyan，on_white。

     可用属性：
         粗体，黑色，下划线，闪烁，反转，隐藏

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

    print('测试亮点:')
    cprint('On grey color', on_color='on_grey')
    cprint('On red color', on_color='on_red')
    cprint('On green color', on_color='on_green')
    cprint('On yellow color', on_color='on_yellow')
    cprint('On blue color', on_color='on_blue')
    cprint('On magenta color', on_color='on_magenta')
    cprint('On cyan color', on_color='on_cyan')
    cprint('On white color', color='grey', on_color='on_white')
    print('-' * 78)

    print('测试属性:')
    cprint('粗体灰色', 'grey', attrs=['bold'])
    cprint('深红色', 'red', attrs=['dark'])
    cprint('下划线绿色', 'green', attrs=['underline'])
    cprint('闪烁黄色', 'yellow', attrs=['blink'])
    cprint('反转蓝色', 'blue', attrs=['reverse'])
    cprint('隐藏洋红色', 'magenta', attrs=['concealed'])
    cprint('粗体下划线反向青色', 'cyan', attrs=['bold', 'underline', 'reverse'])
    cprint('黑白闪烁', 'white', attrs=['dark', 'blink', 'concealed'])
    print(('-' * 78))

    print('测试混合:')
    cprint('红色下划线，灰色字', 'red', 'on_grey', ['underline'])
    cprint('红色反转绿色', 'green', 'on_red', ['reverse'])

