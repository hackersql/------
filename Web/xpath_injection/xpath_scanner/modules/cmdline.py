#coding=utf-8
import argparse
from global_object import GLOBJ
#-------------------------------------------------------------------------
programm_name = 'XPath_Scanner_v.5.0'
##########################################################################


##########################################################################
def methods_check(first_object, second_object):  # methods_check
    if (first_object.boolean_based == None and
            first_object.time_based == None and
            first_object.request_based == None):
        print u'[\033[91mERROR\033[92m]: 没有选择任何一个 XPI 方法'
        second_object.print_help()
        exit()
#-------------------------------------------------------------------------


def port_check(first_object, second_object):  # port_check
    if first_object.isdigit() == False or int(first_object) < 1:
        print(u'[\033[91mERROR\033[92m]: 基于请求的方法的最后一个参数必须是正整数(端口)')
        second_object.print_help()
        exit()
#-------------------------------------------------------------------------


def boolean_based_check(first_object, second_object):  # boolean_based_check
    if first_object != None:
        if first_object[0] != 'true' and first_object[0] != 'false':
            print(u'[\033[91mERROR\033[92m]: 基于布尔的方法的第一个参数必须是"true"或"false"')
            second_object.print_help()
            exit()
#-------------------------------------------------------------------------


def request_based_check(first_object, second_object):  # request_based_check
    if first_object != None:
        if first_object[0] != 'doc' and first_object[0] != 'unparsed-text':
            print(u'[\033[91mERROR\033[92m]: 基于请求的方法的第一个参数必须是"doc"或"unparsed-text"')
            second_object.print_help()
            exit()
        port_check(first_object[2], second_object)
##########################################################################


##########################################################################
def cmdLineParser():  # cmdLineParser
    #-------------------------------------------------------------------------
    #   boolean-based arguments parser
    boolean_based = argparse.ArgumentParser(add_help=False)
    boolean_based.add_argument('-b',
                               '--boolean-based',
                               nargs=2,
                               metavar=(
                                   'answer_type', 'str_in_response'),
                               type=str,
                               help='boolean-based method')
#-------------------------------------------------------------------------
#   time-based arguments parser
    time_based = argparse.ArgumentParser(add_help=False)
    time_based.add_argument('-t',
                            '--time-based',
                            nargs=1,
                            metavar=('response_time'),
                            type=float,
                            help='time-based method')
#-------------------------------------------------------------------------
#   request-based arguments parser
    request_based = argparse.ArgumentParser(add_help=False)
    request_based.add_argument('-r',
                               '--request-based',
                               nargs=2,
                               metavar=(
                                   'your_public_ip', 'port'),
                               type=str,
                               help='request-based method')
#-------------------------------------------------------------------------
#   XXE arguments parser
    XXE = argparse.ArgumentParser(add_help=False)
    XXE.add_argument('file_path',
                     type=str,
                     help='目标机器上的文件的本地路径')
    XXE.add_argument('public_ip',
                     type=str,
                     help='你的公共IP')
    XXE.add_argument('port',
                     type=str,
                     help='端口')
#-------------------------------------------------------------------------
#   RLF arguments parser
    RLF = argparse.ArgumentParser(add_help=False)
    RLF.add_argument('file_path',
                     type=str,
                     help='目标机器上的文件的本地路径')
#-------------------------------------------------------------------------
#   extended functionality arguments parser
    ext = argparse.ArgumentParser(add_help=False)
    parse_mode = ext.add_subparsers(title='扩展功能',
                                    dest='EXT_FUNC',
                                    metavar=('EXT_FUNC'),
                                    help='选择扩展功能')
    mode_XXE = parse_mode.add_parser('XXE',
                                     prog=programm_name,
                                     parents=[XXE],
                                     help='XXE读取本地文件')
    mode_unparsed_text = parse_mode.add_parser('RLF',
                                               prog=programm_name,
                                               # boolean_based,time_based],
                                               parents=[request_based, RLF],
                                               usage='''\
%(prog)s  -r public-ip port
                            file_path''',
                                               help='使用unparsed-text函数读取本地文件')
#-------------------------------------------------------------------------
#   modes arguments parser
    modes = argparse.ArgumentParser(prog=programm_name,
                                    add_help=False)
    parse_mode = modes.add_subparsers(title=programm_name + ' 功能',
                                      description='可用的功能',
                                      dest='mode',
                                      metavar=('MODE'),
                                      help='选择XPI方法，扩展功能或使用简单的测试进行检查')
    mode_XPI = parse_mode.add_parser('XPI',
                                     prog=programm_name,
                                     parents=[boolean_based,
                                              time_based, request_based],
                                     usage='''\
%(prog)s  -b [ true | false ] string
                            -t seconds
                            -r public-ip port''',
                                     help='XPI ')
    mode_ext = parse_mode.add_parser('ext',
                                     prog=programm_name,
                                     parents=[ext],
                                     help='扩展功能')
    mode_test = parse_mode.add_parser('test',
                                      prog=programm_name,
                                      parents=[boolean_based,
                                               time_based, request_based],
                                      usage='''\
%(prog)s  -b [ true | false ] string
                            -t seconds
                            -r public-ip port''',
                                      help='测试选择的XPath注入参数')
#-------------------------------------------------------------------------
#   base arguments parser
    base = argparse.ArgumentParser(add_help=False)
    base.add_argument("--method",
                      help="使用HTTP方法",
                      type=str,
                      default="GET",
                      choices=("GET", "POST"))
    base.add_argument("--add_header",
                      help="添加自定义HTTP标头",
                      action='append',
                      type=str)
    base.add_argument('--add_template',
                      nargs=2,
                      metavar=(
                          'begining_of_template', 'ending_of_template'),
                      type=str,
                      help='使用自定义模板')
    base.add_argument("target_url",
                      help="网站扫描.例如: http://127.0.0.1/WEB_APP/index.php",
                      type=str)
    base.add_argument("parameters",
                      help="参数. 例如: param_1=value_1&param_2=value_2",
                      type=str)
    base.add_argument("vulnerable_parameter",
                      help="易受攻击的参数. 例如: value_1",
                      type=str)
#-------------------------------------------------------------------------
#   main arguments parser
    parser = argparse.ArgumentParser(prog=programm_name,
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                     description='扫描站点中的 XPath 漏洞',
                                     parents=[base, modes])
#-------------------------------------------------------------------------
    args = parser.parse_args()
#    print args     used for debug
    settings = GLOBJ()
    settings.init('target',               args.target_url)
    settings.init('parameters',           args.parameters)
    settings.init('vuln_param',           args.vulnerable_parameter)
    settings.init('method',               args.method)
    settings.init('headers',              args.add_header)
    settings.init('template',             args.add_template)
    settings.init('mode',                 args.mode)
#-------------------------------------------------------------------------
    if args.mode == 'XPI':
        methods_check(args,                   mode_XPI)
        boolean_based_check(args.boolean_based,     mode_XPI)
        settings.init('b',                    args.boolean_based)
        settings.init('t',                    args.time_based)
        #request_based_check(    args.request_based,     mode_XPI)
        if args.request_based != None:
            port_check(args.request_based[1],  mode_XPI)
            settings.init('r',                    args.request_based)
#-------------------------------------------------------------------------
    elif args.mode == 'ext':
        settings.init('ext',                  args.EXT_FUNC)
#-------------------------------------------------------------------------
        if args.EXT_FUNC == 'XXE':
            settings.init('file',                 args.file_path)
            port_check(args.port,              mode_XXE)
            settings.init('r',                    [
                          args.public_ip,         args.port])
#-------------------------------------------------------------------------
        else:
            methods_check(args,                   mode_unparsed_text)
            settings.init('file',                 args.file_path)
            if args.request_based != None:
                port_check(args.request_based[1],  mode_unparsed_text)
                settings.init('r',                    args.request_based)
#-------------------------------------------------------------------------
    else:
        methods_check(args,                   mode_test)
        boolean_based_check(args.boolean_based,     mode_test)
        settings.init('b',                    args.boolean_based)
        settings.init('t',                    args.time_based)
        if args.request_based != None:
            port_check(args.request_based[1],  mode_test)
            settings.init('r',                    args.request_based)
#-------------------------------------------------------------------------
    settings.show() #   used for debug
    return settings
