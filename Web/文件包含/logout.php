<?php
session_start();
session_destroy();
ob_start();
header("location:index.php");
ob_end_flush();
