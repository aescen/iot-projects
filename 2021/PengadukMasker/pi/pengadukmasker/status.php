<?php 
	require_once 'db.php';
	
	$sql = "SELECT * FROM `pengadukmasker`";
	$result = $conn->query($sql);
	$red = 'grey';
	$green = 'grey';
	$blue = 'grey';
	$strRed = '<br><span>Proses</span>';
	$strGreen = '<br><span>Luang</span>';
	$strBlue = '<br><span>Penuh</span>';
	
	if ( $result->num_rows > 0 ) {
		echo "<div class='w3-cell-row w3-center'>";
		while( $row = $result->fetch_assoc() ) {
			if ($row['status'] == '1'){
				$red = 'red';
				$green = 'grey';
				$blue = 'grey';
				$strRed = '<br><strong><span>Proses</span></strong>';
				$strGreen = '<br><span>Luang</span>';
				$strBlue = '<br><span>Penuh</span>';
			} else if ($row['status'] == '2'){
				$red = 'grey';
				$green = 'green';
				$blue = 'grey';
				$strRed = '<br><span>Proses</span>';
				$strGreen = '<br><strong><span>Luang</span></strong>';
				$strBlue = '<br><span>Penuh</span>';
			} else if ($row['status'] == '3'){
				$red = 'grey';
				$green = 'grey';
				$blue = 'blue';
				$strRed = '<br><span>Proses</span>';
				$strGreen = '<br><span>Luang</span>';
				$strBlue = '<br><strong><span>Penuh</span></strong>';
			}
			echo "<div class='w3-container w3-cell w3-cell-middle w3-mobile'>
					<div class='w3-card-4 w3-white'>
						<div class='w3-large w3-block w3-grey'>
							<div class='w3-padding'><strong>" . $row['nama'] . "</span></strong></div>
						</div>

						<div class='w3-container w3-cell w3-cell-middle w3-mobile'>
							<img src='static/images/mixer.png' alt='mixer' width='300px' height='300px'>
						</div>

						<div class='w3-large w3-block w3-grey'>
							<div class='w3-padding'>
								<table class='w3-table'>
								  <tr>
									<td class='w3-middle w3-center'>
										<img src='static/images/" . $red . ".png' alt='status' width='84px' height='84px' class='w3-circle'>
										" . $strRed . "
									</td>
									<td class='w3-middle w3-center'>
										<img src='static/images/" . $green . ".png' alt='status' width='84px' height='84px' class='w3-circle'>
										" . $strGreen . "
									</td>
									<td class='w3-middle w3-center'>
										<img src='static/images/" . $blue . ".png' alt='status' width='84px' height='84px' class='w3-circle'>
										" . $strBlue . "
									</td>
								  </tr>
								</table>
								<table class='w3-table'>
								  <tr>
									<th class='w3-left'>Total</th>
									<th class='w3-left'>:</th>
									<td class='w3-right'>" . $row['total'] . "</td>
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