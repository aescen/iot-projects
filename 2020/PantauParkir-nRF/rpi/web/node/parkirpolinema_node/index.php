<!DOCTYPE html>
<html>
<head>
<title>POLINEMA Parking Area</title>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="shortcut icon" type="image/png" href="static/images/favicon.png"/>
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
		  }, 1000);
		  $.ajaxSetup({ cache: false });
		  });
	  });
</script>

<style>
body,h1 {font-family: "Raleway", sans-serif}
body, html {height: 100%}
.bgimg {
	background-color: blue;
	background: url('static/images/bg1c-opacity.jpg') no-repeat center center fixed; 
	-webkit-background-size: cover;
	-moz-background-size: cover;
	-o-background-size: cover;
	background-size: cover;
	background-position:center;
	min-height: 100%;
}

</style>


</head>
<body>
<div class="bgimg w3-display-container w3-animate-opacity w3-text-black">
  <div class="w3-display-topleft w3-padding-large w3-xlarge">&nbsp;</div>
  <div class="w3-display-middle" id="feeds">
    <h1 class="w3-xxxlarge w3-center w3-text-black" style="text-shadow:2px 2px 0 #444">JUMLAH SLOT KENDARAAN</h1>
	<h1 class="w3-jumbo w3-center w3-wide w3-text-black" style="text-shadow:2px 2px 0 #444">null</h1>
    <hr class="w3-border-black" style="margin:auto;width:75%">
	<h1 class="w3-jumbo w3-center w3-text-black" style="text-shadow:2px 2px 0 #444">Status</h1>
    <h1 class="w3-xxxlarge w3-center w3-text-black" style="text-shadow:2px 2px 0 #444">null</h1>
  </div>
  <div class="w3-display-bottomleft w3-padding-large">
    <b>Powered by <a href="https://www.w3schools.com/w3css/default.asp" target="_blank">w3.css</a></b>
  </div>
</div>

</body>
</html>
