<!-- PHP.MySQL.START -->
<?php
	require_once 'inits.php';
	require_once 'db.php';
	
	$info = 'LOW';
	$status = 'No object';
	$totalVisitor = '0';
	$statusColor = 'w3-dark-grey';

	$sql = "SELECT * FROM `palangcov` WHERE `id` = '1'";
	$result = $conn->query($sql);
?>
<!-- PHP.MySQL.END --> 

<div class='w3-card-4 w3-white'>
<div class='w3-large w3-block w3-dark-grey'>
	<div class='w3-padding'><strong>Face Detection<span></span></strong></div>
</div>
	<div class='w3-cell-row'>
	<div class='w3-container w3-cell w3-cell-middle w3-mobile'>
	<img src='<?php echo $IMAGE_SRC; ?>' alt='Kubis baik' width='224px' height='224px' class='w3-left w3-circle w3-padding'>
	<span class='w3-left'>
			<table class='w3-table'>
			<!-- PHP.MySQL.START -->
			<?php
				if ( $result->num_rows > 0 ) {
					if( $row = $result->fetch_assoc() ) {
						if ( floatval($row["objTemp"]) < OBJECT_MIN ){
							$info = 'LOW';
							$status = 'No object';
							$statusColor = 'w3-dark-grey';
						} else if ( floatval($row["objTemp"]) >= OBJECT_MIN && floatval($row["objTemp"]) <= OBJECT_MAX ){
							$info = 'OK';
							$status = 'Normal';
							$statusColor = 'w3-green';
						} else if ( floatval($row["objTemp"]) > OBJECT_MAX ){
							$info = 'HIGH';
							$status = 'Abnormal !';
							$statusColor = 'w3-red';
						}
						
						echo "<tr>
							<th>Object Temperature</th>
							<th>:</th>
							<td>" . $row["objTemp"] . "&#176;C</td>
							</tr>
							<tr>
							<th>Ambient Temperature</th>
							<th>:</th>
							<td>" . $row["ambTemp"] ."&#176;C</td>
							</tr>
							<tr>
							<th>Humidity</th>
							<th>:</th>
							<td>" . $row["humidDHT"] . "%</td>
							</tr>
							<tr>
							<th>Room Temperature</th>
							<th>:</th>
							<td>" . $row["tempDHT"] . "&#176;C</td>
							</tr>
							<tr>
							<th>Information</th>
							<th>:</th>
							<td>" . $info . "</td>
							</tr>";
						
						$totalVisitor = $row["totalVisitor"];
					}
				} else {
					echo "0 results";
				}
			?>
			<!-- PHP.MySQL.END --> 
			</table>
		</span>
	</div>
</div>
	<div class='w3-large w3-block <?php echo $statusColor; ?>'>
		<div class="w3-cell-row">
			<div class="w3-cell">
				<div class='w3-padding-16 w3-margin-left'><strong>Status :  <?php echo $status; ?></strong></div>
			</div>
			<div class="w3-cell">
				<div class='w3-padding-16 w3-margin-right w3-right-align'><strong>Total Visitor:  <?php echo $totalVisitor; ?></strong></div>
			</div>
		</div>
	</div>
</div>