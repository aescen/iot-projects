<!DOCTYPE html>
<html>
<head>
<?php
if( session_id() == ''){
	session_start();
}
?>
<title>Sonar</title>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="shortcut icon" type="image/png" href="static/images/favicon.png"/>
<link rel="stylesheet" href="static/styles/w3.css">
<link rel="stylesheet" href="static/styles/css.css">
<link rel="stylesheet" href="static/styles/font-awesome.css">
<script src="static/scripts/jquery.min.js"></script>
<script src="static/scripts/canvasjs.min.js"></script>
<script languange="javascript">
	  $(document).ready(function() {
		
		$(document).ready(function() {
		  $("#btn").load("btn.php");
		  var refreshId = setInterval(function() {
		  
		  $("#btn").load('btn.php');
		  }, 2500);
		  $.ajaxSetup({ cache: false });
		  });
		
		$(document).ready(function() {
		  $("#feeds").load("feeds.php");
		  var refreshId = setInterval(function() {
		  
		  $("#feeds").load('feeds.php');
		  }, 2500);
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
		<h2>Sonar</h2>
	  </div>
  </header>
  <div class="w3-container w3-row">
	<!-- Feeds panel -->
	<div class="w3-row w3-margin-top" name="btn" id="btn" ></div>
	<div class="w3-row w3-margin-top" name="feeds" id="feeds" ></div>
	<!--- Alarm --->
	<audio id='audioAlarm' src='./static/sounds/alarm-buzzer-short.mp3' type='audio/mpeg' preload='auto'></audio>
  </div>
  <!-- End page content -->
</div>
</body>
<script>
	var audioAlarm = new Audio('./static/sounds/alarm-buzzer-short.mp3');
	function play(){
		audioAlarm.setAttribute('src', './static/sounds/alarm-buzzer-short.mp3');
		audioAlarm.autoplay = true;
		audioAlarm.loop = true;
		audioAlarm.play;
		console.log("Playing");
	}
	function stop(){
		audioAlarm.setAttribute('src', './static/sounds/alarm-buzzer-short.mp3');
		audioAlarm.autoplay = false;
		audioAlarm.loop = false;
		audioAlarm.pause;
		audioAlarm.currentTime = 0;
		console.log("Stopped");
	}
</script>
</html>