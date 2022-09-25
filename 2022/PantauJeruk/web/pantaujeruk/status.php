<!-- PHP.MySQL.START -->
<?php
	require_once 'inits.php';
	require_once 'db.php';

	$sql = "SELECT * FROM `pantaujeruk`";
  $statusSpray = "...";
  $timeSpray = "...";
?>
<!-- PHP.MySQL.END --> 

<div class='w3-card-4 w3-white'>
  <div class="w3-cell-row w3-lime">
    <?php
      $result = $conn->query($sql);
      if ( $result->num_rows > 0 ) {
        while( $row = $result->fetch_assoc() ) {
          if($row["spray"] != null) {
            $statusSpray = STATUS_SPRAY[$row["spray"]];
            $timeSpray = $row["time_stamp"];
          }
        }
      } else {
        echo "0 results";
      }
    ?>
    <div class="w3-cell">
      <div class='w3-padding-16 w3-margin-left'><strong>Status :  <?php echo $statusSpray; ?></strong></div>
    </div>
    <div class="w3-cell w3-cell-middle">
      <div class='w3-padding-16 w3-margin-right w3-right'><strong>Waktu :  <?php echo $timeSpray; ?></strong></div>
    </div>
  </div>
</div>
<br>
<div class='w3-card-4 w3-white'>
  <table class='w3-table w3-striped w3-white w3-centered'>
    <thead><tr class='w3-lime'><td>ID Node</td>
      <td>Kelembapan</td>
      <td>PH Tanah</td>
      <td>Waktu</td></tr></thead>
<?php
  $result = $conn->query($sql);
  if ( $result->num_rows > 0 ) {
    while( $row = $result->fetch_assoc() ) {
      if($row["moist"] != null && $row["ph"] != null) {
        echo "<tr'><td>".$row["node_id"]."</td>
          <td>".$row["moist"]." %</td><td>".($row["ph"])."</td>
          <td>".$row["time_stamp"]."</td></tr>";
      }
    }
  } else {
    echo "0 results";
  }
?>
  </table>
</div>
