<!-- PHP.MySQL.START -->
<?php		
	@session_start();
	if(isset($_POST['resetDate'])){
		unset($_SESSION['dateselect']);
		unset($_POST['dateselect']);
		unset($dateSelect);
		unset($_SESSION['ymd']);
	}
	
	if(isset($_POST['node'])){
		$_SESSION['node'] = $_POST['node'];
		if(isset($_SESSION['PJU'])){
			unset($_SESSION['PJU']);
		}
	}
	
	if(isset($_POST['PJU'])){
		$_SESSION['PJU'] = $_POST['PJU'];
		if(isset($_SESSION['node'])){
			unset($_SESSION['node']);
		}
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
		if (isset($_SESSION['node'])){
			$queryHistory      = "SELECT id, voltage AS v, current AS c, timestamp AS ts FROM `loralampulog` WHERE `timestamp` BETWEEN '$startTime' AND '$endTime' ORDER BY `id` DESC";
		} else if (isset($_SESSION['PJU'])){
			$queryHistory      = "SELECT id, voltage AS v, current AS c, timestamp AS ts FROM `loralampupjulog` WHERE `timestamp` BETWEEN '$startTime' AND '$endTime' ORDER BY `id` DESC";
		} else {
			$queryHistory      = "SELECT id, voltage AS v, current AS c, timestamp AS ts FROM `loralampulog` WHERE `timestamp` BETWEEN '$startTime' AND '$endTime' ORDER BY `id` DESC";
		}
		
		$ymd = date("Y-m-d", strtotime($dateSelect));
		$_SESSION['ymd'] = $ymd;
		
	} else{
		if (isset($_SESSION['node'])){
			$queryHistory      = "SELECT id, voltage AS v, current AS c, timestamp AS ts FROM `loralampulog`";
		} else if (isset($_SESSION['PJU'])){
			$queryHistory      = "SELECT id, voltage AS v, current AS c, timestamp AS ts FROM `loralampupjulog`";
		} else {
			$queryHistory      = "SELECT id, voltage AS v, current AS c, timestamp AS ts FROM `loralampulog`";
			$_SESSION['node'] = 1;
		}
		
	}
	$PaginatorHistory  = new Paginator( $connHistory, $queryHistory);
	if ($PaginatorHistory->getNumRows() > 0){
		$resultsHistory    = $PaginatorHistory->getData( $pageHistory, $limitHistory );
	}
?>
<!DOCTYPE html>
<html>
	<head>
		<title>Lampu LoRa</title>
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
		</style>
	</head>
	<body class="w3-light-grey">
		<!-- Top container -->
		<div class="w3-bar w3-top w3-black w3-large" style="z-index:4">
		  <button type="button" class="w3-bar-item w3-button w3-hide-large w3-hover-none w3-hover-text-light-grey" onclick="w3_open();"><i class="fa fa-bars"></i>  Menu</button>
		  <span class="w3-bar-item w3-right w3-xlarge"><img src="static/images/favicon.png" alt="favicon" height="24px" width="24px"></span>
		</div>

		<!-- Sidebar/menu -->
		<nav class="w3-sidebar w3-bar-block w3-collapse w3-white w3-animate-left" style="z-index:3;width:140px;" id="mySidebar"><br>
		  <div class="w3-container w3-blue">
			<h5>Menu</h5>
		  </div>
		  <div class="w3-bar-block">
			<a href="#" class="w3-bar-item w3-button w3-padding-16 w3-hide-large w3-grey w3-hover-black" onclick="w3_close()" title="Close"><i class="fa fa-remove fa-fw"></i>  Close</a>
			<a href="index.php" class="w3-bar-item w3-button w3-padding"><i class="fa fa-info-circle fa-fw"></i>  Status</a>
			<a href="history.php" class="w3-bar-item w3-button w3-padding w3-grey"><i class="fa fa-history fa-fw"></i><strong>  History</strong></a>
		  </div>
		</nav>

		<!-- Overlay effect when opening sidebar on small screens -->
		<div class="w3-overlay w3-hide-large w3-animate-opacity" onclick="w3_close()" style="cursor:pointer" title="close side menu" id="myOverlay"></div>

		<!-- !PAGE CONTENT! -->
		<div class="w3-main w3-light-grey" style="margin-left:140px;margin-top:43px;">

		  <!-- Header -->
		  <header class="w3-container" style="padding-top:22px">
			<div class="w3-container w3-blue w3-cell-row">
				<h2>History</h2>
			</div>
		  </header>
		  
		  <!-- Feeds panel -->
		  <div class="w3-panel">
			<div class="w3-row-padding w3-container" style="margin:0 -16px">
			  <div>
				<!-- PUT TABLE HERE -->
				<div class="w3-cell-row">
					<div class="w3-cell">
						<div class="w3-left-align">
							<form action="history.php" method="post" onsubmit="return valDate()" required>
								<label for="dateselect">Set tanggal: </label>
								<input class="" type="date" id="dateselect" name="dateselect" min="2019-01-01" max="<?php echo date("Y-m-d"); ?>" value="<?php echo (isset($_SESSION['ymd']) ? $_SESSION['ymd'] : ""); ?>">
								<input class="w3-button w3-ripple w3-blue w3-padding-small" type="submit" value="Pilih">
								<input class="w3-button w3-ripple w3-blue w3-padding-small" type="submit" value="Reset" id="resetDate" name="resetDate">
							</form>
							
						</div>
					</div>
					<div class="w3-cell">
						<div class="w3-right-align">
							<button onclick="nodeSend();" class="w3-button w3-ripple w3-padding-small <?php echo (isset($_SESSION['node']) ? "w3-gray" : "w3-blue");?>" id="node" name="node">Node</button>
							<button onclick="PJUSend();" class="w3-button w3-ripple w3-padding-small <?php echo (isset($_SESSION['PJU']) ? "w3-gray" : "w3-blue");?>" id="PJU" name="PJU">PJU</button>
							<form id="form" hidden></form>
						</div>
					</div>
				</div>
				<br>
				<table class="w3-table-all w3-centered w3-card-4 w3-white">
							<tr class='w3-blue'>
								<th>No</th>
								<th>Id</th>
								<th>Voltage (V)</th>
								<th>Current (A)</th>
								<th>Timestamp</th>
							</tr>
							<?php	if ($PaginatorHistory->getNumRows() > 0) {
										for( $i = 0; $i < count( $resultsHistory->data ); $i++ ) :
											echo "<tr>";
												echo "<td>".($i+1)."</td>";
												echo "<td>".hexdec($resultsHistory->data[$i]['id'])."</td>";
												echo "<td>".$resultsHistory->data[$i]['v']."</td>";
												echo "<td>".(!isset($resultsHistory->data[$i]['c']) ? "-" : $resultsHistory->data[$i]['c'])."</td>";
												echo "<td>".(!isset($resultsHistory->data[$i]['ts']) ? "-" : $resultsHistory->data[$i]['ts'])."</td>";
											echo "</tr>";
										endfor; 
									}
									else{
										echo "<tr><td colspan='5'>Kosong</td></tr>";
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
			
			function nodeSend(){			
				var http_request = new XMLHttpRequest();
				try{
				   // Opera 8.0+, Firefox, Chrome, Safari
				   http_request = new XMLHttpRequest();
				}catch (e) {
				   // Internet Explorer Browsers
				   try{
					  http_request = new ActiveXObject("Msxml2.XMLHTTP");
						
				   }catch (e) {
					
					  try{
						 http_request = new ActiveXObject("Microsoft.XMLHTTP");
					  }catch (e) {
						 // Something went wrong
						 alert("Your browser broke!");
						 return false;
					  }
						
				   }
				}
				
				http_request.onreadystatechange = function() {

				   if (http_request.readyState == 4  ) {
					   window.location.href = window.location.href;
				   }
				};
				http_request.open("POST", "history.php", true);
				http_request.setRequestHeader("Content-Type", "application/x-www-form-urlencoded; charset=UTF-8");
				http_request.send('node=1');
			}
			
			function PJUSend(){
				var http_request = new XMLHttpRequest();
				try{
				   // Opera 8.0+, Firefox, Chrome, Safari
				   http_request = new XMLHttpRequest();
				}catch (e) {
				   // Internet Explorer Browsers
				   try{
					  http_request = new ActiveXObject("Msxml2.XMLHTTP");
						
				   }catch (e) {
					
					  try{
						 http_request = new ActiveXObject("Microsoft.XMLHTTP");
					  }catch (e) {
						 // Something went wrong
						 alert("Your browser broke!");
						 return false;
					  }
						
				   }
				}
				
				http_request.onreadystatechange = function() {

				   if (http_request.readyState == 4  ) {
					   window.location.href = window.location.href;
				   }
				};
				http_request.open("POST", "history.php", true);
				http_request.setRequestHeader("Content-Type", "application/x-www-form-urlencoded; charset=UTF-8");
				http_request.send('PJU=1');
			}
		</script>
	</body>
</html>