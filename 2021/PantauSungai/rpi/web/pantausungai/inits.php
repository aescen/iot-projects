<?php
  require_once 'db.php';
  $strTurbidity = 'turbidity';
  $arrStrStatus = ['-1' => 'tidak diketahui',
                    '0' => 'sungai bersih',
                    '1' => 'sungai kotor'];
  
  function checkServer($host = '127.0.0.1', $port = '8080', $timeout = 20){
    try {
      $socket = @fsockopen($host, $port, $errno, $errstr, $timeout);
      if($socket){
        return true;
      } else{
        throw new Exception("Cannot connect to host on port");
      }
    }
    catch(Exception $e) {
      return false;
    }
  }
  
  function loadResource(){
    if(checkServer() !== false) {
      return 'http://127.0.0.1:8080/image';
    } else {
      return './static/images/videofeed.png';
    }
  }
  
  $IMAGE_SRC= loadResource();
?>