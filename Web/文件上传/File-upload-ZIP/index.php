<?php
if (isset($_FILES['zipfile'])) {
	//判断文件类型
	if ($_FILES['zipfile']['type'] === "application/zip" || $_FILES['zipfile']['type'] === "application/x-zip-compressed" || $_FILES['zipfile']['type'] === "application/octet-stream") {
		//uniqid() 函数基于以微秒计的当前时间，生成一个唯一的23个字符长的字符串标识符。
		//生成随机目录名
		$uploaddir = 'tmp/upload/' . uniqid("", true) . '/';
		mkdir($uploaddir, 0750, true);
/*$_FILES['userfile']['name']
客户端机器文件的原名称。

$_FILES['userfile']['type']
文件的 MIME 类型，如果浏览器提供此信息的话。一个例子是“image/gif”。不过此 MIME 类型在 PHP 端并不检查，因此不要想当然认为有这个值。

$_FILES['userfile']['size']
已上传文件的大小，单位为字节。

$_FILES['userfile']['tmp_name']
文件被上传后在服务端储存的临时文件名。

$_FILES['userfile']['error']
和该文件上传相关的错误代码。此项目是在 PHP 4.2.0 版本中增加的。*/
		//basename() 函数返回路径中的文件名部分。
		//文件名md5后加后缀.zip
		$uploadfile = $uploaddir . md5(basename($_FILES['zipfile']['name'])) . '.zip';
		if (move_uploaded_file($_FILES['zipfile']['tmp_name'], $uploadfile)) {
			$message = "<p>File uploaded</p> ";
		} else {
			$message = "<p>Error!</p>";
		}

		$zip = new ZipArchive;
		if ($zip->open($uploadfile)) {
			// Don't know if this is safe, but it works, someone told me the flag is N3v3r_7rU5T_u5Er_1npU7 , did not understand what it means
			exec("/usr/bin/timeout -k2 3 /usr/bin/unzip '$uploadfile' -d '$uploaddir'", $output, $ret);
			$message = "<p>File unzipped <a href='" . $uploaddir . "'>here</a>.</p>";
			$zip->close();
		} else {
			$message = "<p> Decompression Error </p>";
		}
	} else {

		$message = "<p> Error bad file type ! <p>";
	}

}
?>

<html>
    <body>
        <h1>ZIP upload</h1>
        <?php print $message;?>
        <form enctype="multipart/form-data" method="post" action>
            <input name="zipfile" type="file">
            <button type="submit">Submit</button>
        </form>
    </body>
</html>