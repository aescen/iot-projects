<div class="w3-row-padding" style="margin:0 -16px">
      <div>
        <!-- PUT TABLE HERE -->
		<!-- PHP.MySQL.START -->
		<?php
		include('config.php');

		$sql = "SELECT id, namaAlat, noSeri, noSeriBaca, statusAlat FROM `lokerStatus`";
		$result = $conn->query($sql);

		if ($result->num_rows > 0) {
			echo "<table class='w3-table w3-striped w3-white w3-centered'><tr><th>No</th><th>Alat</th><th>Serial</th><th>Serial Terbaca</th><th>Status</th><th></th></tr>";
			// output data of each row
			while($row = $result->fetch_assoc()) {
				if ($row["statusAlat"] == 0){
					echo "<tr><td>".$row["id"]."</td><td>".$row["namaAlat"]."</td><td>".$row["noSeri"]."</td><td>".$row["noSeriBaca"]."</td><td>Ada</td><td><i type='button' class='fa fa-check w3-large w3-green w3-hover-lime' onclick='history.go(0)'></i></td></tr>";
				}
				else if($row["statusAlat"] == 1){
					echo "<tr><td>".$row["id"]."</td><td>".$row["namaAlat"]."</td><td>".$row["noSeri"]."</td><td>".$row["noSeriBaca"]."</td><td>Kosong</td><td><i type='button' class='fa fa-check w3-large w3-indigo w3-hover-light-blue' onclick='history.go(0)'></i></td></tr>";
				}
				else if($row["statusAlat"] == 2){
					echo "<tr><td>".$row["id"]."</td><td>".$row["namaAlat"]."</td><td>".$row["noSeri"]."</td><td>".$row["noSeriBaca"]."</td><td>Salah</td><td><i type='button' class='fa fa-times w3-xlarge w3-red w3-hover-orange' onclick='history.go(0)'></i></td></tr>";
				}
				else{
					echo "<tr><td>".$row["id"]."</td><td>".$row["namaAlat"]."</td><td>".$row["noSeri"]."</td><td>".$row["noSeriBaca"]."</td><td>Tidak diketahui</td><td><i type='button' class='fa fa-warning w3-large w3-dark-grey w3-hover-light-grey' onclick='history.go(0)'></i></td></tr>";
				}
			}
			echo "</table>";
		} else {
			echo "0 results";
		}
		$conn->close();
		?>
		<!-- PHP.MySQL.END --> 
      </div>
      <div>
	<input class="w3-table w3-button w3-dark-grey w3-centered" type="button" value = "Refresh" onclick="history.go(0)" />
      </div>
    </div>