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
html,body,h1,h2,h3,h4,h5,h6 {font-family: "Raleway", sans-serif}
{ margin: 0; padding: 0; }
html { 
	background-color: blue;
	background: url('static/images/bg0.jpg') no-repeat center center fixed; 
	-webkit-background-size: cover;
	-moz-background-size: cover;
	-o-background-size: cover;
	background-size: cover;
	background-position:center;
	opacity: 0.90;
}
</style>


</head>
<body class="w3-teal">

<div class="w3-main w3-light-grey w3-padding-large">

  <header class="w3-container w3-padding-large">
    <h5><b><i class="fa fa-dashboard"></i> Status Area Parkir</b></h5>
  </header>
  
  <div class="w3-panel" id="feeds">
    
  </div>
  <hr>
  
  <div class="w3-display-bottomleft w3-padding-large">
    <b>Powered by <a href="https://www.w3schools.com/w3css/default.asp" target="_blank">w3.css</a></b>
  </div>
</div>

</body>
</html>
