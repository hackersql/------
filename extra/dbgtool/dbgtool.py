#!/usr/bin/env python
#coding=utf-8
"""
dbgtool.py - Portable executable to ASCII debug script converter

Copyright (c) 2006-2017 sqlmap developers (http://sqlmap.org/)
See the file 'doc/COPYING' for copying permission
"""

import os
import sys
import struct

from optparse import OptionError
from optparse import OptionParser

def convert(inputFile):
    fileStat = os.stat(inputFile)
    fileSize = fileStat.st_size

    if fileSize > 65280:
        print "错误：提供的输入文件'%s'对于debug.exe来说太大了" % inputFile
        sys.exit(1)

    script = "n %s\nr cx\n" % os.path.basename(inputFile.replace(".", "_"))
    script += "%x\nf 0100 ffff 00\n" % fileSize
    scrString = ""
    counter = 256
    counter2 = 0

    fp = open(inputFile, "rb")
    fileContent = fp.read()

    for fileChar in fileContent:
        unsignedFileChar = struct.unpack("B", fileChar)[0]

        if unsignedFileChar != 0:
            counter2 += 1

            if not scrString:
                scrString = "e %0x %02x" % (counter, unsignedFileChar)
            else:
                scrString += " %02x" % unsignedFileChar
        elif scrString:
            script += "%s\n" % scrString
            scrString = ""
            counter2 = 0

        counter += 1

        if counter2 == 20:
            script += "%s\n" % scrString
            scrString = ""
            counter2 = 0

    script += "w\nq\n"

    return script

def main(inputFile, outputFile):
    if not os.path.isfile(inputFile):
        print "错误：提供的输入文件'%s'不是正常文件" % inputFile
        sys.exit(1)

    script = convert(inputFile)

    if outputFile:
        fpOut = open(outputFile, "w")
        sys.stdout = fpOut
        sys.stdout.write(script)
        sys.stdout.close()
    else:
        print script

if __name__ == "__main__":
    usage = "%s -i <input file> [-o <output file>]" % sys.argv[0]
    parser = OptionParser(usage=usage, version="0.1")

    try:
        parser.add_option("-i", dest="inputFile", help="Input binary file")

        parser.add_option("-o", dest="outputFile", help="Output debug.exe text file")

        (args, _) = parser.parse_args()

        if not args.inputFile:
            parser.error("缺少输入文件，-h寻求帮助")

    except (OptionError, TypeError), e:
        parser.error(e)

    inputFile = args.inputFile
    outputFile = args.outputFile

    main(inputFile, outputFile)
