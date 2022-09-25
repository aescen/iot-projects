<!DOCTYPE html>
<html>
<head>
<title>Prediksi Hujan Asam</title>
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
</style>
</head>
<body class="w3-dark-grey">

<!-- Top container -->
<div class="w3-bar w3-top w3-dark-grey w3-large">
  <a href="../hujanasam"><span class="w3-bar-item w3- w3-xlarge fa fa-tree"></span></a>
</div>

<!-- !PAGE CONTENT! -->
<div class="w3-main w3-light-grey" style="margin-top:43px;">

  <!-- Header -->
  <header class="w3-container">
    <h5><b><i class="fa fa-dashboard"></i> Status</b></h5>
  </header>
  
  <!-- Feeds panel -->
  <div class="w3-container">
  <div id="feeds">
    
  </div></div>
  <hr>
  
  <!-- Footer -->
  <footer class="w3-container w3-dark-grey">
    <h4><strong>Hujan Asam</strong></h4>
    <p>Powered by <a href="https://www.w3schools.com/w3css/default.asp" target="_blank">w3.css</a></p>
  </footer>

  <!-- End page content -->
</div>

</body>
</html>