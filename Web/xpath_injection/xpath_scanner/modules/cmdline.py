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
        print '[\033[91mERROR\033[92m]: No one XPI method was chosen'
        second_object.print_help()
        exit()
#-------------------------------------------------------------------------


def port_check(first_object, second_object):  # port_check
    if first_object.isdigit() == False or int(first_object) < 1:
        print('[\033[91mERROR\033[92m]: The last argument for request-based'
              + ' method must be positive integer')
        second_object.print_help()
        exit()
#-------------------------------------------------------------------------


def boolean_based_check(first_object, second_object):  # boolean_based_check
    if first_object != None:
        if first_object[0] != 'true' and first_object[0] != 'false':
            print('[\033[91mERROR\033[92m]: The firs argument for boolean-based'
                  + ' method must be "true" or "false"')
            second_object.print_help()
            exit()
#-------------------------------------------------------------------------


def request_based_check(first_object, second_object):  # request_based_check
    if first_object != None:
        if first_object[0] != 'doc' and first_object[0] != 'unparsed-text':
            print('[\033[91mERROR\033[92m]: The firs argument for request-based'
                  + ' method must be "doc" or "unparsed-text"')
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
                     help='local path to the file on the target machine')
    XXE.add_argument('public_ip',
                     type=str,
                     help='your public ip')
    XXE.add_argument('port',
                     type=str,
                     help='port')
#-------------------------------------------------------------------------
#   RLF arguments parser
    RLF = argparse.ArgumentParser(add_help=False)
    RLF.add_argument('file_path',
                     type=str,
                     help='local path to the file on the target machine')
#-------------------------------------------------------------------------
#   extended functionality arguments parser
    ext = argparse.ArgumentParser(add_help=False)
    parse_mode = ext.add_subparsers(title='Extended functionality',
                                    dest='EXT_FUNC',
                                    metavar=('EXT_FUNC'),
                                    help='choose extended functionality')
    mode_XXE = parse_mode.add_parser('XXE',
                                     prog=programm_name,
                                     parents=[XXE],
                                     help='XXE read local file')
    mode_unparsed_text = parse_mode.add_parser('RLF',
                                               prog=programm_name,
                                               # boolean_based,time_based],
                                               parents=[request_based, RLF],
                                               usage='''\
%(prog)s  -r public-ip port
                            file_path''',
                                               help='read local file using unparsed-text function')
#-------------------------------------------------------------------------
#   modes arguments parser
    modes = argparse.ArgumentParser(prog=programm_name,
                                    add_help=False)
    parse_mode = modes.add_subparsers(title=programm_name + ' functionality',
                                      description='Available functionality',
                                      dest='mode',
                                      metavar=('MODE'),
                                      help='Choose XPI methods, extended functionality or'
                                      ' use simple tests for checking')
    mode_XPI = parse_mode.add_parser('XPI',
                                     prog=programm_name,
                                     parents=[boolean_based,
                                              time_based, request_based],
                                     usage='''\
%(prog)s  -b [ true | false ] string
                            -t seconds
                            -r public-ip port''',
                                     help='XPI methods')
    mode_ext = parse_mode.add_parser('ext',
                                     prog=programm_name,
                                     parents=[ext],
                                     help='Extended functionality')
    mode_test = parse_mode.add_parser('test',
                                      prog=programm_name,
                                      parents=[boolean_based,
                                               time_based, request_based],
                                      usage='''\
%(prog)s  -b [ true | false ] string
                            -t seconds
                            -r public-ip port''',
                                      help='Test XPath injection for parameter,'
                                      ' which was chosen')
#-------------------------------------------------------------------------
#   base arguments parser
    base = argparse.ArgumentParser(add_help=False)
    base.add_argument("--method",
                      help="using HTTP method",
                      type=str,
                      default="GET",
                      choices=("GET", "POST"))
    base.add_argument("--add_header",
                      help="add custom HTTP header",
                      action='append',
                      type=str)
    base.add_argument('--add_template',
                      nargs=2,
                      metavar=(
                          'begining_of_template', 'ending_of_template'),
                      type=str,
                      help='use custom template')
    base.add_argument("target_url",
                      help="site to scan. ex: http://127.0.0.1/WEB_APP/index.php",
                      type=str)
    base.add_argument("parameters",
                      help="parameters. ex: param_1=value_1&param_2=value_2",
                      type=str)
    base.add_argument("vulnerable_parameter",
                      help="vulnerable parameter. ex: value_1",
                      type=str)
#-------------------------------------------------------------------------
#   main arguments parser
    parser = argparse.ArgumentParser(prog=programm_name,
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                     description='Scan your site for XPath vulnerability',
                                     epilog='For the support and suggestions please'
                                     ' write to e-mail obriain@yandex.ru',
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
#    settings.show() #   used for debug
    return settings
