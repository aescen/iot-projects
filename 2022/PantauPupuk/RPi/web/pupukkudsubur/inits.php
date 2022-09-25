<?php	
  define('FERTILIZER_TYPE', array("fertilizer_1" => "NPK", "fertilizer_2" => "ZA", "fertilizer_3" => "KOMPOS"));

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
  
  function map($x, $in_min, $in_max, $out_min, $out_max, $precision=2) {
    return round(($x - $in_min) * ($out_max - $out_min) / ($in_max - $in_min) + $out_min, $precision);
  }
?>