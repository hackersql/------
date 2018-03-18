#Requests Header | Http Header
  <table> 
   <thead> 
    <tr> 
     <th width="50%">Header </th> 
     <th width="35%">解释</th> 
     <th width="80%">示例</th> 
    </tr> 
   </thead> 
   <tbody> 
    <tr> 
     <td>Accept </td> 
     <td>指定客户端能够接收的内容类型</td> 
     <td>Accept: text/plain, text/html</td> 
    </tr> 
    <tr> 
     <td>Accept-Charset</td> 
     <td>浏览器可以接受的字符编码集。</td> 
     <td>Accept-Charset: iso-8859-5</td> 
    </tr> 
    <tr> 
     <td>Accept-Encoding</td> 
     <td>指定浏览器可以支持的web服务器返回内容压缩编码类型。</td> 
     <td>Accept-Encoding: compress, gzip</td> 
    </tr> 
    <tr> 
     <td>Accept-Language</td> 
     <td>浏览器可接受的语言</td> 
     <td>Accept-Language: en,zh</td> 
    </tr> 
    <tr> 
     <td>Accept-Ranges</td> 
     <td>可以请求网页实体的一个或者多个子范围字段</td> 
     <td>Accept-Ranges: bytes</td> 
    </tr> 
    <tr> 
     <td>Authorization</td> 
     <td>HTTP授权的授权证书</td> 
     <td>Authorization: Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ==</td> 
    </tr> 
    <tr> 
     <td>Cache-Control</td> 
     <td>指定请求和响应遵循的缓存机制</td> 
     <td>Cache-Control: no-cache</td> 
    </tr> 
    <tr> 
     <td>Connection</td> 
     <td>表示是否需要持久连接。（HTTP 1.1默认进行持久连接）</td> 
     <td>Connection: close</td> 
    </tr> 
    <tr> 
     <td>Cookie</td> 
     <td>HTTP请求发送时，会把保存在该请求域名下的所有cookie值一起发送给web服务器。</td> 
     <td>Cookie: $Version=1; Skin=new;</td> 
    </tr> 
    <tr> 
     <td>Content-Length</td> 
     <td>请求的内容长度</td> 
     <td>Content-Length: 348</td> 
    </tr> 
    <tr> 
     <td>Content-Type</td> 
     <td>请求的与实体对应的MIME信息</td> 
     <td>Content-Type: application/x-www-form-urlencoded</td> 
    </tr> 
    <tr> 
     <td>Date</td> 
     <td>请求发送的日期和时间</td> 
     <td>Date: Tue, 15 Nov&nbsp;2010 08:12:31 GMT</td> 
    </tr> 
    <tr> 
     <td>Expect</td> 
     <td>请求的特定的服务器行为</td> 
     <td>Expect: 100-continue</td> 
    </tr> 
    <tr> 
     <td>From</td> 
     <td>发出请求的用户的Email</td> 
     <td>From: user@email.com</td> 
    </tr> 
    <tr> 
     <td>Host</td> 
     <td>指定请求的服务器的域名和端口号</td> 
     <td>Host: www.zcmhi.com</td> 
    </tr> 
    <tr> 
     <td>If-Match</td> 
     <td>只有请求内容与实体相匹配才有效</td> 
     <td>If-Match: “737060cd8c284d8af7ad3082f209582d”</td> 
    </tr> 
    <tr> 
     <td>If-Modified-Since</td> 
     <td>如果请求的部分在指定时间之后被修改则请求成功，未被修改则返回304代码</td> 
     <td>If-Modified-Since: Sat, 29 Oct 2010 19:43:31 GMT</td> 
    </tr> 
    <tr> 
     <td>If-None-Match</td> 
     <td>如果内容未改变返回304代码，参数为服务器先前发送的Etag，与服务器回应的Etag比较判断是否改变</td> 
     <td>If-None-Match: “737060cd8c284d8af7ad3082f209582d”</td> 
    </tr> 
    <tr> 
     <td>If-Range</td> 
     <td>如果实体未改变，服务器发送客户端丢失的部分，否则发送整个实体。参数也为Etag</td> 
     <td>If-Range: “737060cd8c284d8af7ad3082f209582d”</td> 
    </tr> 
    <tr> 
     <td>If-Unmodified-Since</td> 
     <td>只在实体在指定时间之后未被修改才请求成功</td> 
     <td>If-Unmodified-Since: Sat, 29 Oct 2010 19:43:31 GMT</td> 
    </tr> 
    <tr> 
     <td>Max-Forwards</td> 
     <td>限制信息通过代理和网关传送的时间</td> 
     <td>Max-Forwards: 10</td> 
    </tr> 
    <tr> 
     <td>Pragma</td> 
     <td>用来包含实现特定的指令</td> 
     <td>Pragma: no-cache</td> 
    </tr> 
    <tr> 
     <td>Proxy-Authorization</td> 
     <td>连接到代理的授权证书</td> 
     <td>Proxy-Authorization: Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ==</td> 
    </tr> 
    <tr> 
     <td>Range</td> 
     <td>只请求实体的一部分，指定范围</td> 
     <td>Range: bytes=500-999</td> 
    </tr> 
    <tr> 
     <td>Referer</td> 
     <td>先前网页的地址，当前请求网页紧随其后,即来路</td> 
     <td>Referer: http://www.zcmhi.com/archives/71.html</td> 
    </tr> 
    <tr> 
     <td>TE</td> 
     <td>客户端愿意接受的传输编码，并通知服务器接受接受尾加头信息</td> 
     <td>TE: trailers,deflate;q=0.5</td> 
    </tr> 
    <tr> 
     <td>Upgrade</td> 
     <td>向服务器指定某种传输协议以便服务器进行转换（如果支持）</td> 
     <td>Upgrade: HTTP/2.0, SHTTP/1.3, IRC/6.9, RTA/x11</td> 
    </tr> 
    <tr> 
     <td>User-Agent</td> 
     <td>User-Agent的内容包含发出请求的用户信息</td> 
     <td>User-Agent: Mozilla/5.0 (Linux; X11)</td> 
    </tr> 
    <tr> 
     <td>Via</td> 
     <td>通知中间网关或代理服务器地址，通信协议</td> 
     <td>Via: 1.0 fred, 1.1 nowhere.com (Apache/1.1)</td> 
    </tr> 
    <tr> 
     <td>Warning</td> 
     <td>关于消息实体的警告信息</td> 
     <td>Warn: 199 Miscellaneous warning</td> 
    </tr> 
   </tbody> 
  </table>

#Responses 部分 | Http Header 

  <table> 
   <thead> 
    <tr> 
     <th>Header</th> 
     <th width="35%">解释</th> 
     <th width="40%">示例</th> 
    </tr> 
   </thead> 
   <tbody> 
    <tr> 
     <td>Accept-Ranges</td> 
     <td>表明服务器是否支持指定范围请求及哪种类型的分段请求</td> 
     <td>Accept-Ranges: bytes</td> 
    </tr> 
    <tr> 
     <td>Age</td> 
     <td>从原始服务器到代理缓存形成的估算时间（以秒计，非负）</td> 
     <td>Age: 12</td> 
    </tr> 
    <tr> 
     <td>Allow</td> 
     <td>对某网络资源的有效的请求行为，不允许则返回405</td> 
     <td>Allow: GET, HEAD</td> 
    </tr> 
    <tr> 
     <td>Cache-Control</td> 
     <td>告诉所有的缓存机制是否可以缓存及哪种类型</td> 
     <td>Cache-Control: no-cache</td> 
    </tr> 
    <tr> 
     <td>Content-Encoding</td> 
     <td>web服务器支持的返回内容压缩编码类型。</td> 
     <td>Content-Encoding: gzip</td> 
    </tr> 
    <tr> 
     <td>Content-Language</td> 
     <td>响应体的语言</td> 
     <td>Content-Language: en,zh</td> 
    </tr> 
    <tr> 
     <td>Content-Length</td> 
     <td>响应体的长度</td> 
     <td>Content-Length: 348</td> 
    </tr> 
    <tr> 
     <td>Content-Location</td> 
     <td>请求资源可替代的备用的另一地址</td> 
     <td>Content-Location: /index.htm</td> 
    </tr> 
    <tr> 
     <td>Content-MD5</td> 
     <td>返回资源的MD5校验值</td> 
     <td>Content-MD5: Q2hlY2sgSW50ZWdyaXR5IQ==</td> 
    </tr> 
    <tr> 
     <td>Content-Range</td> 
     <td>在整个返回体中本部分的字节位置</td> 
     <td>Content-Range: bytes 21010-47021/47022</td> 
    </tr> 
    <tr> 
     <td>Content-Type</td> 
     <td>返回内容的MIME类型</td> 
     <td>Content-Type: text/html; charset=utf-8</td> 
    </tr> 
    <tr> 
     <td>Date</td> 
     <td>原始服务器消息发出的时间</td> 
     <td>Date: Tue, 15 Nov 2010 08:12:31 GMT</td> 
    </tr> 
    <tr> 
     <td>ETag</td> 
     <td>请求变量的实体标签的当前值</td> 
     <td>ETag: “737060cd8c284d8af7ad3082f209582d”</td> 
    </tr> 
    <tr> 
     <td>Expires</td> 
     <td>响应过期的日期和时间</td> 
     <td>Expires: Thu, 01 Dec 2010 16:00:00 GMT</td> 
    </tr> 
    <tr> 
     <td>Last-Modified</td> 
     <td>请求资源的最后修改时间</td> 
     <td>Last-Modified: Tue, 15 Nov 2010 12:45:26 GMT</td> 
    </tr> 
    <tr> 
     <td>Location</td> 
     <td>用来重定向接收方到非请求URL的位置来完成请求或标识新的资源</td> 
     <td>Location: http://www.zcmhi.com/archives/94.html</td> 
    </tr> 
    <tr> 
     <td>Pragma</td> 
     <td>包括实现特定的指令，它可应用到响应链上的任何接收方</td> 
     <td>Pragma: no-cache</td> 
    </tr> 
    <tr> 
     <td>Proxy-Authenticate</td> 
     <td>它指出认证方案和可应用到代理的该URL上的参数</td> 
     <td>Proxy-Authenticate: Basic</td> 
    </tr> 
    <tr> 
     <td>refresh</td> 
     <td>应用于重定向或一个新的资源被创造，在5秒之后重定向（由网景提出，被大部分浏览器支持）</td> 
     <td> Refresh: 5; url=http://www.atool.org/httptest.php </td> 
    </tr> 
    <tr> 
     <td>Retry-After</td> 
     <td>如果实体暂时不可取，通知客户端在指定时间之后再次尝试</td> 
     <td>Retry-After: 120</td> 
    </tr> 
    <tr> 
     <td>Server</td> 
     <td>web服务器软件名称</td> 
     <td>Server: Apache/1.3.27 (Unix) (Red-Hat/Linux)</td> 
    </tr> 
    <tr> 
     <td>Set-Cookie</td> 
     <td>设置Http Cookie</td> 
     <td>Set-Cookie: UserID=JohnDoe; Max-Age=3600; Version=1</td> 
    </tr> 
    <tr> 
     <td>Trailer</td> 
     <td>指出头域在分块传输编码的尾部存在</td> 
     <td>Trailer: Max-Forwards</td> 
    </tr> 
    <tr> 
     <td>Transfer-Encoding</td> 
     <td>文件传输编码</td> 
     <td><span style="font-family: monospace;"><span style="font-family: Georgia,'Times New Roman','Bitstream Charter',Times,serif;">Transfer-Encoding:chunked</span></span> </td> 
    </tr> 
    <tr> 
     <td>Vary</td> 
     <td>告诉下游代理是使用缓存响应还是从原始服务器请求</td> 
     <td>Vary: *</td> 
    </tr> 
    <tr> 
     <td>Via</td> 
     <td>告知代理客户端响应是通过哪里发送的</td> 
     <td>Via: 1.0 fred, 1.1 nowhere.com (Apache/1.1)</td> 
    </tr> 
    <tr> 
     <td>Warning</td> 
     <td>警告实体可能存在的问题</td> 
     <td>Warning: 199 Miscellaneous warning</td> 
    </tr> 
    <tr> 
     <td>WWW-Authenticate</td> 
     <td>表明客户端请求实体应该使用的授权方案</td> 
     <td>WWW-Authenticate: Basic</td> 
    </tr> 
   </tbody> 
  </table> 