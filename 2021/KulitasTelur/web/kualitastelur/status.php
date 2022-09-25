<?php 
	require_once 'db.php';
	
	$sql = "SELECT * FROM `kualitastelur`";
	$result = $conn->query($sql);
	
	if ( $result->num_rows > 0 ) {
		echo "<div class='w3-cell-row w3-center'>";
		while( $row = $result->fetch_assoc() ) {
			echo "<div class='w3-container w3-cell w3-cell-middle w3-mobile'>
					<div class='w3-card-4 w3-white'>
						<div class='w3-large w3-block w3-dark-grey'>
							<div class='w3-padding'><strong>Telur " . ucwords($row['tipeTelur']) . "</span></strong></div>
						</div>

						<div class='w3-container w3-cell w3-cell-middle w3-mobile'>
							<img src='static/images/" . $row['tipeTelur'] . ".png' alt='" . $row['tipeTelur'] . "' width='300px' height='300px' class='w3-circle'>
						</div>

						<div class='w3-large w3-block w3-dark-grey'>
							<div class='w3-padding'>
								<table class='w3-table'>
								  <tr>
									<th class='w3-left'>Berat</th>
									<th class='w3-left'>:</th>
									<td class='w3-right'>" . $row['beban'] . "</td>
								  </tr>
								  <tr>
									<th class='w3-left'>Total</th>
									<th class='w3-left'>:</th>
									<td class='w3-right'>" . $row['jumlah'] . "</td>
								  </tr>
								</table>
							</div>
						</div>
					</div>
				</div>";
		}
		echo "</div>";
	} else {
		include 'status-template.php';
	}

?>