<!DOCTYPE html>
<html>
<title>Loker.io</title>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<!-- Credit:https://www.colourbox.com/vector/vector-icon-of-closed-lock-all-layers-are-grouped-vector-2459737 -->
<link rel="shortcut icon" type="image/png" href="static/images/favicon.png"/>
<link rel="stylesheet" href="static/styles/w3.css">
<link rel="stylesheet" href="static/styles/css.css">
<link rel="stylesheet" href="static/styles/font-awesome.css">

<style>
html,body,h1,h2,h3,h4,h5 {font-family: "Raleway", sans-serif}
</style>
<body class="w3-light-grey">

<!-- Top container -->
<div class="w3-bar w3-top w3-black w3-large" style="z-index:4">
  <button type="button" class="w3-bar-item w3-button w3-hide-large w3-hover-none w3-hover-text-light-grey" onclick="w3_open();"><i class="fa fa-bars"></i>  Menu</button>
  <span class="w3-bar-item w3-right w3-xlarge fa fa-cubes"></span>
</div>

<!-- Sidebar/menu -->
<nav class="w3-sidebar w3-collapse w3-white w3-animate-left" style="z-index:3;width:300px;" id="mySidebar"><br>
  <div class="w3-container w3-row">
    <div class="w3-col s4">
      <img src="static/images/avatar2.png" class="w3-circle w3-margin-center" style="width:46px">
    </div>
    <div class="w3-col s8 w3-bar">
      <span>Welcome, <strong>user</strong></span><br>
      <a href="#" class="w3-bar-item w3-button"><i class="fa fa-envelope"></i></a>
      <a href="#" class="w3-bar-item w3-button"><i class="fa fa-user"></i></a>
      <a href="#" class="w3-bar-item w3-button"><i class="fa fa-cog"></i></a>
    </div>
  </div>
  <hr>
  <div class="w3-container w3-black">
    <h5>Dashboard</h5>
  </div>
  <div class="w3-bar-block">
    <a href="#" class="w3-bar-item w3-button w3-padding-16 w3-hide-large w3-grey w3-hover-black" onclick="w3_close()" title="close menu"><i class="fa fa-remove fa-fw"></i>  Close Menu</a>
    <a href="index.php" class="w3-bar-item w3-button w3-padding"><i class="fa fa-dashboard fa-fw"></i>  Status</a>
    <a href="logs.php" class="w3-bar-item w3-button w3-padding w3-blue"><i class="fa fa-history fa-fw"></i>  Logs</a>
  </div>
</nav>


<!-- Overlay effect when opening sidebar on small screens -->
<div class="w3-overlay w3-hide-large w3-animate-opacity" onclick="w3_close()" style="cursor:pointer" title="close side menu" id="myOverlay"></div>

<!-- !PAGE CONTENT! -->
<div class="w3-main" style="margin-left:300px;margin-top:43px;">

  <!-- Header -->
  <header class="w3-container" style="padding-top:22px">
    <h5><b><i class="fa fa-history"></i> Logs</b></h5>
  </header>
  
  <!-- Feeds panel -->
  <div class="w3-panel" id="simplePicker">
    <div class="w3-row-padding" style="margin:0 -16px">
      <div>
        <!-- PUT TABLE HERE -->
		<!-- PHP.MySQL.START -->
		<?php		
			require_once 'paginator.php';
			include('config.php');
		 
			$limit      = ( isset( $_GET['limit'] ) ) ? $_GET['limit'] : 25;
			$page       = ( isset( $_GET['page'] ) ) ? $_GET['page'] : 1;
			$links      = ( isset( $_GET['links'] ) ) ? $_GET['links'] : 7;
			$query      = "SELECT * FROM `lokerLogs`";
		 
			$Paginator  = new Paginator( $conn, $query );
		 
			$results    = $Paginator->getData( $page, $limit );
		?>
		<table class="w3-table w3-striped w3-white w3-centered">
					<tr>
						<th>No</th>
						<th>Waktu</th>
						<th>SN</th>
						<th>SN terbaca</th>
						<th>Status alat</th>
						<th>No node</th>
						<th>Nilai sensor</th>
					</tr>
					<?php for( $i = 0; $i < count( $results->data ); $i++ ) : ?>
						<tr>
							<td><?php echo $results->data[$i]['id']; ?></td>
							<td><?php echo $results->data[$i]['stempelWaktu']; ?></td>
							<td><?php echo $results->data[$i]['noSeri']; ?></td>
							<td><?php echo $results->data[$i]['noSeriBaca']; ?></td>
							<td><?php echo $results->data[$i]['statusAlat']; ?></td>
							<td><?php echo $results->data[$i]['noNode']; ?></td>
							<td><?php echo $results->data[$i]['sensorLdr']; ?></td>
						</tr>
					<?php endfor; ?>
		</table>
		<?php echo $Paginator->createLinks( $links, 'w3-bar-item w3-button w3-border' ); ?>
		<!-- PHP.MySQL.END --> 
      </div>
    </div>
  </div>
  <hr>  

  <!-- Footer -->
  <footer class="w3-container w3-padding-16 w3-light-grey">
    <h4><strong>Smart Loker.io</strong></h4>
    <p>Powered by <a href="https://www.w3schools.com/w3css/default.asp" target="_blank">w3.css</a></p>
  </footer>

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
