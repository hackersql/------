import re
import socket
import sys
import BHS
import time
import urllib
sys.path.append('modules/')

VAR = None

class MyHandler(BHS.BaseHTTPRequestHandler):
    def do_HEAD(s):
        s.send_response(200)
        s.send_header("Content-type", "text/html")
        s.end_headers()
    def do_GET(s):
        global VAR
        VAR = urllib.unquote(s.path[1:])#.decode('utf16')
        """Respond to a GET request."""
        s.send_response(200)
        s.send_header("Content-type", "application/xml")
        s.end_headers()
        s.wfile.write("<html><head><title>XPath Scanner.</title></head>")
        s.wfile.write("<body><p>request-based method.</p>")
        s.wfile.write("</body></html>")
#-------------------------------------------------------------------------------
if __name__ == "__main__":
#-------------------------------------------------------------------------------
    #global VAR
    f = open('server/log.txt', 'w')
    f.write('begin\n')
    f.flush()
    public_ip = sys.argv[1]
    f.write(public_ip+'\n')
    f.flush()
    port = int(sys.argv[2])
    f.write(sys.argv[2]+'\n')
    f.flush()
    server_address = ('', port)                                                 #public_ip
    socket.setdefaulttimeout(5.0)
    httpd = BHS.HTTPServer(server_address, MyHandler)
#-------------------------------------------------------------------------------
    while True:
        input_var = sys.stdin.readline()
        f.write('new_step\n')
        f.flush()
        time.sleep(0.01)
        if input_var[:5] == 'false':
            break
        f.write('input_var : '+input_var)
        f.flush()

        httpd.handle_request()
        f.write('mysocket\n')
        f.flush()
        #-----------------------------------------------------------
        if VAR != None:
            if not ('TAG' in VAR):
                VAR = '1TAG'+VAR
            f.write(VAR+'\n')
            f.flush()
            sys.stdout.write(VAR+'\n')
            sys.stdout.flush()
        else:

            f.write('No connectionTAG\n')
            f.flush()
            sys.stdout.write('NOCONTAG\n')
            sys.stdout.flush()
        VAR = None
        #-----------------------------------------------------------
        f.write('ending_of_step\n')
        f.flush()
#-------------------------------------------------------------------------------
    f.write('exit\n')
    f.flush()
    exit()
