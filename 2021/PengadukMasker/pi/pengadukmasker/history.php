<!-- PHP.MySQL.START -->
<?php
	@session_start();
	
	$nama = 0;
	
	if(isset($_POST['resetDate'])){
		unset($_SESSION['dateselect']);
		unset($_POST['dateselect']);
		unset($dateSelect);
		unset($_SESSION['ymd']);
	}
	if(isset($_POST['dateselect']) && isset($_POST['nama'])){
        $_SESSION['dateselect'] = $_POST['dateselect'];
        $_SESSION['nama'] = $_POST['nama'];
    }
    
    if(isset($_SESSION['dateselect']) && isset($_SESSION['nama'])){
        $dateSelect = $_SESSION['dateselect'];
        $nama = $_SESSION['nama'];
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
		
		if ($nama == '1'){
			$queryHistory      = "SELECT * FROM `pengadukmaskerlog` WHERE `pengadukmaskerlog`.`nama` = 'Mixer 1' AND `pengadukmaskerlog`.`waktu` BETWEEN '$startTime' AND '$endTime' ORDER BY `id` DESC";
		} else if ($nama == '2'){
			$queryHistory      = "SELECT * FROM `pengadukmaskerlog` WHERE `pengadukmaskerlog`.`nama` = 'Mixer 2' AND `pengadukmaskerlog`.`waktu` BETWEEN '$startTime' AND '$endTime' ORDER BY `id` DESC";
		} else if ($nama == '3'){
			$queryHistory      = "SELECT * FROM `pengadukmaskerlog` WHERE `pengadukmaskerlog`.`nama` = 'Mixer 3' AND `pengadukmaskerlog`.`waktu` BETWEEN '$startTime' AND '$endTime' ORDER BY `id` DESC";
		} else {
			$queryHistory      = "SELECT * FROM `pengadukmaskerlog` WHERE `pengadukmaskerlog`.`waktu` BETWEEN '$startTime' AND '$endTime' ORDER BY `id` DESC";
		}
		
		$ymd = date("Y-m-d", strtotime($dateSelect));
		$_SESSION['ymd'] = $ymd;
		
	} else{
		$queryHistory      = "SELECT * FROM `pengadukmaskerlog` ORDER BY `id` DESC";
	}
	$PaginatorHistory  = new Paginator( $connHistory, $queryHistory);
	if ($PaginatorHistory->getNumRows() > 0){
		$resultsHistory    = $PaginatorHistory->getData( $pageHistory, $limitHistory );
	}
?>
<!DOCTYPE html>
<html>
	<head>
		<title>Pengaduk Masker</title>
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
	<body class="w3-light-grey" onload="setClock()">
		<!-- Top container -->
		<div class="w3-bar w3-top w3-black w3-large" style="z-index:4">
		  <button type="button" class="w3-bar-item w3-button w3-hide-large w3-hover-none w3-hover-text-light-grey" onclick="w3_open();"><i class="fa fa-bars"></i> ??Menu</button>
		  <span class="w3-bar-item w3-right w3-xlarge"><img src="static/images/favicon.png" alt="favicon" height="24px" width="24px"></span>
		</div>

		<!-- Sidebar/menu -->
		<nav class="w3-sidebar w3-bar-block w3-collapse w3-white w3-animate-left" style="z-index:3;width:140px;" id="mySidebar"><br>
		  <div class="w3-container w3-blue-grey">
			<h5>Menu</h5>
		  </div>
		  <div class="w3-bar-block">
			<a href="#" class="w3-bar-item w3-button w3-padding-16 w3-hide-large w3-grey w3-hover-black" onclick="w3_close()" title="Close"><i class="fa fa-remove fa-fw"></i>?? Close</a>
			<a href="index.php" class="w3-bar-item w3-button w3-padding"><i class="fa fa-info-circle fa-fw"></i>?? Status</a>
			<a href="history.php" class="w3-bar-item w3-button w3-padding w3-grey"><i class="fa fa-history fa-fw"></i><strong>?? History</strong></a>
		  </div>
		</nav>

		<!-- Overlay effect when opening sidebar on small screens -->
		<div class="w3-overlay w3-hide-large w3-animate-opacity" onclick="w3_close()" style="cursor:pointer" title="close side menu" id="myOverlay"></div>

		<!-- !PAGE CONTENT! -->
		<div class="w3-main w3-light-grey" style="margin-left:140px;margin-top:43px;">

		  <!-- Header -->
		  <header class="w3-container" style="padding-top:22px">
			<div class="w3-container w3-blue-grey">
				<h2>History <?php echo ($nama == 0)? '(Semua Mixer)': '(Mixer ' . $nama . ')'; ?> </h2>
			  </div>
		  </header>
		  
		  <!-- Feeds panel -->
		  <div class="w3-panel">
			<div class="w3-row-padding w3-container" style="margin:0 -16px">
			  <div>
				<!-- PUT TABLE HERE -->				
				<div class="w3-cell-row">
					<div class="w3-left-align">
						<form action="history.php" method="post" onsubmit="return valDate()" required>
							<label for="nama">Tipe</label>
							<select id="nama" name="nama" autofocus>
							 <option value="0" <?php echo ($nama == 0)? 'selected': ''; ?> >Semua</option>
							 <option value="1" <?php echo ($nama == 1)? 'selected': ''; ?> >Mixer 1</option>
							 <option value="2" <?php echo ($nama == 2)? 'selected': ''; ?> >Mixer 2</option>
							 <option value="3" <?php echo ($nama == 3)? 'selected': ''; ?> >Mixer 3</option>
							</select>
							<label for="dateselect">Set tanggal: </label>
							<input type="date" id="dateselect" name="dateselect" min="2021-01-01" max="<?php echo date("Y-m-d"); ?>" value="<?php echo (isset($_SESSION['ymd']) ? $_SESSION['ymd'] : ""); ?>">
							<input type="submit" value="Pilih">
							<input type="submit" value="Reset" id="resetDate" name="resetDate">
						</form>
					</div>
				</div>
				<br>
				<table class="w3-table-all w3-centered w3-card-4 w3-white">
							<tr class='w3-blue-grey'>
								<th style="vertical-align: middle;">No</th>
                                <th style="vertical-align: middle;">Nama</th>
                                <th style="vertical-align: middle;">Status</th>
                                <th style="vertical-align: middle;">Total</th>
								<th style="vertical-align: middle;">Waktu</th>
							</tr>
							<?php
								if ($PaginatorHistory->getNumRows() > 0) {
									$validData = 0;
									for( $i = 0; $i < count( $resultsHistory->data ); $i++ ) :
										echo "<tr>";
											echo "<td>" . ($i+1) . "</td>";
											echo "<td>" . strtoupper($resultsHistory->data[$i]['nama']) . "</td>";
											echo "<td>" . $resultsHistory->data[$i]['status'] . "</td>";
											echo "<td>" . $resultsHistory->data[$i]['total'] . "</td>";
											echo "<td>" . $resultsHistory->data[$i]['waktu'] . "</td>";
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
		</script>
	</body>
</html>