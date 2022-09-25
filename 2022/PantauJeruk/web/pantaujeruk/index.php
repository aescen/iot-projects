<?php
	require_once 'inits.php';
?>
<!DOCTYPE html>
<html>
	<head>
		<title>Monitoring Kebun Jeruk</title>
		<meta charset="UTF-8">
		<meta name="viewport" content="width=device-width, initial-scale=1">
		<link rel="shortcut icon" type="image/png" href="static/images/favicon.png"/>
		<link rel="stylesheet" href="static/styles/w3.css">
		<link rel="stylesheet" href="static/styles/theme.css">
		<link rel="stylesheet" href="static/styles/raleway.css">
		<link rel="stylesheet" href="static/styles/font-awesome.min.css">
    <link href="../video/video-js.min.css" rel="stylesheet">
    <script src="../video/video.min.js"></script>
    <script src="../video/videojs-http-streaming.min.js"></script>
		<script src="static/scripts/jquery.min.js"></script>
		<script languange="javascript">
			  $(document).ready(function() {
				
				$(document).ready(function() {
				  $("#status").load("status.php");
				  var refreshId = setInterval(function() {
				  $("#status").load('status.php');
				  }, 2000);
				  $.ajaxSetup({ cache: false });
				  });
			  });
		</script>

		<style>
			html,body,h1,h2,h3,h4,h5,h6 {font-family: "Raleway", sans-serif}
      .center-video {
        position: relative;
        display: block !important;
        width: auto;
        margin: 0 auto;
        text-align: center;
      }
		</style>
	</head>
	<body class="w3-light-grey">
		<!-- Top container -->
		<div class="w3-bar w3-top w3-black w3-large" style="z-index:4">
		  <button type="button" class="w3-bar-item w3-button w3-hide-large w3-xlarge w3-hover-none w3-hover-text-light-grey" onclick="w3_open();"><i class="fa fa-bars"></i>  Menu</button>
      <span class="w3-bar-item w3-hide-small w3-hide-medium w3-xlarge">Monitoring Kebun Jeruk</span>
		  <span class="w3-bar-item w3-right w3-xlarge"><img src="static/images/favicon.png" alt="favicon" height="24px" width="24px"></span>
		</div>

		<!-- Sidebar/menu -->
		<nav class="w3-sidebar w3-bar-block w3-collapse w3-lime w3-animate-left" style="z-index:3;width:140px;" id="mySidebar"><br>
		  <div class="w3-container w3-lime">
        <h5>Menu</h5>
      </div>
      <div class="w3-bar-block" >
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
        <div class='w3-card-4'>
         <div class="w3-cell-row w3-lime">
          <div class="w3-container w3-cell">
            <h2>Status</h2>
            </div>
            <div class="w3-container w3-cell w3-right-align">
            <h2 id="clock">Clock</h2>
            </div>
          </div>
        </div>
		  </header>
		  
		  <!-- Feeds panel -->
		  <div class="w3-container" style="margin-left:8px;margin-right:8px;margin-top:20px;">
			<div class="w3-row-padding" style="margin:0 -16px">

        <div class='w3-card-4 w3-white'>
          <div class='w3-large w3-block w3-lime'>
            <div class='w3-padding'><strong>Video Camera<span></span></strong></div>
          </div>
            <div class='w3-cell-row'>
              <div class='w3-container w3-cell w3-cell-middle w3-center w3-mobile'>
                <video-js id="video-stream" width="640" height="360" class="video-js vjs-big-play-centered center-video" controls preload="auto">
                  <source
                   src="<?php echo "http://" . $_SERVER['SERVER_ADDR'] . "/video/live/index.m3u8";?>"
                   type="application/x-mpegURL">
                </video-js>
              </div>
            </div>
          </div>
        
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
		<script type="text/javascript">
			function updateClock ( ){
				var currentTime = new Date ();

				var currentYear = currentTime.getFullYear();
				var currentMonth = currentTime.getMonth();
				var currentDate = currentTime.getDate();
				var currentHours = currentTime.getHours ( );
				var currentMinutes = currentTime.getMinutes ( );
				var currentSeconds = currentTime.getSeconds ( );

				const monthNames = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun",
                            "Jul", "Agu", "Sep", "Okt", "Nov", "Des"];

				// Pad the minutes and seconds with leading zeros, if required
				currentMinutes = ( currentMinutes < 10 ? "0" : "" ) + currentMinutes;
				currentSeconds = ( currentSeconds < 10 ? "0" : "" ) + currentSeconds;
				var currentTimeString =  currentDate + " " + monthNames[currentMonth] + " "+ currentYear + " " + currentHours + ":" + currentMinutes + ":" + currentSeconds;

				document.getElementById("clock").firstChild.nodeValue = currentTimeString;
			}
			setInterval('updateClock()', 1000 );
      
      var player = videojs('video-stream', {
        liveui: false,
        autoplay: 'play',
        normalizeAutoplay: true,
      });
      
      // https://jsbin.com/quqodek/edit?html,js,output
      var bpb = player.getChild('bigPlayButton');
      if (bpb) {  
        bpb.hide();
        player.ready(function() {
          var promise = player.play();
          if (promise === undefined) {
            bpb.show();
          } else {
            promise.then(function() {
              bpb.show();
            }, function() {
              bpb.show();
            });
          }
        });
      }

      // https://blog.videojs.com/autoplay-best-practices-with-video-js/
      player.ready(function() {
        var promise = player.play();

        if (promise !== undefined) {
          promise.then(function() {
            console.log('autoplay success');
          }).catch(function(error) {
            console.log('autoplay prevented');
          });
        }
      });
			
		</script>
	</body>
</html>