<!-- Header -->
<header class="w3-container" style="padding-top:22px">
	<div class="w3-container w3-card w3-green">
		<h2>Status Node</h2>
	</div>
</header>

<!-- Feeds panel -->
<div class="w3-container" style="margin-left:8px;margin-right:8px;margin-top:20px;">
	<div class="w3-row-padding" style="margin:0 -16px">
		<!-- PUT TABLE HERE -->
		<!-- PHP.MySQL.START -->
		<?php
		require_once 'db.php';

		$sql = "SELECT * FROM `nrf24lampu`";
		$result = $conn->query($sql);

		if ( $result->num_rows > 0 ) {
			echo "<table class='w3-table-all w3-centered w3-card-4 w3-white'>
				<tr class='w3-green'><th>Id</th>
					<th>Voltage (V)</th>
					<th>Current (I)</th>
					<th>Timestamp</th></tr>";
			// output data of each row
			while( $row = $result->fetch_assoc() ) {
				echo "<tr><td>".hexdec($row["id"])."</td>
					   <td>".$row["dcVoltage"]."</td>
					   <td>".$row["dcCurrent"]."</td>
					   <td>".$row["timeStamp"]."</td></tr>";
				}
			echo "</table>";
		} else {
			echo "0 results";
		}
		?>
		<!-- PHP.MySQL.END --> 
	</div>
</div>
<hr>
		  
<!-- Header -->
<header class="w3-container" style="padding-top:22px">
	<div class="w3-container w3-card w3-green">
		<h2>Status PJU</h2>
	</div>
</header>

<!-- Feeds panel -->
<div class="w3-container" style="margin-left:8px;margin-right:8px;margin-top:20px;">
	<div class="w3-row-padding" style="margin:0 -16px">
		<!-- PUT TABLE HERE -->
		<!-- PHP.MySQL.START -->
		<?php
		require_once 'db.php';

		$sql = "SELECT * FROM `nrf24lampu`";
		$result = $conn->query($sql);

		if ( $result->num_rows > 0 ) {
			echo "<table class='w3-table-all w3-centered w3-card-4 w3-white'>
				<tr class='w3-green'><th>Id</th>
					<th>Voltage (V)</th>
                    <th>Current (I)</th>
					<th>Timestamp</th></tr>";
			// output data of each row
			while( $row = $result->fetch_assoc() ) {
				echo "<tr><td>".hexdec($row["id"])."</td>
					   <td>".$row["acVoltage"]."</td>
                       <td>".$row["acCurrent"]."</td>
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
</div>
<hr>