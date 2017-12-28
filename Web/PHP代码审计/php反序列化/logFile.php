<?php

class logFile
{
	public $filename = 'error.log';

	public function logData($text)
	{
		echo 'Log some data: ' . $text . '<br />';
	}

	public function __destruct()
	{
		echo '__destruct delete ' . $this->filename . ' file. <br />';
		print dirname(__FILE__);
		unlink(dirname(__FILE__) . '/' . $this->filename);
	}
}
?>