<?php
require_once "db.php";
$valConductivity = 100;
$nodeId = 1;
if (session_id() == '') {
  session_start();
}
if (!isset($_SESSION['play'])) {
  $_SESSION['play'] = false;
} else {
  $play = $_SESSION['play'];
}

if (!isset($_SESSION['alarm'])) {
  $_SESSION['alarm'] = false;
} else {
  $alarm = $_SESSION['alarm'];
}

if (!isset($play)) {
  $play = $_SESSION['play'];
}
if ($alarm == true) {
  if ($play == false) {
    echo "<script>play();</script>";
    //echo "<script>console.log('Alarm:on');</script>";
    $play = true;
    $_SESSION['play'] = true;
  } else if ($play == true) {
    //echo "<script>console.log('Alarm:on:playing');</script>";
  }
} else if ($alarm == false) {
  if ($play == true) {
    echo "<script>stop();</script>";
    //echo "<script>console.log('Alarm:off');</script>";
    $play = false;
    $_SESSION['play'] = false;
  } else if ($play == false) {
    //echo "<script>console.log('Alarm:off:stopped');</script>";
  }
}

$sqlConductivityChart =
  "SELECT * FROM (SELECT * FROM `pantautandonlog` WHERE `objectType` LIKE 'conductivity' AND `nodeId` = '" . $nodeId . "' ORDER BY `timeStamp` DESC LIMIT 12) aTable ORDER BY `timeStamp` ASC";
$dataPointsConductivity = array();
if ($resultConductivity = $conn->query($sqlConductivityChart)) {
  while ($rowConductivity = $resultConductivity->fetch_assoc()) {
    array_push($dataPointsConductivity, array("label" => $rowConductivity['timeStamp'], "y" => (float)$rowConductivity['valObject']));
    if ((int)$rowConductivity['valObject'] >= $valConductivity) {
      $_SESSION['btn'] = 'button-red';
      $_SESSION['setAlarm'] = true;
    } else {
      $_SESSION['btn'] = 'button-green';
      $_SESSION['setAlarm'] = false;
    }
  }
}

if ((isset($_SESSION['setAlarm'])) && ($_SESSION['setAlarm'] == true)) {
  $_SESSION['alarm'] = true;
} else {
  $_SESSION['alarm'] = false;
}
$sql = "SELECT * FROM `pantautandon` WHERE `objectType` LIKE 'conductivity' AND `nodeId` = '" . $nodeId . "'";
$result = $conn->query($sql);
?>

<table class='w3-table-all w3-centered w3-card w3-white'>
  <tr class='w3-blue'>
    <th style='vertical-align: middle;'>Conductivity (ppm)</th>
    <th style='vertical-align: middle;'>Timestamp</th>
  </tr>
  <?php
  if ($result->num_rows > 0) {
    while ($row = $result->fetch_assoc()) {
      echo "<tr>
            <td style='vertical-align: middle;'>" . $row['valObject'] . "</td>
            <td style='vertical-align: middle;'>" . $row['timeStamp'] . "</td>
          </tr>";
    }
  } else echo "<tr><td colspan='2'>Kosong</td></tr>";
  ?>
</table>
<br>
<div class="w3-card" id="chartContainer"></div>

<script type="text/javascript">
  $(function() {
    var chart = new CanvasJS.Chart("chartContainer", {
      theme: "light2",
      zoomEnabled: true,
      zoomType: "xy",
      title: {
        text: "_",
        fontColor: "white",
      },
      axisY: {
        title: "Conductivity",
        suffix: "ppm"
      },
      data: [{
        type: "line",
        name: "Conductivity",
        color: "#df1111",
        showInLegend: true,
        dataPoints: <?php echo json_encode($dataPointsConductivity); ?>
      }]
    });
    chart.render();
  });
</script>