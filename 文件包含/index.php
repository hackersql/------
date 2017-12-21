<?php
error_reporting(0);
session_start();
if (isset($_GET['action'])) {
    include $_GET['action'];
    exit();
} else {
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>Login</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="css/bootstrap.css" rel="stylesheet" media="screen">
    <link href="css/main.css" rel="stylesheet" media="screen">
</head>
<body>
<div class="container">
    <div class="form-signin">
        <?php if (isset($_SESSION['username'])) { ?>
            <?php echo "<div class=\"alert alert-success\">You have been <strong>successfully logged in</strong>.</div>
<a href=\"index.php?action=logout.php\" class=\"btn btn-default btn-lg btn-block\">Logout</a>";}else{ ?>
            <?php echo "<div class=\"alert alert-warning\">Please Login.</div>
<a href=\"index.php?action=login.php\" class=\"btn btn-default btn-lg btn-block\">Login</a>
<a href=\"index.php?action=register.php\" class=\"btn btn-default btn-lg btn-block\">Register</a>";
        } ?>
    </div>
</div>
</body>
</html>

<?php

}
?>


