<!DOCTYPE html>
<html>
<head>
<title>Ruang Tahanan</title>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="shortcut icon" type="image/png" href="static/images/favicrot.png"/>
<link rel="stylesheet" href="static/styles/w3.css">
<link rel="stylesheet" href="static/styles/css.css">
<link rel="stylesheet" href="static/styles/font-awesome.css">
<script src="static/scripts/jquery.min.js"></script>
<script languange="javascript">
	  $(document).ready(function() {
		
		$(document).ready(function() {
		  $("#feeds").load("feeds.php");
		  var refreshId = setInterval(function() {
		  
		  $("#feeds").load('feeds.php');
		  }, 100);
		  $.ajaxSetup({ cache: false });
		  });
	  });
</script>
</head>
<style>
html,body,h1,h2,h3,h4,h5 {font-family: "Raleway", sans-serif}
</style>
<body class="w3-light-grey">
<!-- Top container -->
<div class="w3-bar w3-top w3-black w3-large" style="z-index:4"></div>
<!-- !PAGE CONTENT! -->
<div class="w3-main" style="margin-left:25px;">
  <!-- Header -->
  <header class="w3-container" style="padding-top:22px">
	<div class="w3-container w3-teal">
		<h2>Kamera Ruang Tahanan</h2>
	  </div>
  </header>
  <div class="w3-container w3-row">
	<!-- Feeds panel -->
	<div class="w3-row w3-margin-top" name="feeds" id="feeds"></div>
	<!-- Video -->
	
	  <div class="w3-row-padding w3-margin-top">
		<table><tr>
		  <td>
		  <div class="w3-card-4 w3-dark-grey" style="width:320px;height:320px">
			 <iframe src="http://192.168.100.10/video.cgi" style="width:320px;height:240px;" frameborder="0" scrolling="no" seamless="seamless" width="100%" height="100%" controls></iframe>
			  <div class="w3-container w3-center">
				<p>Ruang 1</p>
			  </div>
		  </div>
		  </td>	
		  <td>
		  <div class="w3-card-4 w3-dark-grey" style="width:320px;height:320px">
			  <iframe src="http://192.168.100.10/video.cgi" style="width:320px;height:240px;" frameborder="0" scrolling="no" seamless="seamless" width="100%" height="100%"></iframe>
			  <div class="w3-container w3-center">
				<p>Ruang 2</p>
			  </div>
		  </div>
		  </td>

		<td>
		  <div class="w3-card-4 w3-dark-grey" style="width:320px;height:320px">
			  <iframe src="http://192.168.100.20/video.cgi" style="width:320px;height:240px;" frameborder="0" scrolling="no" seamless="seamless" width="100%" height="100%"></iframe>
			  <div class="w3-container w3-center">
				<p>Ruang 3</p>
			  </div>
		  </div>
		  </td> 

		<td>
		  <div class="w3-card-4 w3-dark-grey" style="width:320px;height:320px">
			  <iframe src="http://192.168.100.20/video.cgi" style="width:320px;height:240px;" frameborder="0" scrolling="no" seamless="seamless" width="100%" height="100%"></iframe>
			  <div class="w3-container w3-center">
				<p>Ruang 4</p>
			  </div>
		  </div>
		  </td>
		</tr></table>
	  </div>
	
  </div>
  <!-- End page content -->
</div>
</body>
</html>