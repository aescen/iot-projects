<div class="w3-row-padding" style="margin:0 -16px">
	<!-- PUT TABLE HERE -->
	<!-- PHP.MySQL.START -->
	<?php
	$servername = "localhost";
	$username = "pi";
	$password = "raspberry";
	$dbname = "pi";
	define("MAX_CAP", 40);

	// Create connection
	$conn = new mysqli($servername, $username, $password, $dbname);
	// Check connection
	if ( $conn->connect_error ) {
		die("Connection failed: " . $conn->connect_error);
	} 

	$sql = "SELECT * FROM `parkirpolinema_node`";
	$result = $conn->query($sql);

	if ( $result->num_rows > 0 ) {
		// output data of each row
		if( $row = $result->fetch_assoc() ) {
			if(intval($row['jumlahKendaraan']) >= 0 && intval($row['jumlahKendaraan']) <= MAX_CAP){
				echo "<h1 class='w3-xxxlarge w3-center w3-text-black'>JUMLAH SLOT KENDARAAN</h1>
					<b><h1 class='w3-jumbo w3-center w3-wide w3-text-black' style='text-shadow:2px 2px 0 #444'>".(MAX_CAP - intval($row['jumlahKendaraan']))."</h1></b>
					<hr class='w3-border-black' style='margin:auto;width:75%'>
					<h1 class='w3-xxxlarge w3-center w3-text-black'>Status</h1>
					<b><h1 class='w3-jumbo w3-center w3-text-black' style='text-shadow:2px 2px 0 #444'>".strtoupper($row['parkirStatus'])."</h1></b>";
			}
		}
	} else {
		echo "<h1 class='w3-xxxlarge w3-center w3-text-black' style='text-shadow:2px 2px 0 #444'>JUMLAH SLOT KENDARAAN</h1>
			<b><h1 class='w3-jumbo w3-center w3-wide w3-text-black' style='text-shadow:3px 3px 0 #444'>null</h1></b>
			<hr class='w3-border-black' style='margin:auto;width:75%'>
			<h1 class='w3-xxxlarge w3-center w3-text-black' style='text-shadow:2px 2px 0 #444'>Status</h1>
			<b><h1 class='w3-jumbo w3-center w3-text-black' style='text-shadow:2px 2px 0 #444'>null</h1></b>";
	}
	$conn->close();
	?>
	<!-- PHP.MySQL.END --> 
</div>