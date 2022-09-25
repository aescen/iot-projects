<!-- PHP.MySQL.START -->
<?php
	@session_start();
	
	if(isset($_POST['resetDate'])){
		unset($_SESSION['dateselect']);
		unset($_POST['dateselect']);
		unset($dateSelect);
		unset($_SESSION['ymd']);
	}
	if(isset($_POST['dateselect'])){
		$_SESSION['dateselect'] = $_POST['dateselect'];
	}
	if(isset($_SESSION['dateselect'])){
		$dateSelect = $_SESSION['dateselect'];
	}
	else{
		unset($dateSelect);
		unset($resultsHistory);
	}
	require_once 'paginator.php';
	require_once 'db.php';
	
	$connHistory       = $conn;	
 
	$limitHistory      = ( isset( $_GET['limit'] ) ) ? $_GET['limit'] : 25;
	$pageHistory       = ( isset( $_GET['page'] ) ) ? $_GET['page'] : 1;
	$linksHistory      = ( isset( $_GET['links'] ) ) ? $_GET['links'] : 7;
	if( isset($dateSelect) ){
		$startTime = $dateSelect . " 00:00:00.000000";
		$endTime = $dateSelect . " 23:59:59.999999";
		$queryHistory      = "
      SELECT * FROM
      (
        SELECT e.time_stamp,
          (SELECT e2.total from `energyman_transmission_log` e2 WHERE e2.time_stamp = e.time_stamp AND e2.name = 'NODE 1') as node_1,
          (SELECT e2.total from `energyman_transmission_log` e2 WHERE e2.time_stamp = e.time_stamp AND e2.name = 'NODE 2') as node_2
        FROM `energyman_transmission_log` as e
        GROUP BY e.time_stamp
      ) as t
      WHERE t.time_stamp BETWEEN '$startTime' AND '$endTime' ORDER BY t.time_stamp DESC";
		
		$ymd = date("Y-m-d", strtotime($dateSelect));
		$_SESSION['ymd'] = $ymd;
		
	} else{
		$queryHistory      = "
      SELECT *, ((t.node_1 + t.node_2) / 2) as average FROM
      (
        SELECT e.time_stamp,
          (SELECT e2.total from `energyman_transmission_log` e2 WHERE e2.time_stamp = e.time_stamp AND e2.name = 'NODE 1') as node_1,
          (SELECT e2.total from `energyman_transmission_log` e2 WHERE e2.time_stamp = e.time_stamp AND e2.name = 'NODE 2') as node_2
        FROM `energyman_transmission_log` as e
        GROUP BY e.time_stamp
      ) as t
      ORDER BY t.time_stamp DESC";
	}
	$PaginatorHistory  = new Paginator( $connHistory, $queryHistory);
	if ($PaginatorHistory->getNumRows() > 0){
		$resultsHistory    = $PaginatorHistory->getData( $pageHistory, $limitHistory );
	}
?>
<!DOCTYPE html>
<html>
	<head>
		<title>Energy Management</title>
		<meta charset="UTF-8">
		<meta name="viewport" content="width=device-width, initial-scale=1">
		<link rel="shortcut icon" type="image/png" href="static/images/favicon.png"/>
		<link rel="stylesheet" href="static/styles/w3.css">
		<link rel="stylesheet" href="static/styles/theme.css">
		<link rel="stylesheet" href="static/styles/raleway.css">
		<link rel="stylesheet" href="static/styles/font-awesome.min.css">
		<script src="static/scripts/jquery.min.js"></script>
		<style>
			html,body,h1,h2,h3,h4,h5,h6 {font-family: "Raleway", sans-serif}
      tr:nth-child(even) {
        background-color: #DEE8F9;
      }
		</style>
	</head>
	<body class="w3-light-grey" onload="setClock()">
		<!-- Top container -->
		<div class="w3-bar w3-top w3-white w3-large" style="z-index:4">
		  <button type="button" class="w3-bar-item w3-button w3-hide-large w3-xlarge w3-hover-none w3-hover-text-light-grey" onclick="w3_open();"><i class="fa fa-bars"></i>  Menu</button>
      <span class="w3-bar-item w3-hide-small w3-hide-medium w3-xlarge">DASHBOARD</span>
		  <a href="#"><span class="w3-hover-grayscale w3-bar-item w3-right w3-medium" style="margin-top:8px;color:#3f51b5;">Hello, admin</span></a>
		</div>

		<!-- Sidebar/menu -->
		<nav class="w3-sidebar w3-bar-block w3-collapse w3-indigo w3-animate-left" style="z-index:3;width:140px;" id="mySidebar"><br>
		  <div class="w3-container w3-indigo">
			<h5>Menu</h5>
		  </div>
		  <div class="w3-bar-block">
			<a href="#" class="w3-bar-item w3-button w3-padding-16 w3-hide-large w3-grey w3-hover-black" onclick="w3_close()" title="Close"><i class="fa fa-remove fa-fw"></i>  Close</a>
			<a href="index.php" class="w3-bar-item w3-button w3-padding"><i class="fa fa-info-circle fa-fw"></i>  Status</a>
      <a href="charging.php" class="w3-bar-item w3-button w3-padding"><i class="fa fa-bolt fa-fw"></i>  Pengisian</a>
      <a href="transmission.php" class="w3-bar-item w3-button w3-padding w3-light-blue"><i class="fa fa-rocket fa-fw"></i>  Pengiriman</a>
		  </div>
		</nav>

		<!-- Overlay effect when opening sidebar on small screens -->
		<div class="w3-overlay w3-hide-large w3-animate-opacity" onclick="w3_close()" style="cursor:pointer" title="close side menu" id="myOverlay"></div>

		<!-- !PAGE CONTENT! -->
		<div class="w3-main w3-light-grey" style="margin-left:140px;margin-top:43px;">
		  
		  <!-- Feeds panel -->
		  <div class="w3-panel">
			<div class="w3-row-padding w3-container" style="margin:0 -16px;margin-top:32px;">
			  <div>
				<!-- PUT TABLE HERE -->
				<table class="w3-table-all w3-centered w3-card-4 w3-white">
              <thead>
							<tr class='w3-indigo'>
                <th style="vertical-align: middle;" rowspan=3>Tanggal</th>
								<th style="vertical-align: middle;" colspan=5>Rata - Rata Pengiriman Setiap Node</th>
							</tr>
              <tr class='w3-indigo'>
                <th style="vertical-align: middle;">Node 1</th>
								<th style="vertical-align: middle;">Node 2</th>
								<th style="vertical-align: middle;">Rata - Rata</th>
              </tr>
              </thead>
							<?php	
								if ($PaginatorHistory->getNumRows() > 0) {
									for( $i = 0; $i < count( $resultsHistory->data ); $i++ ) :
                    $node_1 = ($resultsHistory->data[$i]['node_1'] != "") ? intval($resultsHistory->data[$i]['node_1']) : 0;
                    $node_2 = ($resultsHistory->data[$i]['node_2'] != "") ? intval($resultsHistory->data[$i]['node_2']) : 0;
                    $average = (($node_1 + $node_2) / 2);
                    if ($node_1 > 0 && $node_2 == 0) {
                      $average = $node_1;
                    } else if ($node_1 == 0 && $node_2 > 0) {
                      $average = $node_2;
                    }
										echo "<tr>";
											echo "<td>".$resultsHistory->data[$i]['time_stamp']."</td>";
											echo "<td>".$node_1."</td>";
											echo "<td>".$node_2."</td>";
                      echo "<td>".$average."</td>";
										echo "</tr>";
									endfor;
								}
								else{
									echo "<tr><td colspan='7'>Kosong</td></tr>";
								}
						?>
				</table>
				<br>
				<?php
					if ($PaginatorHistory->getNumRows() > 0){
						if ($PaginatorHistory->getLastPageNum() > 1){
							echo $PaginatorHistory->createLinks( $linksHistory, 'w3-bar-item w3-button w3-border' );
						}
					}
				?>
			  </div>
			</div>
		  </div>
		  <!-- End page content -->
		</div>
		<script>
			// Get the Sidebar
			var mySidebar = document.getElementById("mySidebar");

			// Get the DIV with overlay effect
			var overlayBg = document.getElementById("myOverlay");

			// Toggle between showing and hiding the sidebar, and add overlay effect
			function w3_open() {
			  if (mySidebar.style.display === 'block') {
				mySidebar.style.display = 'none';
				overlayBg.style.display = "none";
			  } else {
				mySidebar.style.display = 'block';
				overlayBg.style.display = "block";
			  }
			}

			// Close the sidebar with the close button
			function w3_close() {
			  mySidebar.style.display = "none";
			  overlayBg.style.display = "none";
			}
			
			function valDate(){
				var valueDate = document.getElementById('dateselect').value;
				if(!Date.parse(valueDate)){
					alert('Date is invalid or empty!');
					return false;
				}
			}
		</script>
	</body>
</html>