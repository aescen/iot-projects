<!-- PHP.MySQL.START -->
<?php
	require_once 'inits.php';
	require_once 'db.php';
	
	$sql = "SELECT * FROM `zonabuta` WHERE `id` = '0'";
	$result = $conn->query($sql);
?>
<!-- PHP.MySQL.END --> 

<div class='w3-card-4 w3-white'>
<div class='w3-large w3-block w3-blue-grey'>
	<div class='w3-padding'><strong>Video Camera<span></span></strong></div>
</div>
	<div class='w3-cell-row'>
		<div class='w3-container w3-cell w3-cell-middle w3-center w3-mobile'>
			<img src='<?php echo $IMAGE_SRC; ?>' alt='videofeed' width='480px' height='360px' class='w3-center w3-middle w3-padding'>
		</div>
	</div>
	<div class='w3-large w3-block w3-blue-grey'>
		<div class="w3-cell-row">
			<?php
				if ( $result->num_rows > 0 ){
					if( $row = $result->fetch_assoc() ){
						$objectCount = (intval($row['objectCount']) == 0) ? 'No object' : $row['objectCount'];
                        $objectType = json_decode($row['objectType'], true);
						$totalDeteksi = $row['totalDetection'];
					}
				}
			?>
			<div class="w3-cell">
				<div class='w3-padding-16 w3-margin-left'><strong>Deteksi :  <?php echo $objectCount; ?></strong></div>
			</div>
			<div class="w3-cell">
				<div class='w3-padding-16 w3-margin-left'><strong>Mobil :  <?php echo $objectType['mobil']; ?></strong></div>
			</div>
			<div class="w3-cell">
				<div class='w3-padding-16 w3-margin-left'><strong>Sepeda Motor :  <?php echo $objectType['sepeda_motor']; ?></strong></div>
			</div>
			<div class="w3-cell">
				<div class='w3-padding-16 w3-margin-left'><strong>Orang :  <?php echo $objectType['orang']; ?></strong></div>
			</div>
			<div class="w3-cell">
				<div class='w3-padding-16 w3-margin-right w3-right-align'><strong>Total Deteksi:  <?php echo $totalDeteksi; ?></strong></div>
			</div>
		</div>
	</div>
</div>
