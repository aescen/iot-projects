<div class="w3-row-padding" style="margin:0 -16px">
	<!-- PUT TABLE HERE -->
	<!-- PHP.MySQL.START -->
	<?php
	require_once 'db.php';
	
	$sql = "SELECT t1.ids, t1.plateNumbers Plat, t1.comeIn Masuk, t1.comeOut Keluar FROM platenumbershistory t1 JOIN (SELECT MAX(ids) ids, plateNumbers FROM platenumbershistory GROUP BY plateNumbers) t2 ON t1.ids = t2.ids AND t1.plateNumbers = t2.plateNumbers ORDER BY `t1`.`ids` DESC;";
	$result = $conn->query($sql);

	if ( $result->num_rows > 0 ) {
		echo "<table class='w3-table w3-card w3-bordered w3-striped w3-white w3-centered'>
			<tr class='w3-teal'><th><strong>No</strong></th>
				<th><strong>Plat</strong></th>
				<th><strong>Masuk</strong></th>
				<th><strong>Keluar</strong></th>
			</tr>";
		// output data of each row
		$cnt = 1;
		while( $row = $result->fetch_assoc() ) {
			if ($row['Keluar'] == NULL){
				$row["Keluar"] = "-";
			} else {
				$row["Keluar"] = date('H:m:s', strtotime($row["Keluar"]));
			}
			echo "<tr'>
			       <td>".$cnt."</td>
				   <td>".$row["Plat"]."</td>
				   <td>".date('H:m:s', strtotime($row["Masuk"]))."</td>
				   <td>".$row["Keluar"]."</td>
				  </tr>";
			$cnt++;
		}
		echo "</table>";
	} else {
		echo "<center><h2>Kosong</h2></center>";
	}
	$conn->close();
	?>
	<!-- PHP.MySQL.END --> 
</div>