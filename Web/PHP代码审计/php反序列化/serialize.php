<?php

class User
{
	public $age = 0;
	public $name = '';

	public function PrintDate()
	{
		echo 'User ' . $this->name . 'is ' . $this->age . ' years old. <br />';
	}
}

$usr = new User();

$usr->age = 20;
$usr->name = 'John';

$usr->PrintDate();

echo serialize($usr);

echo "<br /><br />序列化与反序列化";

class UUser
{
	public $aage = 0;
	public $nname = '';

	public function PPrintDate()
	{
		echo '<br /> UUser ' . $this->nname . ' is ' . $this->aage . ' years old. <br />';
	}
}
echo '<br /><br />O:5:"UUser":2:{s:4:"aage";i:20;s:5:"nname";s:4:"John";}';

$uusr = unserialize('O:5:"UUser":2:{s:4:"aage";i:20;s:5:"nname";s:4:"John";}');

$uusr->PPrintDate();



/*

字符串
s:size:value;

数值型
i:value;

布尔型
b:value; (不存储"true" or "false", 只存储'1' or '0')

Null
N;

数组
a:size:{key definition;value definition;}

Object对象
O:strlen(object name):object name:object size:{s:strlen(property name):property name:property definition;}

字符串值用双引号包围
数组键总是整数或字符串
    "null => 'value'" 等同于 's:0:"";s:5:"value";',
    "true => 'value'" 等同于 'i:1;s:5:"value";',
    "false => 'value'" 等同于 'i:0;s:5:"value";',
*/
?>