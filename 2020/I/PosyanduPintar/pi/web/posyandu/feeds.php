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

	$sql = "SELECT * FROM `posyandu`";
	$result = $conn->query($sql);

	if ( $result->num_rows > 0 ) {
		echo "<table class='w3-table w3-striped w3-white w3-centered'>
			<tr>
				<th>Nama</td>
				<th>Tinggi Badan</th>
				<th>Berat Badan</th>
				<th>Tensi Darah</th>
				<th>Suhu Badan</th>
			</tr>";
		// output data of each row
		while( $row = $result->fetch_assoc() ) {
			echo "<tr'>
				   <td>".$row["nama"]."</td>
				   <td>".$row["tb"]."</td>
				   <td>".$row["bb"]."</td>
				   <td>".$row["td"]."</td>
				   <td>".$row["sb"]."</td>
				  </tr>";
			}
		echo "</table>";
	} else {
		echo "0 results";
	}
	$conn->close();
	?>
	<!-- PHP.MySQL.END --> 
</div>