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
		$queryHistory      = "SELECT * FROM `kualitasudaralog` WHERE `timestamp` BETWEEN '$startTime' AND '$endTime' ORDER BY `id` DESC";
		
		$ymd = date("Y-m-d", strtotime($dateSelect));
		$_SESSION['ymd'] = $ymd;
		
	} else{
		$queryHistory      = "SELECT * FROM `kualitasudaralog`";
	}
	$PaginatorHistory  = new Paginator( $connHistory, $queryHistory);
	if ($PaginatorHistory->getNumRows() > 0){
		$resultsHistory    = $PaginatorHistory->getData( $pageHistory, $limitHistory );
	}
?>
<!DOCTYPE html>
<html>
	<head>
		<title>Kualitas Udara Logs</title>
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
	<body class="w3-light-grey" onload="updateClock()">
		<!-- Top container -->
		<div class="w3-bar w3-top w3-black w3-large" style="z-index:4">
		  <button type="button" class="w3-bar-item w3-button w3-hide-large w3-hover-none w3-hover-text-light-grey" onclick="w3_open();"><i class="fa fa-bars"></i>  Menu</button>
		  <span class="w3-bar-item w3-right w3-xlarge"><img src="static/images/favicon.png" alt="favicon" height="24px" width="24px"></span>
		</div>

		<!-- Overlay effect when opening sidebar on small screens -->
		<div class="w3-overlay w3-hide-large w3-animate-opacity" onclick="w3_close()" style="cursor:pointer" title="close side menu" id="myOverlay"></div>

		<!-- !PAGE CONTENT! -->
		<div class="w3-main w3-light-grey" style="margin-top:43px;">

		  <!-- Header -->
		  <header class="w3-container" style="padding-top:22px">
			 <div class="w3-cell-row w3-blue-grey">
			  <div class="w3-container w3-cell">
				<h2>Logs</h2>
			  </div>
			  <div class="w3-container w3-cell w3-right-align">
				<h2 id="clock">Clock</h2>
			  </div>
			</div>
		  </header>
		  
		  <!-- Feeds panel -->
		  <div class="w3-panel">
			<div class="w3-row-padding w3-container" style="margin:0 -16px">
			  <div>
				<!-- PUT TABLE HERE -->				
				<div class="w3-cell-row">
					<div class="w3-left-align">
						<form action="index.php" method="post" onsubmit="return valDate()" required>
							<label for="dateselect">Set tanggal: </label>
							<input type="date" id="dateselect" name="dateselect" min="2019-01-01" max="<?php echo date("Y-m-d"); ?>" value="<?php echo (isset($_SESSION['ymd']) ? $_SESSION['ymd'] : ""); ?>">
							<input type="submit" value="Pilih">
							<input type="submit" value="Reset" id="resetDate" name="resetDate">
						</form>
					</div>
				</div>
				<br>
				<table class="w3-table-all w3-centered w3-card-4 w3-white">
							<tr class='w3-blue-grey'>
								<th style="vertical-align: middle;">No</th>
								<th style="vertical-align: middle;">CO 1</th>
								<th style="vertical-align: middle;">CO 2</th>
								<th style="vertical-align: middle;">CO 3</th>
								<th style="vertical-align: middle;">Debu</th>
								<th style="vertical-align: middle;">Jumlah</th>
								<th style="vertical-align: middle;">Waktu</th>
							</tr>
							<?php	
									if ($PaginatorHistory->getNumRows() > 0) {
										$validData = 0;
										for( $i = 0; $i < count( $resultsHistory->data ); $i++ ) :
											echo "<tr>";
												echo "<td>".($i+1)."</td>";
												echo "<td>".$resultsHistory->data[$i]['ppm1']."</td>";
												echo "<td>".$resultsHistory->data[$i]['ppm2']."</td>";
												echo "<td>".$resultsHistory->data[$i]['ppm3']."</td>";
												echo "<td>".$resultsHistory->data[$i]['dust']."</td>";
												echo "<td>".$resultsHistory->data[$i]['jumlah']."</td>";
												echo "<td>".$resultsHistory->data[$i]['timestamp']."</td>";
											echo "</tr>";
										endfor;
									}
									else{
										echo "<tr><td colspan='9'>Kosong</td></tr>";
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
		<script type="text/javascript">
			function updateClock ( ){
				var currentTime = new Date ();

				var currentYear = currentTime.getFullYear();
				var currentMonth = currentTime.getMonth();
				var currentDate = currentTime.getDate();
				var currentHours = currentTime.getHours ( );
				var currentMinutes = currentTime.getMinutes ( );
				var currentSeconds = currentTime.getSeconds ( );

				const monthNames = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun",
									  "Jul", "Agu", "Sep", "Okt", "Nov", "Des"
									];

				// Pad the minutes and seconds with leading zeros, if required
				currentMinutes = ( currentMinutes < 10 ? "0" : "" ) + currentMinutes;
				currentSeconds = ( currentSeconds < 10 ? "0" : "" ) + currentSeconds;

				// Choose either "AM" or "PM" as appropriate
				//var timeOfDay = ( currentHours < 12 ) ? "AM" : "PM";

				// Convert the hours component to 12-hour format if needed
				//currentHours = ( currentHours > 12 ) ? currentHours - 12 : currentHours;

				// Convert an hours component of "0" to "12"
				//currentHours = ( currentHours == 0 ) ? 12 : currentHours;

				// Compose the string for display
				//var currentTimeString = currentHours + ":" + currentMinutes + ":" + currentSeconds + " " + timeOfDay;
				var currentTimeString =  currentDate + " " + monthNames[currentMonth] + " "+ currentYear + " " + currentHours + ":" + currentMinutes + ":" + currentSeconds;

				// Update the time display
				document.getElementById("clock").firstChild.nodeValue = currentTimeString;
			}
			setInterval('updateClock()', 1000 );
			
			function valBatch(){
				var valueBatch = document.getElementById('batchselect').value;
				if((valueBatch == '')){
					alert('Text is invalid or empty!');
					return false;
				}
			}
			
		</script>
	</body>
</html>