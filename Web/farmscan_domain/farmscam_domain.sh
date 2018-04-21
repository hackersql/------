#!/bin/bash
rm -rf ips 
rm -rf mail 
rm -rf domain
rm -rf *.txt
echo "pls input domain name,like:sina.com"
read domain
cd ./subDomainsBrute&&python subDomainsBrute.py $domain -o ../1$domain.txt 
cd ../Sublist3r&&python sublist3r.py -d $domain -o ../2$domain.txt
cd ../teemo&&python teemo.py -d $domain -o ../../3$domain.txt
cd ..
cat 3*.txt |grep @ >>mail
cat 1*.txt |awk '{print($1)}'>>a.txt
cat 1*.txt |sed 's/,//g'|awk '{print($2)}'>>b.txt
cat b.txt|while read ip
do
ipcalc -n $ip/28 |grep Network |awk '{print ($2)}'>>ips.txt
done
cat 3*.txt |grep / >>ips.txt
cat ips.txt|sort|uniq >>ips
cat 2*.com.txt >>a.txt
cat 3*.com.txt |grep -v @|grep -v / |awk '{print($1)}' |grep -v ^[0-9]>>a.txt
cat a.txt|sort|uniq>>domain
rm -rf *.txt
echo "IP段计算完毕，请查看ips文件"
echo "邮箱计算完毕，请查看mail文件"
echo "域名计算完毕，请查看domain文件"
