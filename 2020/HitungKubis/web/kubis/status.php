<?php
require_once 'db.php';

$sql = "SELECT * FROM `kubis`";
$result = $conn->query($sql);

if ( $result->num_rows > 0 ) {
	// output data of each row
	$total = 0;
	$body = '';
	$batch = '';
	while( $row = $result->fetch_assoc() ) {
		$img = "";
		$batch = $row["kloter"];
		if ($row["kualitas"] == "Baik"){
			$img = "<img src='static/images/kubis-baik.png' alt='Kubis baik' width='224px' height='224px' class='w3-left w3-circle'>";
		}else{
			$img = "<img src='static/images/kubis-buruk.png' alt='Kubis buruk' width='224px' height='224px' class='w3-left w3-circle'>";
		}
		$body = $body."	<div class='w3-container w3-cell w3-cell-middle w3-mobile'>
					".$img."
					<span class='w3-left'>
						<table class='w3-table'>
						  <tr>
							<th>Warna</th>
							<th>:</th>
							<td>".$row["warna"]."</td>
						  </tr>
						  <tr>
							<th>Kulitas</th>
							<th>:</th>
							<td>".$row["kualitas"]."</td>
						  </tr>
						  <tr>
							<th>Jumlah</th>
							<th>:</th>
							<td>".$row["jumlah"]."</td>
						  </tr>
						  <tr>
							<th>Red</th>
							<th>:</th>
							<td>".$row["r"]."</td>
						  </tr>
						  <tr>
							<th>Green</th>
							<th>:</th>
							<td>".$row["g"]."</td>
						  </tr>
						  <tr>
							<th>Blue</th>
							<th>:</th>
							<td>".$row["b"]."</td>
						  </tr>
						</table>
					</span>
				</div>";
		$total += (int)$row["jumlah"];
	}
	$header = "<div class='w3-card-4 w3-white'>";
	$header = $header."<div class='w3-large w3-block w3-dark-grey'>
			<div class='w3-padding'><strong>Kloter: <span>".$batch."</span></strong></div>
		</div>";
	$header =	$header."<div class='w3-cell-row'>";
	$body = $body."</div>
			<div class='w3-large w3-block w3-dark-grey'><div class='w3-padding-16 w3-margin-left'><strong>Total kubis : ".$total."</strong></div></div>
		</div>";
	echo $header.$body;
} else {
	echo "0 results";
}

$conn->close();
?>