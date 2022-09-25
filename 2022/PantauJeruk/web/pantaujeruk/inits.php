<?php	
  define('STATUS_SPRAY', array("Tidak menyiram", "Menyiram air", "Menyiram vitamin"));

	function checkServer($host = '127.0.0.1', $port = '5000', $timeout = 20){
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
			return 'http://127.0.0.1:5000/imagestream';
		} else {
			return './static/images/videofeed.png';
		}
	}
	
	$IMAGE_SRC= loadResource();
?>