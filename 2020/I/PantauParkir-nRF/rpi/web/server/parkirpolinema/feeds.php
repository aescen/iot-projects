<div class="w3-row-padding" style="margin:0 -16px">
	<!-- PUT TABLE HERE -->
	<!-- PHP.MySQL.START -->
	<?php
	$servername = "localhost";
	$username = "pi";
	$password = "raspberry";
	$dbname = "pi";

	// Create connection
	$conn = new mysqli($servername, $username, $password, $dbname);
	// Check connection
	if ( $conn->connect_error ) {
		die("Connection failed: " . $conn->connect_error);
	} 

	$sql = "SELECT * FROM `parkirpolinema`";
	$result = $conn->query($sql);

	if ( $result->num_rows > 0 ) {
		echo "<table class='w3-table-all w3-white w3-centered'>
			<tr><th>ID Node</th>
				<th>Jumlah Kendaraan</th>
				<th>Status</th>
				<th>Waktu</th></tr>";
		// output data of each row
		while( $row = $result->fetch_assoc() ) {
			echo "<tr'><td>".$row["nodeId"]."</td><td>".$row["jumlahKendaraan"]."</td>
			<td>".$row["parkirStatus"]."</td><td>".$row["timeStamp"]."</td></tr>";
			}
		echo "</table>";
	} else {
		echo "0 results";
	}
	$conn->close();
	?>
	<!-- PHP.MySQL.END --> 
</div>