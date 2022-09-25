<!-- PHP.MySQL.START -->
<?php
  require_once 'inits.php';
  
  $objectStatus = 0;
  $valTurbidty = 0.0;

  $sql = "SELECT * FROM `pantausungai` WHERE `id` = '0'";
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
						$valStatus = strval($row['objectStatus']);
                        if ( $row['sensorType'] == $strTurbidity ){
                            //$valTurbidty = $row['sensorVal'];
                            $valTurbidty = rand(4000, 6000) / 100;
                        } else {
                            $valTurbidty = -0.101; /* sensor type unavailable */
                        }
					}
				}
			?>
			<div class="w3-cell">
				<div class='w3-padding-16 w3-margin-left'><strong>Status :  <?php echo $arrStrStatus[$valStatus]; ?></strong></div>
			</div>
			<div class="w3-cell">
				<div class='w3-padding-16 w3-margin-right w3-right-align'><strong>Kekeruhan:  <?php echo $valTurbidty . "%"; ?></strong></div>
			</div>
		</div>
	</div>
</div>
