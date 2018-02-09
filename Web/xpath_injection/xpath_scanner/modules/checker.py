import time
import socket
import re
#-------------------------------------------------------------------------------


def bb_checker(_netcon,    _warhead,   _required,  _type):  # bb_checker
    if _type == 'true':
        if _required in _netcon.request(_warhead):
            return True
        return False
    else:
        if _required in _netcon.request(_warhead):
            return False
        return True
#-------------------------------------------------------------------------------


def tb_checker(_netcon,    _warhead,   _time):  # tb_checker
    # Most databases terminate, while they try execute cycle calculations
    time.sleep(5.0)
    time_start = time.time()
    _netcon.request(_warhead)
    if time.time() - time_start >= _time:
        return True
    return False
