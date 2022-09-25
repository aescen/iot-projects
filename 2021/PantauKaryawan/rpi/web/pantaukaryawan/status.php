<!-- Feeds panel -->
<div class="w3-row-padding w3-container" style="margin:0 -16px">
  <!-- PUT TABLE HERE -->
  <!-- PHP.MySQL.START -->
  <?php
  require_once 'inits.php';

  $sql = "SELECT * FROM `pantaukaryawan`";
  $result = $conn->query($sql);

  if ($result->num_rows > 0) {
    echo "<table class='w3-table-all w3-centered w3-card w3-white'>
            <tr class='w3-blue-grey'>
              <th>Id</th>
              <th>Heart Rate (bpm)</th>
              <th>Oxygen Level (spO2)</th>
              <th>Temp (&deg;C)</th>
              <th>Location</th>
              <th>Timestamp</th>
            </tr>";
    // output data of each row
    while ($row = $result->fetch_assoc()) {
      $strStatus = (floatval($row['valTemp']) > $threshTemp ? $statusStr1 . $tempBad . $statusStr2 : $statusStr1 . $tempOk . $statusStr2);
      echo "<tr>
              <td style='vertical-align: middle;'>" . $row['nodeId'] . "</td>
              <td style='vertical-align: middle;'>" . $row['valBpm'] . "</td>
              <td style='vertical-align: middle;'>" . $row['valOxy'] . "</td>
              <td style='vertical-align: middle;'>" . $row['valTemp'] . "&nbsp;<span>" . $strStatus . "</span></td>
              <td style='vertical-align: middle;'>" . $row['valLoc'] . "</td>
              <td style='vertical-align: middle;'>" . $row['timeStamp'] . "</td>
            </tr>";
    }
    echo "</table>";
  } else {
    echo "No results";
  }
  ?>
  <!-- PHP.MySQL.END -->
</div>
<hr>