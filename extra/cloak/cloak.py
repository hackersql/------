#!/usr/bin/env python
#coding=utf-8
"""
cloak.py - Simple file encryption/compression utility

Copyright (c) 2006-2017 sqlmap developers (http://sqlmap.org/)
See the file 'doc/COPYING' for copying permission
"""

import os
import sys
import zlib

from optparse import OptionError
from optparse import OptionParser

def hideAscii(data):
    retVal = ""
    for i in xrange(len(data)):
        if ord(data[i]) < 128:
            retVal += chr(ord(data[i]) ^ 127)
        else:
            retVal += data[i]

    return retVal

def cloak(inputFile=None, data=None):
    if data is None:
        with open(inputFile, "rb") as f:
            data = f.read()

    return hideAscii(zlib.compress(data))

def decloak(inputFile=None, data=None):
    if data is None:
        with open(inputFile, "rb") as f:
            data = f.read()
    try:
        data = zlib.decompress(hideAscii(data))
    except:
        print '错误：提供的输入文件\'%s\'不包含有效的隐藏内容' % inputFile
        sys.exit(1)
    finally:
        f.close()

    return data

def main():
    usage = '%s [-d] -i <input file> [-o <output file>]' % sys.argv[0]
    parser = OptionParser(usage=usage, version='0.1')

    try:
        parser.add_option('-d', dest='decrypt', action="store_true", help='Decrypt')
        parser.add_option('-i', dest='inputFile', help='Input file')
        parser.add_option('-o', dest='outputFile', help='Output file')

        (args, _) = parser.parse_args()

        if not args.inputFile:
            parser.error('缺少输入文件，-h寻求帮助')

    except (OptionError, TypeError), e:
        parser.error(e)

    if not os.path.isfile(args.inputFile):
        print '错误：提供的输入文件\'%s\'不存在' % args.inputFile
        sys.exit(1)

    if not args.decrypt:
        data = cloak(args.inputFile)
    else:
        data = decloak(args.inputFile)

    if not args.outputFile:
        if not args.decrypt:
            args.outputFile = args.inputFile + '_'
        else:
            args.outputFile = args.inputFile[:-1]

    f = open(args.outputFile, 'wb')
    f.write(data)
    f.close()

if __name__ == '__main__':
    main()
