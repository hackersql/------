import sys
sys.path.append('modules/')
from cmdline import cmdLineParser
from network_connection import NETCON
from global_object import GLOBJ
import boolean_tester
import time_tester
import request_tester
##########################################################################


##########################################################################
if __name__ == "__main__":
    settings = cmdLineParser()
    netcon = NETCON(settings.get('method'), settings.get('target'), settings.get('parameters'),
                    settings.get('vuln_param'), settings.get('headers'))
    if settings.get('mode') == 'XPI':
        if settings.available('b'):
            print '[\033[94mINFO\033[92m]: XPATH'
            boolean_tester.scan(settings,   netcon, '')
            print '[\033[94mINFO\033[92m]: XQUERY'
            boolean_tester.scan(settings,   netcon, 'root()')
        if settings.available('r'):
            print '[\033[94mINFO\033[92m]: XQUERY'
            request_tester.scan(settings,   netcon, 'root()')
        if settings.available('t'):
            print '[\033[94mINFO\033[92m]: XQUERY'
            time_tester.scan(settings,   netcon, 'root()')
    elif settings.get('mode') == 'test':
        print '[\033[94mINFO\033[92m]: XPATH'
        boolean_tester.test(settings,   netcon, '')
        print '[\033[94mINFO\033[92m]: XQUERY'
        request_tester.test(settings,   netcon, 'root()')
        boolean_tester.test(settings,   netcon, 'root()')
        time_tester.test(settings,   netcon, 'root()')
    elif settings.get('mode') == 'ext':
        print '[\033[94mINFO\033[92m]: XQUERY'
        request_tester.ext(settings,   netcon, '')
    exit()
