<?php
	require_once('config.php');
	session_start();
	if($_SESSION['username']) {
		header('Location: index.php');
		exit;
	}
	if($_POST['username'] && $_POST['password']) {
		$username = $_POST['username'];
		$password = md5($_POST['password']);

        $mysqli = @new mysqli($dbhost, $dbuser, $dbpass, $dbname);

        if ($mysqli->connect_errno) {
            die("could not connect to the database:\n" . $mysqli->connect_error);
        }
        $sql = "select password from user where username=?";
        $stmt = $mysqli->prepare($sql);
        $stmt->bind_param("s", $username);
        $stmt->bind_result($res_password);
        $stmt->execute();

        $stmt->fetch();
        if ($res_password == $password) {
            $_SESSION['username'] = base64_encode($username);
            header("location:index.php");
        } else {
            die("Invalid user name or password");
        }
        $stmt->close();
        $mysqli->close();
	}
	else {
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
		<form action="login.php" method="post" class="well" style="width:220px;margin:0px auto;">
			<h3>Login</h3>
			<label>Username:</label>
			<input type="text" name="username" style="height:30px"class="span3"/>
			<label>Password:</label>
			<input type="password" name="password" style="height:30px" class="span3">

			<button type="submit" class="btn btn-primary">LOGIN</button>
		</form>
	</div>
</body>
</html>
<?php
	}
?>
 
