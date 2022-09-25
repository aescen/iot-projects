<?php
@session_start();

?>
<!DOCTYPE html>
<html>

<head>
  <title>Jual Beli Ternak</title>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="shortcut icon" type="image/png" href="./static/images/favicon.png" />
  <link rel="stylesheet" href="./static/styles/w3.css">
  <link rel="stylesheet" href="./static/styles/theme.css">
  <link rel="stylesheet" href="./static/styles/raleway.css">
  <link rel="stylesheet" href="./static/styles/font-awesome.min.css">
  <script src="./static/scripts/jquery.min.js"></script>
  <script src="./static/scripts/supportVhVw.js"></script>
  <script>
    <?php
    if ($_POST['logout']) {
      unset($_POST['logout']);
      unset($_SESSION['username']);
      echo '
					window.localStorage.removeItem("isLogin");
					window.location.href = "/jualbeliternak/login.php";
				';
    }
    ?>
  </script>
  <script>
    const isLogin = window.localStorage.getItem('isLogin');
    if (isLogin !== 'true') {
      window.location.href = '/jualbeliternak/login.php';
    }
  </script>
  <script>
    window.sessionStorage.removeItem('SET_ITEM');
    window.sessionStorage.setItem('dataChange', true);
    window.sessionStorage.setItem('dbData', JSON.stringify([]));

    $(document).ready(function() {
      $("#status").load("status.php");
      $("#statusCheck").load("./statuscheck.php");
      $.ajaxSetup({
        cache: false
      });

      var refreshStatusId = setInterval(function() {
        var dataChange = JSON.parse(window.sessionStorage.getItem('dataChange'));
        if (dataChange === true) {
          $("#status").load("./status.php");
          window.sessionStorage.setItem('dataChange', false);
        }
      }, 1111);

      var checkDataChangeId = setInterval(function() {
        $("#statusCheck").load("./statuscheck.php");
      }, 1111);
    });
  </script>

  <style>
    html,
    body,
    h1,
    h2,
    h3,
    h4,
    h5,
    h6 {
      font-family: "Raleway", sans-serif
    }

    #divLargerImage {
      display: none;
      width: 640;
      height: 480;
      position: absolute;
      top: 18.75%;
      left: 26.5739%;
      z-index: 99;
    }

    #divOverlay {
      display: none;
      position: absolute;
      top: 0;
      left: 0;
      background-color: #CCC;
      opacity: 0.5;
      width: 100%;
      height: 100%;
      z-index: 98;
    }
  </style>
</head>

<body class="w3-light-grey">
  <!-- Top container -->
  <div class="w3-bar w3-top w3-white w3-large" style="z-index:4">
    <button type="button" class="w3-bar-item w3-button w3-hide-large w3-xlarge w3-hover-none w3-hover-text-light-grey" onclick="w3_open();"><i class="fa fa-bars"></i>  Menu</button>
    <span class="w3-bar-item w3-hide-small w3-hide-medium w3-xlarge">Jual Beli Ternak</span>
    <span class="w3-bar-item w3-right w3-xlarge">
      <?php
      if (isset($_SESSION['username'])) {
        echo '<span>
                <a href="#" style="cursor: pointer; text-decoration: none;">
                  <i class="fa fa-user-circle-o w3-text-teal">&nbsp;
                    <span style="font-size: 18px!important;">Hi, ' . $_SESSION['username'] . '!</span>
                  </i>
                </a>
              </span>
              <span>
                <form method="post" style="display: inline;">
									<button type="submit" class="w3-margin-left w3-button w3-medium w3-teal" name="logout" value="logout">
										<b>Logout</b>
									</button>
								</form>
              </span>';
      } else {
        echo '
				<span>
          <a class="w3-text-teal" style="text-decoration: none; cursor: pointer;" href="./login.php"><b>Login</b></a>
        </span>
				<span>
          <button class="w3-margin-left w3-button w3-medium w3-teal">
            <a style="text-decoration: none; cursor: pointer;" href="./register.php"><b>Register</b></a>
          </button>
        </span>';
      }
      ?>
    </span>
  </div>

  <!-- Sidebar/menu -->
  <nav class="w3-sidebar w3-bar-block w3-collapse w3-teal w3-animate-left" style="z-index:3;width:140px;" id="mySidebar"><br>
    <div class="w3-container w3-teal">
      <h5>Menu</h5>
    </div>
    <div class="w3-bar-block">
      <a href="#" class="w3-bar-item w3-button w3-padding-16 w3-hide-large w3-grey w3-hover-black" onclick="w3_close()" title="Close"><i class="fa fa-remove fa-fw"></i>  Close</a>
      <a href="index.php" class="w3-bar-item w3-button w3-padding w3-grey"><i class="fa fa-info-circle fa-fw"></i><strong> Status</strong></a>
      <a href="history.php" class="w3-bar-item w3-button w3-padding"><i class="fa fa-history fa-fw"></i> History</a>
    </div>
  </nav>

  <!-- Overlay effect when opening sidebar on small screens -->
  <div class="w3-overlay w3-hide-large w3-animate-opacity" onclick="w3_close()" style="cursor:pointer" title="close side menu" id="myOverlay"></div>

  <!-- !PAGE CONTENT! -->
  <div class="w3-main w3-light-grey" style="margin-left:140px;margin-top:43px;">

    <!-- Header -->
    <header class="w3-container" style="padding-top:22px">
      <div class='w3-card-4'>
        <div class="w3-cell-row w3-teal">
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
        <div id="status"></div>
        <div id="statusCheck"></div>
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
  <script>
    function updateClock() {
      var currentTime = new Date();

      var currentYear = currentTime.getFullYear();
      var currentMonth = currentTime.getMonth();
      var currentDate = currentTime.getDate();
      var currentHours = currentTime.getHours();
      var currentMinutes = currentTime.getMinutes();
      var currentSeconds = currentTime.getSeconds();

      const monthNames = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun",
        "Jul", "Agu", "Sep", "Okt", "Nov", "Des"
      ];

      // Pad the minutes and seconds with leading zeros, if required
      currentMinutes = (currentMinutes < 10 ? "0" : "") + currentMinutes;
      currentSeconds = (currentSeconds < 10 ? "0" : "") + currentSeconds;
      var currentTimeString = currentDate + " " + monthNames[currentMonth] + " " + currentYear + " " + currentHours + ":" + currentMinutes + ":" + currentSeconds;

      document.getElementById("clock").firstChild.nodeValue = currentTimeString;
    }
    setInterval('updateClock()', 1000);
  </script>
  <script>
    function setItem(id, berat, suhu, imgPath, imgCertPath, harga) {
      const item = {
        id,
        berat,
        suhu,
        imgPath,
        imgCertPath,
        harga
      };
      window.sessionStorage.setItem('SET_ITEM', JSON.stringify(item));
      window.location.href = './pembelian.php';
    }
  </script>
</body>

</html>