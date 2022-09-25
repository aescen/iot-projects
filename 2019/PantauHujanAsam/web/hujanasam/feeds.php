<div class="w3-row-padding" style="margin:0 -16px">
	<!-- PUT TABLE HERE -->
	<!-- PHP.MySQL.START -->
	<?php
	$servername = "localhost";
	$username = "root";
	$password = "";
	$dbname = "hujanasam";

	// Create connection
	$conn = new mysqli($servername, $username, $password, $dbname);
	// Check connection
	if ( $conn->connect_error ) {
		die("Connection failed: " . $conn->connect_error);
	} 

	$sql = "SELECT * FROM `prediksi`";
	$result = $conn->query($sql);

	if ( $result->num_rows > 0 ) {
		echo "<table class='w3-table w3-responsive w3-card w3-bordered w3-white w3-centered'>
			<tr><td><strong>Nilai PH</strong></td>
				<td><strong>Nilai CO2</strong></td>
				<td><strong>Hasil Prediksi GNB</strong></td>
				<td><strong>Nilai Probabilistik GNB PH</strong></td>
				<td><strong>Nilai Probabilistik GNB CO2</strong></td>
				<td><strong>Nilai Akurasi</strong></td></tr>";
		// output data of each row
		while( $row = $result->fetch_assoc() ) {
			echo "<tr'><td>".$row["ph"]."</td><td>".$row["co2"]."</td>
				   <td>".$row["hasilprediksiGNB"]."</td>
				   <td>".$row["nilaiprobabilistikGNBPH"]."</td>
				   <td>".$row["nilaiprobabilistikGNBCO2"]."</td>
				   <td>".$row["nilaiakurasi"]." %</td></tr>";
			}
		echo "</table>";
	} else {
		echo "0 results";
	}
	$conn->close();
	?>
	<!-- PHP.MySQL.END --> 
</div>