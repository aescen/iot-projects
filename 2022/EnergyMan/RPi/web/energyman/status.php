<?php 
	require_once 'db.php';
	
	$sql = "SELECT * FROM `energyman`";
	$result = $conn->query($sql);
	$red = 'grey';
	$green = 'grey';
	$blue = 'grey';
  $strCharges = array('Charging', 'Full');
  $colorCharges = array('yellow', 'green');
  $strChargeStatus = array('Normal', 'Overcharged');
  $colorChargeStatus = array('green', 'red');
  $strRelays = array('Open', 'Close');
  $colorRelays = array('red', 'green');
	
	if ( $result->num_rows > 0 ) {
		echo "<div class='w3-cell-row w3-center'>";
		while( $row = $result->fetch_assoc() ) {
      $statusBatt = $row['battery'];
      $statusCharge = $row['charge'];
      $statusRelay1 = $row['relay_1'];
      $statusRelay2 = $row['relay_2'];
			echo "<div class='w3-container w3-cell w3-cell-middle w3-mobile'>
					<div class='w3-card-4 w3-white'>
						<div class='w3-large w3-block w3-indigo'>
							<div class='w3-padding'><strong>" . $row['name'] . "</span></strong></div>
						</div>

            <table class='w3-table w3-centered'><tr><td>
              <img src='static/images/fan.png' alt='fan' width='256px' height='256px'>
            </td></tr></table>

						<div class='w3-large w3-block w3-indigo'>
              <table class='w3-table'>
                <tr>
                <td rowspan=5 style='vertical-align:middle; text-align:center; padding: 8px; margin: 0;'>
                  <img src='static/images/grey.png' alt='status' width='56px' height='56px' class='w3-circle'>
                </td>
                </tr>
                
                <tr>
                <td style='background-color:white; color:black;'>
                  <strong>Battery: " . $strCharges[$statusBatt] . "</strong></td>
                <td style='vertical-align:bottom; text-align:center; background-color:" . $colorCharges[$statusBatt] . ";'>
                  <img src='static/images/grey.png' alt='status' width='32px' height='32px' class='w3-circle'>
                </td>
                </tr>
                
                <tr>
                <td style='background-color:white; color:black;'>
                  <strong>Status: " . $strChargeStatus[$statusCharge] . "</strong></td>
                <td style='vertical-align:bottom; text-align:center; background-color:" . $colorChargeStatus[$statusCharge] . ";'>
                  <img src='static/images/grey.png' alt='status' width='32px' height='32px' class='w3-circle'>
                </td>
                </tr>
                
                <tr>
                <td style='background-color:white; color:black;'>
                  <strong>Solar Panel Relay: " . $strRelays[$statusRelay1] . "</strong></td>
                <td style='vertical-align:bottom; text-align:center; background-color:" . $colorRelays[$statusRelay1] . ";'>
                  <img src='static/images/grey.png' alt='status' width='32px' height='32px' class='w3-circle'>
                </td>
                </tr>
                
                <tr>
                <td style='background-color:white; color:black;'>
                  <strong>Wind Turbine Relay: " . $strRelays[$statusRelay2] . "</strong></td>
                <td style='vertical-align:bottom; text-align:center; background-color:" . $colorRelays[$statusRelay2] . ";'>
                  <img src='static/images/grey.png' alt='status' width='32px' height='32px' class='w3-circle'>
                </td>
                </tr>
              </table>
						</div>
					</div>
				</div>";
		}
		echo "</div>";
    
    echo "<div class='w3-cell-row w3-center w3-responsive' style='margin-top:32px;'>
    <table class='w3-table w3-white w3-centered'>
			<thead>
        <tr class='w3-indigo'>
          <th>ID</th>
          <th>Arus 1 (mA)</th>
          <th>Arus 2 (mA)</th>
          <th>Voltage (v)</th>
          <th>Location</th>
          <th>Timestamp</th>
        </tr>
      </thead>";
		// output data of each row
    $result = $conn->query($sql);
		while( $row = $result->fetch_assoc() ) {
			echo "<tr'>
           <td>".$row["id"]."</td>
           <td>".$row["current_1"]."</td>
           <td>".$row["current_2"]."</td>
				   <td>".$row["voltage"]."</td>
           <td>".$row["location"]."</td>
				   <td>".$row["time_stamp"]."</td></tr>";
			}
		echo "</table></div>";
	}

?>