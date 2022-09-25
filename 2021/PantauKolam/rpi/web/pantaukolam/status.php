<!-- Header -->
<header class="w3-container" style="padding-top:22px">
  <div class="w3-container w3-card w3-orange">
    <h2>Status Turbin</h2>
  </div>
</header>

<!-- Feeds panel -->
<div class="w3-container" style="margin-left:8px;margin-right:8px;margin-top:20px;">
  <div class="w3-row-padding" style="margin:0 -16px">
    <!-- PUT TABLE HERE -->
    <!-- PHP.MySQL.START -->
    <?php
    require_once 'db.php';

    $sql = "SELECT * FROM `pantaukolam_turbin`";
    $result = $conn->query($sql);

    if ($result->num_rows > 0) {
      echo "<table class='w3-table-all w3-centered w3-card-4 w3-white'>
				<tr class='w3-orange'><th>Id</th>
					<th>Putaran Turbin (RPM)</th>
					<th>Daya (W)</th>
                    <th>Debit A (L/menit)</th>
                    <th>Debit B (L/menit)</th>
                    <th>ph A</th>
					<th>Timestamp</th></tr>";
      // output data of each row
      while ($row = $result->fetch_assoc()) {
        echo "<tr><td>" . hexdec($row["id"]) . "</td>
					   <td>" . $row["valRpm"] . "</td>
					   <td>" . $row["valDaya"] . "</td>
                       <td>" . $row["valDebitA"] . "</td>
                       <td>" . $row["valDebitB"] . "</td>
                       <td>" . $row["valPhA"] . "</td>
					   <td>" . $row["timeStamp"] . "</td></tr>";
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
  <div class="w3-container w3-card w3-orange">
    <h2>Status Kolam Ikan</h2>
  </div>
</header>

<!-- Feeds panel -->
<div class="w3-container" style="margin-left:8px;margin-right:8px;margin-top:20px;">
  <div class="w3-row-padding" style="margin:0 -16px">
    <!-- PUT TABLE HERE -->
    <!-- PHP.MySQL.START -->
    <?php
    require_once 'db.php';

    $sql = "SELECT * FROM `pantaukolam_kolam`";
    $result = $conn->query($sql);

    if ($result->num_rows > 0) {
      echo "<table class='w3-table-all w3-centered w3-card-4 w3-white'>
				<tr class='w3-orange'><th>Id</th>
					<th>ph B</th>
                    <th>Turbidity (ppm)</th>
					<th>Timestamp</th></tr>";
      // output data of each row
      while ($row = $result->fetch_assoc()) {
        echo "<tr><td>" . hexdec($row["id"]) . "</td>
					   <td>" . $row["valPhB"] . "</td>
                       <td>" . $row["valTurbidity"] . "</td>
					   <td>" . $row["timeStamp"] . "</td></tr>";
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