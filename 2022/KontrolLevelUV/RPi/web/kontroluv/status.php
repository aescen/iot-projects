<!-- PHP.MySQL.START -->
<?php
	require_once 'inits.php';
	require_once 'db.php';
	
	$temp = 0;
	$humid = 0;
	$powerUsage = 0;
	$totalVisitor = 0;

	$sql = "SELECT * FROM `kontroluv` WHERE `id` = '0'";
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
						$temp = $row['temp'];
						$humid = $row['humid'];
						$powerUsage = $row['power_usage'];
						$totalVisitor = $row['total_visitor'];
					}
				}
			?>
			<div class="w3-cell">
				<div class='w3-padding-16 w3-margin-left w3-margin-right'><strong>Suhu :  <?php echo $temp; ?>&#176;C</strong></div>
			</div>
			<div class="w3-cell">
				<div class='w3-padding-16 w3-margin-left w3-margin-right'><strong>Kelembapan :  <?php echo $humid; ?>%</strong></div>
			</div>
      <div class="w3-cell">
				<div class='w3-padding-16 w3-margin-left w3-margin-right w3-right-align'><strong>Jumlah Orang:  <?php echo $totalVisitor; ?></strong></div>
			</div>
			<div class="w3-cell">
				<div class='w3-padding-16 w3-margin-left w3-margin-right w3-right-align'><strong>Daya :  <?php echo $powerUsage; ?>w</strong></div>
			</div>
		</div>
	</div>
</div>
