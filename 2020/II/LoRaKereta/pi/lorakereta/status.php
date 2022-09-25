<?php
require_once 'db.php';

$sql = "SELECT * FROM `loratrain`";
$result = $conn->query($sql);

if ( $result->num_rows > 0 ) {
	// output data of each row
	$total = 0;
	$body = '';
	while( $row = $result->fetch_assoc() ) {
		$imgDirectionLamp1 = "";
		$imgStopGoLamp1 = "";
		$imgDirectionLamp2 = "";
		$imgStopGoLamp2 = "";
		if ($row["directionlamp"] == "FromRight"){
			$imgDirectionLamp1 = "<img src='static/images/leftarrow-grey.png' alt='Direction Lamp 1' width='164px' height='164px' class='w3-image w3-circle'>";
			$imgDirectionLamp2 = "<img src='static/images/rightarrow.png' alt='Direction Lamp 2' width='164px' height='164px' class='w3-image w3-circle'>";
		}else if ($row["directionlamp"] == "FromLeft"){
			$imgDirectionLamp1 = "<img src='static/images/leftarrow.png' alt='Direction Lamp 1' width='164px' height='164px' class='w3-image w3-circle'>";
			$imgDirectionLamp2 = "<img src='static/images/rightarrow-grey.png' alt='Direction Lamp 2' width='164px' height='164px' class='w3-image w3-circle'>";
		}else{
			$imgDirectionLamp1 = "<img src='static/images/leftarrow-grey.png' alt='Direction Lamp 1' width='164px' height='164px' class='w3-image w3-circle'>";
			$imgDirectionLamp2 = "<img src='static/images/rightarrow-grey.png' alt='Direction Lamp 2' width='164px' height='164px' class='w3-image w3-circle'>";
		}
		if ($row["stopgolamp"] == "Stop"){
			$imgStopGoLamp1 = "<img src='static/images/StopGo.png' alt='StopGo Lamp 1' width='164px' height='164px' class='w3-image w3-circle'>";
			$imgStopGoLamp2 = "<img src='static/images/Stop.png' alt='StopGo Lamp 2' width='164px' height='164px' class='w3-image w3-circle'>";
		}else if ($row["stopgolamp"] == "Go"){
			$imgStopGoLamp1 = "<img src='static/images/Go.png' alt='StopGo Lamp 1' width='164px' height='164px' class='w3-image w3-circle'>";
			$imgStopGoLamp2 = "<img src='static/images/StopGo.png' alt='StopGo Lamp 2' width='164px' height='164px' class='w3-image w3-circle'>";
		}else{
			$imgStopGoLamp1 = "<img src='static/images/StopGo.png' alt='StopGo Lamp 1' width='164px' height='164px' class='w3-image w3-circle'>";
			$imgStopGoLamp2 = "<img src='static/images/StopGo.png' alt='StopGo Lamp 2' width='164px' height='164px' class='w3-image w3-circle'>";
		}
		$body = $body."	<div class='w3-container w3-cell w3-cell-middle w3-center w3-mobile'>
					".$imgDirectionLamp1."</div>";
		$body = $body."	<div class='w3-container w3-cell w3-cell-middle w3-center w3-mobile'>
					".$imgDirectionLamp2."</div>";
		$body = $body."	<div class='w3-container w3-cell w3-cell-middle w3-center w3-mobile'>
					".$imgStopGoLamp1."</div>";
					$body = $body."	<div class='w3-container w3-cell w3-cell-middle w3-center w3-mobile'>
					".$imgStopGoLamp2."</div>";
		$total += (int)$row["traincount"];
	}
	$header = "<div class='w3-card-4 w3-white'>";
	$header = $header."<div class='w3-large w3-block w3-dark-grey'>
			<div class='w3-padding'><strong>Lampu kereta<span></span></strong></div>
		</div>";
	$header =	$header."<div class='w3-cell-row'>";
	$body = $body."</div>
			<div class='w3-large w3-block w3-dark-grey'><div class='w3-padding-16 w3-margin-left'><strong></strong></div></div>
		</div>";
	echo $header.$body;
} else {
	echo "0 results";
}

$conn->close();
?>