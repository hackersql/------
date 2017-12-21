<?php

class Test
{
    public $variable = 'BUZZ';
    public $variable2 = 'OTHER';

    public function PrintVariable()
    {
        echo $this->variable . '<br />';
    }

    public function __construct()
    {
        echo '__construct<br />';
    }

    public function __destruct()
    {
        echo '__destruct<br />';
    }

    public function __wakeup()
    {
        echo '__wakeup<br />';
    }

    public function __sleep()
    {
        echo '__sleep<br />';

        return array('variable', 'variable2');
    }
}

// 创建一个对象，会调用 __construct

$obj = new Test();

// 序列化一个对象，会调用 __sleep

$serialized = serialize($obj);

//输出序列化后的字符串

print 'Serialized: ' . $serialized . '<br />';

// 重建对象，会调用 __wakeup

$obj2 = unserialize($serialized);

//调用 PintVariable, 会输出数据 (BUZZ)

$obj2->PrintVariable();

// php脚本结束，会调用 __destruct 

?>