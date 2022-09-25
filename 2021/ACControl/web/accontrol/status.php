<!-- PHP.MySQL.START -->
<?php
	require_once 'inits.php';
	require_once 'db.php';
	
	$objectCount = 'No object';
	$roomTemp = 20;
	$humid = 62.0;
	$acTemp = 18;
	$totalVisitor = 0;

	$sql = "SELECT * FROM `accontrol` WHERE `id` = '1'";
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
						$objectCount = $row['objectCount'];
						$roomTemp = $row['roomTemp'];
						$humid = $row['humidity'];
						$acTemp = $row['acTemp'];
						$totalVisitor = $row['totalVisitor'];
					}
				}
			?>
			<div class="w3-cell">
				<div class='w3-padding-16 w3-margin-left'><strong>Status :  <?php echo $objectCount . (($objectCount > 1) ? " objects":" object"); ?></strong></div>
			</div>
			<div class="w3-cell">
				<div class='w3-padding-16 w3-margin-left'><strong>Room :  <?php echo $roomTemp; ?> &#176;C</strong></div>
			</div>
			<div class="w3-cell">
				<div class='w3-padding-16 w3-margin-left'><strong>Humidity :  <?php echo $humid; ?> %</strong></div>
			</div>
			<div class="w3-cell">
				<div class='w3-padding-16 w3-margin-left'><strong>AC :  <?php echo $acTemp; ?> &#176;C</strong></div>
			</div>
			<div class="w3-cell">
				<div class='w3-padding-16 w3-margin-right w3-right-align'><strong>Total Visitor:  <?php echo $totalVisitor; ?></strong></div>
			</div>
		</div>
	</div>
</div>
