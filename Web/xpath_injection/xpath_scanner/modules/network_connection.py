import urllib, urllib2, re, copy, socket, httplib
from time import gmtime, strftime
from urlparse import urlparse
################################################################################


################################################################################
def search_vuln_param(_params_array, _vuln_param):                              #search_vuln_param
    for i in range(len(_params_array)):
        if i%2 == 0 and _params_array[i] == _vuln_param:
            return i
    print "[\033[91mERROR\033[92m]: Not found vulnerable_parameter in parameters"
    exit()
#-------------------------------------------------------------------------------
def add_warhead(_params_array, _i, _warhead):                                   #add_warhead
    _params_array[_i+1] = _params_array[_i+1] + _warhead
    return _params_array
#-------------------------------------------------------------------------------
def create_data(_params_array):                                                 #create_data
    D = {}
    if len(_params_array) % 2 != 0:
        print "[\033[91mERROR\033[92m]: Wrong parameters format "+_params_array
        exit()
    for i in range(len(_params_array)):
        if i%2 == 0:
            D[_params_array[i]] = _params_array[i+1]
    return D
#-------------------------------------------------------------------------------
def init_headers(_params_array):                                                #init_headers
    D = {}
    for i in _params_array:
        header = re.split(':', i)
        if len(header) != 2:
            print "[\033[91mERROR\033[92m]: Wrong header format %(i)s"
            exit()
        if D.get(header[0]) != None:
            print "[\033[91mERROR\033[92m]: Dublicate header "+header[0]
            exit()
        D[header[0]] = header[1]
    return D
################################################################################


################################################################################
class NETCON:
    def __init__(self, _method, _url, _params, _vuln_param, _headers):          #__init__
        self.method = _method
        object = urlparse(_url)
        self.url = object.netloc
        self.path = object.path
        self.params_array = re.split('=|&', _params)
        if _headers != None:
            self.headers = init_headers(_headers)
        else:
            self.headers = {"User-Agent":"XPath Scanner"}
        self.i = search_vuln_param(self.params_array, _vuln_param)
#-------------------------------------------------------------------------------
    def request(self, _warhead):                                                #request
        _params_array = add_warhead(copy.deepcopy(self.params_array), self.i, _warhead)
        _data = urllib.urlencode(create_data(_params_array))
        try:
            conn = httplib.HTTPConnection(self.url, timeout=3)
            if self.method == "GET":
                conn.request(self.method, self.path+'?'+_data, '', self.headers)
            else:
                conn.request(self.method, self.path, _data, self.headers)
            result = conn.getresponse()
            data = result.read()
            return data
        except httplib.HTTPException, e:
            print '[\033[91mERROR\033[92m]: We failed to reach a server.',e
            print "Paramerers: "+_data
            pass
        except socket.timeout, e:
            print '[\033[91mERROR\033[92m]: We failed to reach a server.'
            exit()
            pass
