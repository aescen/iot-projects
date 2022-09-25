<div class="w3-row">
	<?php
		include("config.php");
		
		$sql = "SELECT Nama, Nilai FROM `Status` WHERE `Status`.`Nama` = 'm1'";
		$result = $conn->query($sql);
		if ($result->num_rows > 0) {
			$row = $result->fetch_assoc();
			$m1 = $row['Nilai'];
			if($m1 >= 200){
				$btn = 'button-red';
			}else{
				$btn = 'button-green';
			}
			echo "<button class='button button4 ".$btn."'><strong>SENSOR 1</strong></button>";
		}

		$sql2 = "SELECT Nama, Nilai FROM `Status` WHERE `Status`.`Nama` = 'm2'";
		$result2 = $conn->query($sql2);
		if ($result2->num_rows > 0) {
			$row2 = $result2->fetch_assoc();
			$m2 = $row2['Nilai'];
			if($m2 >= 200){
				$btn = 'button-red';
			}else{
				$btn = 'button-green';
			}
			echo "<button class='button button4 ".$btn."'><strong>SENSOR 2</strong></button>";
		}

		$sql3 = "SELECT Nama, Nilai FROM `Status` WHERE `Status`.`Nama` = 'm3'";
		$result3 = $conn->query($sql3);
		if ($result2->num_rows > 0) {
			$row3 = $result3->fetch_assoc();
			$m3 = $row3['Nilai'];
			if($m3 >= 50){
				$btn = 'button-red';
			}else{
				$btn = 'button-green';
			}
			echo "<button class='button button4 ".$btn."'><strong>SENSOR 3</strong></button>";
		}

		$sql4 = "SELECT Nama, Nilai FROM `Status` WHERE `Status`.`Nama` = 'm4'";
		$result4 = $conn->query($sql4);
		if ($result4->num_rows > 0) {
			$row4 = $result4->fetch_assoc();
			$m4 = $row4['Nilai'];
			if($m4 >= 50){
				$btn = 'button-red';
			}else{
				$btn = 'button-green';
			}
			echo "<button class='button button4 ".$btn."'><strong>SENSOR 4</strong></button>";
		}
	?>
</div>