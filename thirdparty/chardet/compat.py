#!/usr/bin/env python
#coding=utf-8

import sys
"""
sys.version_info
(major=2, minor=7, micro=13, releaselevel='final', serial=0)
major:重大的（更新）
minor:次要（的迭代）
micro:微（小的改进）
releaselevel发布级别
sys.version
'2.7.13 (v2.7.13:a06454b1afa1, Dec 17 2016, 20:42:59) [MSC v.1500 32 bit (Intel)]'
"""

# 检测python版本是2.X还是3.X
if sys.version_info < (3, 0):
    base_str = (str, unicode)
else:
    base_str = (bytes, str)


def wrap_ord(a):
    if sys.version_info < (3, 0) and isinstance(a, base_str):
        return ord(a)
    else:
        return a

"""
将ASCLL码值转换为字符 
示例：
ord('a')表示a在ASSCLL码中的序号，为97；

另外 chr是 ord 的互逆函数 也就是说 chr(97)=a
"""