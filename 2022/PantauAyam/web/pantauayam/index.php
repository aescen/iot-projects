<?php
	require_once 'inits.php';
?>
<!DOCTYPE html>
<html>
	<head>
		<title>Pantau Ayam</title>
		<meta charset="UTF-8">
		<meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="shortcut icon" href="favicon.ico"/>
		<link rel="stylesheet" href="static/styles/w3.css">
		<link rel="stylesheet" href="static/styles/theme.css">
		<link rel="stylesheet" href="static/styles/font-awesome.min.css">
		<script src="static/scripts/jquery.min.js"></script>
        <script src="static/scripts/update-clock.js"></script>
		<script languange="javascript">
			  $(document).ready(function() {
				
				$(document).ready(function() {
				  $("#status").load("status.php");
				  var refreshId = setInterval(function() {
				  $("#status").load('status.php');
				  }, 1000);
				  $.ajaxSetup({ cache: false });
				  });
			  });
		</script>

		<style>
			html,body,h1,h2,h3,h4,h5,h6 {font-family: "Raleway", sans-serif}
		</style>
	</head>
	<body class="w3-light-grey">
		<!-- Top container -->
		<div class="w3-bar w3-top w3-white w3-large" style="z-index:4">
		  <button type="button" class="w3-bar-item w3-button w3-hide-large w3-hover-none w3-hover-text-light-grey" onclick="w3_open();"><i class="fa fa-bars"></i>  Menu</button>
          <span class="w3-bar-item w3-hide-small w3-left w3-xlarge">Pantau Ayam</span>
		  <span class="w3-bar-item w3-right w3-xlarge"><img src="favicon.ico" alt="favicon" height="24px" width="24px"></span>
		</div>

		<!-- Sidebar/menu -->
		<nav class="w3-sidebar w3-bar-block w3-collapse w3-white w3-animate-left" style="z-index:3;width:140px;" id="mySidebar"><br>
		  <div class="w3-container w3-khaki">
			<h5>Menu</h5>
		  </div>
		  <div class="w3-bar-block">
			<a href="#" class="w3-bar-item w3-button w3-padding-16 w3-hide-large w3-grey w3-hover-black" onclick="w3_close()" title="Close"><i class="fa fa-remove fa-fw"></i>  Close</a>
			<a href="index.php" class="w3-bar-item w3-button w3-padding w3-grey"><i class="fa fa-info-circle fa-fw"></i><strong>  Status</strong></a>
			<a href="history.php" class="w3-bar-item w3-button w3-padding"><i class="fa fa-history fa-fw"></i>  History</a>
		  </div>
		</nav>

		<!-- Overlay effect when opening sidebar on small screens -->
		<div class="w3-overlay w3-hide-large w3-animate-opacity" onclick="w3_close()" style="cursor:pointer" title="close side menu" id="myOverlay"></div>

		<!-- !PAGE CONTENT! -->
		<div class="w3-main w3-light-grey" style="margin-left:140px;margin-top:43px;">

		  <!-- Header -->
		  <header class="w3-container" style="padding-top:22px">
			 <div class="w3-cell-row w3-khaki">
			  <div class="w3-container w3-cell">
				<h2>Status</h2>
			  </div>
			  <div class="w3-container w3-cell w3-right-align">
				<h2 id="clock">Clock</h2>
			  </div>
			</div>
		  </header>
		  
		  <!-- Feeds panel -->
		  <div class="w3-container" style="margin-left:8px;margin-right:8px;margin-top:20px;">
			<div class="w3-row-padding" style="margin:0 -16px">
				<div id="status"></div>
			</div>
		  </div>
		  <hr>

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