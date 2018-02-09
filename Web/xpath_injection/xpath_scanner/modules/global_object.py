keys = ['target', 'template', 'parameters', 'vuln_param',
        'method', 'headers', 'mode', 'file', 'ext', 'b', 't', 'r']
################################################################################


class GLOBJ:
    def __init__(self):  # __init__
        self.d = {}
        for key in keys:
            self.d.setdefault(key)
#-------------------------------------------------------------------------------

    def init(self, _key, _data):  # init
        self.d.update({_key: _data})
#-------------------------------------------------------------------------------

    def available(self, _key):  # available
        if self.d.get(_key) == None:
            return False
        else:
            return True
#-------------------------------------------------------------------------------

    def get(self, _key):  # get
        return self.d.get(_key)
#-------------------------------------------------------------------------------
#    def show(self): #   used for debug                                          #show
#        print self.d
################################################################################
