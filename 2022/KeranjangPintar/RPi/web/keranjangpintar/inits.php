<?php
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
  
  function checkoutCart($conn, $idKeranjang, $idProduk, $idUser, $jumlah) {
    $sql = "INSERT INTO
              `keranjang_history` (`id`, `id_keranjang`, `id_produk`, `id_user`, `jumlah`, `time_stamp`)
            VALUES
              (NULL, '" . $idKeranjang . "', '" . $idProduk . "', '" . $idUser . "', '" . $jumlah . "', current_timestamp())";
    
    return ($conn -> query( $sql ) === TRUE);
  }
  
  function deleteCart($conn, $idPos) {
    $sql = "DELETE FROM `keranjang_pos` WHERE `keranjang_pos`.`id` = '".$idPos."'";
    return ($conn -> query( $sql ) === TRUE);
  }
?>