<?php
	@session_start();
	@$_SESSION = array();
	@session_destroy();
?>
<!DOCTYPE html>
<html>
	<head>
		<title>Dumptruck JTD</title>
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
		  <span class="w3-bar-item w3-right w3-xlarge fa fa-circle"></span>
		</div>

		<!-- Sidebar/menu -->
		<nav class="w3-sidebar w3-bar-block w3-collapse w3-white w3-animate-left" style="z-index:3;width:140px;" id="mySidebar"><br>
		  <div class="w3-container w3-teal">
			<h5>Menu</h5>
		  </div>
		  <div class="w3-bar-block">
			<a href="#" class="w3-bar-item w3-button w3-padding-16 w3-hide-large w3-grey w3-hover-black" onclick="w3_close()" title="Close"><i class="fa fa-remove fa-fw"></i>  Close</a>
			<a href="index.php" class="w3-bar-item w3-button w3-padding"><i class="fa fa-info-circle fa-fw"></i>  Status</a>
			<a href="history.php" class="w3-bar-item w3-button w3-padding"><i class="fa fa-history fa-fw"></i>  History</a>
			<a href="platnomor.php" class="w3-bar-item w3-button w3-padding w3-grey"><i class="fa fa-save fa-fw"></i><strong>  Plat nomor</strong></a>
		  </div>
		</nav>

		<!-- Overlay effect when opening sidebar on small screens -->
		<div class="w3-overlay w3-hide-large w3-animate-opacity" onclick="w3_close()" style="cursor:pointer" title="close side menu" id="myOverlay"></div>

		<!-- !PAGE CONTENT! -->
		<div class="w3-main w3-light-grey" style="margin-left:140px;margin-top:43px;">

		  <!-- Header -->
		  <header class="w3-container" style="padding-top:22px">
			<div class="w3-container w3-teal">
				<h2>Plat Nomor</h2>
			  </div>
		  </header>
		  
		  <!-- Feeds panel -->
		  		  <div class="w3-panel" id="simplePicker">
			<div class="w3-row-padding w3-container" style="margin:0 -16px">
			  <div>
				<!-- PUT TABLE HERE -->
				<!-- PHP.MySQL.START -->
				<?php		
					require_once 'paginator.php';
					require_once 'db.php';
					
					$connPlat = $conn;
				 
					$limitPlat      = ( isset( $_GET['limit'] ) ) ? $_GET['limit'] : 25;
					$pagePlat       = ( isset( $_GET['page'] ) ) ? $_GET['page'] : 1;
					$linksPlat      = ( isset( $_GET['links'] ) ) ? $_GET['links'] : 7;
					$queryPlat      = "SELECT plateNumbers AS Plat FROM `platenumbers`";
					
					$PaginatorPlat  = new Paginator( $connPlat, $queryPlat);
					if ($PaginatorPlat->getNumRows() > 0){
						$resultsPlat    = $PaginatorPlat->getData( $pagePlat, $limitPlat );
					}				
				?>
				
				<form action="platnomor.php" method="post">
					<label for="newplate">Tambah nomor plat baru: </label>
					<input type="text" id="newplate" name="newplate">
					<input type="submit" value="Tambah">
				</form>
				<br>
				<table class="w3-table w3-card w3-bordered w3-striped w3-white w3-centered">
					<tr class='w3-teal'>
						<th>No</th>
						<th>Plat</th>
					</tr>
					<?php	if ($PaginatorPlat->getNumRows() > 0) {
								for( $i = 0; $i < count( $resultsPlat->data ); $i++ ) :
									echo "<tr>";
										echo "<td>".($i+1)."</td>";
										echo "<td>".$resultsPlat->data[$i]['Plat']."</td>";
									echo "</tr>";
								endfor;
							}
							else{
								echo "<tr><td colspan='2'>Kosong</td></tr>";
							}
					?>
				</table>
				<br>
				<?php 
					if ($PaginatorPlat->getNumRows() > 0){
						if ($PaginatorPlat->getLastPageNum() > 1){
							echo $PaginatorPlat->createLinks( $linksPlat, 'w3-bar-item w3-button w3-border' ); 
						}
					}
				?>
				<?php
					if( isset($_POST['newplate']) ){		
						// Create connection
						require_once 'db.php';
						
						$newplate = $_POST['newplate'];
						$sql = "INSERT INTO `platenumbers` (`id`, `plateNumbers`) VALUES (NULL, '$newplate')";
						if ($conn->query($sql) === TRUE) {
						  #echo "New record created successfully";
						} else {
						  echo "Error: " . $sql . "<br>" . $conn->error;
						}
						$conn->close();
						header("Refresh:0");
					}
				?>
				<!-- PHP.MySQL.END --> 
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
		</script>
	</body>
</html>