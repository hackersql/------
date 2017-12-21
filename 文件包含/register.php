<?php

if ($_POST['username'] && $_POST['password']) {
    require_once('config.php');

    $username = $_POST['username'];
    $password = md5($_POST['password']);

    $mysqli = @new mysqli($dbhost, $dbuser, $dbpass, $dbname);
    if ($mysqli->connect_errno) {
        die("could not connect to the database:\n" . $mysqli->connect_error);
    }
    $mysqli->set_charset("utf8");
    $sql = "select * from user where username=?";
    $stmt = $mysqli->prepare($sql);
    $stmt->bind_param("s", $username);
    $stmt->bind_result($res_id, $res_username, $res_password);
    $stmt->execute();
    $stmt->store_result();
    $count = $stmt->num_rows();
    if($count) {
        die('User name Already Exists');
    } else {
        $sql = "insert into user(username, password) values(?,?)";
        $stmt = $mysqli->prepare($sql);
        $stmt->bind_param("ss", $username, $password);
        $stmt->execute();
        echo 'Register OK!<a href="index.php">Please Login</a>';
    }
    $stmt->close();
    $mysqli->close();
} else {

?>
<!DOCTYPE html>
<html>
<head>
   <title>Login</title>
   <link href="static/bootstrap.min.css" rel="stylesheet">
   <script src="static/jquery.min.js"></script>
   <script src="static/bootstrap.min.js"></script>
</head>
<body>
	<div class="container" style="margin-top:100px">  
		<form action="register.php" method="post" class="well" style="width:220px;margin:0px auto;">
			<h3>Register</h3>
			<label>Username:</label>
			<input type="text" name="username" style="height:30px"class="span3"/>
			<label>Password:</label>
			<input type="password" name="password" style="height:30px" class="span3">

			<button type="submit" class="btn btn-primary">REGISTER</button>
		</form>
	</div>
</body>
</html>
<?php
	}
?>
