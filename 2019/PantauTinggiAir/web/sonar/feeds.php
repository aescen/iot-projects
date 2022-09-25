<div id="chartContainer"></div>

<?php
	include("config.php");
	if( session_id() == ''){
		session_start();
	}
	if( !isset($_SESSION['play']) ){
			$_SESSION['play'] = false;
	}else{ $play = $_SESSION['play']; }
	
	if( !isset($_SESSION['alarm']) ){
			$_SESSION['alarm'] = false;
	}else{ $alarm = $_SESSION['alarm']; }
	
	if (!isset($play)){
		$play = $_SESSION['play'];
	}
	if($alarm == true){
		if($play == false){
			echo "<script>play();</script>";
			echo "<script>console.log('Alarm:on');</script>";
			$play=true;
			$_SESSION['play'] = true;
		}else if($play == true){
			echo "<script>console.log('Alarm:on:playing');</script>";
		}
	}else if($alarm == false){
		if($play == true){
			echo "<script>stop();</script>";
			echo "<script>console.log('Alarm:off');</script>";
			$play=false;
			$_SESSION['play'] = false;
		}else if($play == false){
			echo "<script>console.log('Alarm:off:stopped');</script>";
		}
	}
	
	$sql1="SELECT * FROM `status` WHERE `Nama` = 'data1' ORDER BY `Waktu`";
	$sql2="SELECT * FROM `status` WHERE `Nama` = 'data2' ORDER BY `Waktu`";
	$dataPoints1 = array();
	if ($result1 = $conn->query($sql1)) {
		/* fetch associative array */
		while ($row1 = $result1->fetch_assoc()) {
			//echo $row1["Waktu"].' '.$row1["Nilai"];
			array_push($dataPoints1, array( "label" => $row1["Waktu"], "y" => (int)$row1["Nilai"] ));
		}
	}
	$dataPoints2 = array();
	if ($result2 = $conn->query($sql2)) {
		/* fetch associative array */
		while ($row2 = $result2->fetch_assoc()) {
			//echo $row2["Waktu"].' '.$row2["Nilai"];
			array_push($dataPoints2, array( "label" => $row2["Waktu"], "y" => (int)$row2["Nilai"] ));
			if((int)$row2["Nilai"] <= 10){
				$_SESSION['btn'] = 'button-red';
				$_SESSION['setAlarm'] = true;
			}else{
				$_SESSION['btn'] = 'button-green';
				$_SESSION['setAlarm'] = false;
			}
		}
	}
	if( ( isset($_SESSION['setAlarm']) ) && ( $_SESSION['setAlarm'] == true ) ){
		$_SESSION['alarm'] = true;
	}else{
		$_SESSION['alarm'] = false;
	}
?>

<script type="text/javascript">

    $(function () {
        var chart = new CanvasJS.Chart("chartContainer", {
            theme: "light2",
            zoomEnabled: true,
            title: {
                text: "Jarak vs Jarak Terfilter"
            },
            subtitles: [
                {
                    text: ""
                }
            ],
			axisY: {
				title: "Jarak",
				suffix: " cm"
			},
            data: [
            {
                type: "line",
				name: "Jarak",
				color: "#369EAD",
				showInLegend: true,
                dataPoints: <?php echo json_encode($dataPoints1); ?>
            },
			{
                type: "line",
				name: "Jarak terfilter",
				color: "#C24642",
				showInLegend: true,
                dataPoints: <?php echo json_encode($dataPoints2); ?>
            }
            ]
        });
        chart.render();
    });
</script>