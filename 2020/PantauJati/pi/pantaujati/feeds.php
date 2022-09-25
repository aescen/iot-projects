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

	$sql = "SELECT * FROM `pantauJati`";
	$result = $conn->query($sql);

	if ( $result->num_rows > 0 ) {
		echo "<table class='w3-table w3-striped w3-white w3-centered'>
			<tr><td>ID Node</td>
				<td>Kelembapan (%)</td>
				<td>Status</td>
				<td>Ketinggian (cm)</td>
				<td>Waktu</td></tr>";
		// output data of each row
		while( $row = $result->fetch_assoc() ) {
			echo "<tr'><td>".$row["nodeId"]."</td><td>".$row["soilMoist"]."</td>
				   <td>".$row["soilStatus"]."</td><td>".$row["ketinggian"]."</td>
				   <td>".$row["timeStamp"]."</td></tr>";
			}
		echo "</table>";
	} else {
		echo "0 results";
	}
	$conn->close();
	?>
	<!-- PHP.MySQL.END --> 
</div>