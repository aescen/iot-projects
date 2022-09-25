<!-- PHP.MySQL.START -->
<?php
	require_once 'inits.php';
	require_once 'db.php';
  $idKolam = 'B';

	$sql = "SELECT * FROM `pantaubioflok` WHERE kolam = '".$idKolam."'";
	$result = $conn->query($sql);
?>
<!-- PHP.MySQL.END --> 

<?php
  if ( $result->num_rows > 0 ) {
    // output data of each row
    if( $row = $result->fetch_assoc() ) {
      echo "<div class='w3-white'>";
      echo "<table class='w3-table w3-large w3-striped w3-white w3-centered'>";
      echo "<thead><tr class='w3-blue'>
        <td class='w3-left'>Ketersediaan Pakan</td>
        <td>".$row["pakan"]." gram</td></tr></thead>";
      echo "</table>";
      echo "</div>";
      
      echo "<br>";
      
      echo "<div class='w3-white'>";
      echo "<table class='w3-table w3-large w3-striped w3-white w3-centered'>";
      echo "<thead><tr class='w3-blue'>
        <td>Cuaca</td>
        <td>Kekeruhan</td>
        <td>Jadwal Pakan</td></tr></thead>";
      echo "<tr'>
        <td>".$row["cuaca"]."</td>
        <td>".($row["kekeruhan"])." ppm</td>
        <td>".$row["waktu"]."</td></tr>";
      echo "</table>";
      echo "</div>";
        
    }
  } else {
    echo "0 results";
  }
?>

<br>
<div class='w3-cell-row w3-center '>
  <div class='w3-container w3-cell w3-cell-middle w3-mobile'>
    <div id="chartContainerCuaca"></div>
    <div class='w3-white'>
      <h1>Data Kosong</h1>
    </div>
  </div>
  <div class='w3-container w3-cell w3-cell-middle w3-mobile'>
    <div id="chartContainerKekeruhan"></div>
    <div class='w3-white'>
      <h1>Data Kosong</h1>
    </div>
  </div>
</div>

<?php
  $cuacaY = array('HUJAN' => 1, 'CERAH' => 2);
  $startTime = date('Y-m-d') . " 00:00:00.000000";
  $endTime = date('Y-m-d') . " 23:59:59.999999";
  $sqlCuaca = "SELECT `id`, `cuaca`, `time_stamp` FROM `pantaubioflok_log` WHERE `kolam` = '" . $idKolam . "' AND `time_stamp` BETWEEN '$startTime' AND '$endTime' ORDER BY `pantaubioflok_log`.`id` DESC LIMIT 12";
  $sqlKekeruhan = "SELECT `id`, `kekeruhan`, `time_stamp` FROM `pantaubioflok_log` WHERE `kolam` = '" . $idKolam . "' AND `time_stamp` BETWEEN '$startTime' AND '$endTime' ORDER BY `pantaubioflok_log`.`id` DESC LIMIT 12";
	$dataPointsCuaca = array();
	$resultCuaca = $conn->query($sqlCuaca);
  $isResultCuacaOk = false;
  if ( $resultCuaca->num_rows > 0 ) {
    $isResultCuacaOk = true;
		while ($rowCuaca = $resultCuaca->fetch_assoc()) {
			array_push($dataPointsCuaca, array(
          "label" => $rowCuaca["time_stamp"],
          "y" => $cuacaY[$rowCuaca["cuaca"]],
          "indexLabel" => $rowCuaca["cuaca"],
          "indexLabelOrientation" => "vertical",
        )
      );
		}
	} else {
    
  }
  //echo json_encode($dataPointsCuaca);
	$dataPointsKekeruhan = array();
	$resultKekeruhan = $conn->query($sqlKekeruhan);
  $isResultKekeruhanOk = false;
  if ( $resultKekeruhan->num_rows > 0 ) {
    $isResultKekeruhanOk = true;
		while ($rowKekeruhan = $resultKekeruhan->fetch_assoc()) {
			array_push($dataPointsKekeruhan, array( "label" => $rowKekeruhan["time_stamp"], "y" => (float)$rowKekeruhan["kekeruhan"] ));
		}
	}
?>

<script type="text/javascript">
  $(function () {
    const chartCuaca = new CanvasJS.Chart("chartContainerCuaca", {
      theme: "light2",
      zoomEnabled: true,
      title: {
          text: "Cuaca"
      },
      axisY:
        {
         title: "Ket",
        },
      data: [
        {
          type: "line",
          name: "Cuaca",
          color: "#369EAD",
          showInLegend: true,
          dataPoints: <?php echo json_encode($dataPointsCuaca); ?>
        },
      ]
    });
    
    const chartKekeruhan = new CanvasJS.Chart("chartContainerKekeruhan", {
      theme: "light2",
      zoomEnabled: true,
      title: {
          text: "Kekeruhan"
      },
      axisY:
        {
         title: "Kadar",
         suffix: " ppm"
        },
      data: [
        {
          type: "line",
          name: "Kekeruhan",
          color: "#C24642",
          showInLegend: true,
          dataPoints: <?php echo json_encode($dataPointsKekeruhan); ?>
        },
      ]
    });
  
    <?php if($isResultCuacaOk) echo 'chartCuaca.render();';?>;
    <?php if($isResultKekeruhanOk) echo 'chartKekeruhan.render();';?>;
  });
</script>
<br>