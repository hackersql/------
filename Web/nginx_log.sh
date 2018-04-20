#!/bin/bash  
# --------------------------------------------------------------------  
#      文件名:analyse_log.sh  
#      版本： v_1.0  
#      日期：2016/7  
#      作者：nextdoor  
#      作用：nginx日志分析工具(可根据日志的格式进行相应修改)  
#       
# --------------------------------------------------------------------  
  
help(){  
    echo  "Usage: ./action.sh [options] [FILE]       "  
    echo  "Options:"  
    echo  "xxx.sh xss    [FILE] 获取成功访问请求中带有xss关键字的日志列表"  
    echo  "xxx.sh sql    [FILE] 获取成功访问请求中带有sql关键字的日志列表"  
    echo  "xxx.sh other  [FILE] 获取成功访问请求中除xss和sql其他漏洞的日志列表"  
    echo  "xxx.sh act1   [FILE] 统计带有攻击关键词的次数和对应恶意ip地址"  
    echo  "xxx.sh act2   [FILE] 统计访问最多的请求接口并显示次数和对应接口"  
    echo  "xxx.sh act3   [FILE] 统计访问最多的ip并显示次数和对应ip"  
    echo  "xxx.sh act4   [FILE] 统计服务器响应时长超过3秒的日志"  
}  
  
  
if [ $# == 0 ]  
then  
    help  
    exit  
fi  
  
if [ ! -e $2 ]  
then  
    echo -e "$2: 日志文件不存在"  
    exit  
fi  
  
if [ ! -d "log" ]  
then  
    mkdir log  
fi  
  
echo "[*] Starting ..."  
  
if  [ $1 == "xss" ]   
then  
    echo "开始获取xss跨站脚本攻击日志..."  
    grep -v '| (200|302|301|500) |' $2 | grep -i -E "(<|>|javascript|data:|vbscript|expression|ed2k|onerror|onmouserover|onload|onclick|onblur|onfocus|eval\(|fromCharCode|%3E|%3C|%25|%27|%0a).*?HTTP/1.1" >> ./log/xss.log  
    echo "分析日志已经保存到./log/xss.log"  
elif [ $1 == "sql" ]  
then  
    echo  "开始获取sql注入漏洞攻击日志..."   
    grep -E '| (200|302|301|500) |' $2 | grep -i -E "('|and |and%20|and\+|and-|and@|and\(|or |or%20|or\+|or-|or@|or\(|--|select|if\(|case when|make_set|elt |extractvalue|updatexml|cast\(|sleep\(|benchmark|generate_series|union|order by).*?HTTP/1.1" >> ./log/sql.log  
    echo "分析日志已经保存到./log/sql.log"  
  
elif [ $1 == "other" ]  
then  
    echo -e "开始获取文件遍历/代码执行/扫描器信息/配置文件等相关日志"  
    grep -E '| (200|302|301|500) |' $2 | grep -i -E "(\.\.|WEB-INF|/etc|\w\{1,6\}\.jsp |\w\{1,6\}\.php |system\(|eval\(|exec\(|acunetix-wvs|Appscan|netsparke|\w+\.xml |\w+\.log |\w+\.swp |\w*\.git |\w*\.svn |\w+\.txt |\w+\.json |\w+\.ini |\w+\.inc |\w+\.rar |\w+\.zip |\w+\.gz |\w+\.tgz|\w+\.bak |/resin-doc).*?HTTP/1.1" >> ./log/other.log  
    echo "分析日志已经保存到./log/other.log"  
elif [ $1 == "act1" ]  
then  
    echo -e "正在统计具有攻击行为的ip的次数和值"  
    #统计具有攻击行为的ip的次数和值，作用是统计出带有攻击关键词的ip和个数。$1对应的是用户的ip列。 
    awk -F "|" '/(and |and%20|and\+|or |or%20|or\+|--|select|if\(|sleep\(|benchmark|union|order by|<|>|javascript|data:|vbscript|expression|onerror|onmouserover|onload|eval\(|\.\.\/|WEB-INF\/|\/etc|exec\(|acunetix-wvs|Appscan|netsparke)/{a[$1]+=1}END{for(i in a){print a[i]" " i;}}' $2  
  
elif [ $1 == "act2" ]  
then  
    echo -e "正在统计访问次数最多ip的次数和值"  
    awk -F '|' '{a[$1]+=1;}END{for(i in a){if(a[i]>=200){if(!match(i,/192.168/)){print a[i]"  "i;}}}}' $2  
  
elif [ $1 == "act3" ]  
then  
    echo -e "正在统计访问次数最多的请求接口的url的次数和值" 
    #统计访问次数最多的请求接口的url的次数和值，作用同上，$4对应日志请求path。
    awk -F '|' '{a[$4]+=1;}END{for(i in a){if(a[i]>=100){if(!match(i,/(gif|png|jpg|ico)/)){print a[i]"  "i;}}}}' $2  
  
elif [ $1 == "act4" ]  
then  
    echo -e "正在统计请求时长超过3秒的日志"  
    #统计请求时长超过3秒的用户，主要统计延时注入和某个接口被拒绝服务攻击。$12是请求的响应时间列
    awk -F '|' '{if($12 > 3){print $0}else}' $2  
else   
    help  
fi  
  
echo "[*] shut down"  