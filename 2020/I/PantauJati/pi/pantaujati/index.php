<!DOCTYPE html>
<html>
<head>
<title>Pantau Perkembangan Benih Jati</title>
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
		  }, 2000);
		  $.ajaxSetup({ cache: false });
		  });
	  });
</script>

<style>
html,body,h1,h2,h3,h4,h5,h6 {font-family: "Raleway", sans-serif}
</style>
</head>
<body class="w3-teal">

<!-- Top container -->
<div class="w3-bar w3-top w3-teal w3-large">
  <a href="../Pantau Jati"><span class="w3-bar-item w3- w3-xlarge fa fa-tree"></span></a>
</div>

<!-- !PAGE CONTENT! -->
<div class="w3-main w3-light-grey" style="margin-top:43px;">

  <!-- Header -->
  <header class="w3-container">
    <h5><b><i class="fa fa-dashboard"></i> Status</b></h5>
  </header>
  
  <!-- Feeds panel -->
  <div class="w3-panel" id="feeds">
    
  </div>
  <hr>
  
  <!-- Footer -->
  <footer class="w3-container w3-teal">
    <h4><strong>Pantau Perkembangan Benih Jati</strong></h4>
    <p>Powered by <a href="https://www.w3schools.com/w3css/default.asp" target="_blank">w3.css</a></p>
  </footer>

  <!-- End page content -->
</div>

</body>
</html>
