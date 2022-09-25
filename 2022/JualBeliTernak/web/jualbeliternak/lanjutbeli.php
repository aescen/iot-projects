<?php
@session_start();
require_once 'db.php';


if (isset($_POST['itemId'])) {
  $itemId = $_POST["itemId"];

  $sql = "DELETE FROM `pantauternak` WHERE `pantauternak`.`id` = '" . $itemId . "'";
  if ($conn->query($sql) === TRUE) {
    // if (TRUE) {
    echo "<script>window.alert('Success: " . $itemId . "')</script>";
  } else {
    echo "<script>window.alert('Failed!')</script>";
  }

  unset($_POST['itemId']);
}
?>
<!DOCTYPE html>
<html lang="en">

<head>
  <title>Upload Sertifikat</title>
  <meta charset="UTF-8">
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <link rel="shortcut icon" type="image/png" href="./static/images/favicon.png" />
  <link rel="stylesheet" href="./static/styles/w3.css">
  <link rel="stylesheet" href="./static/styles/theme.css">
  <link rel="stylesheet" href="./static/styles/raleway.css">
  <link rel="stylesheet" href="./static/styles/font-awesome.min.css">
  <script src="./static/scripts/jquery.min.js"></script>
  <script src="./static/scripts/supportVhVw.js"></script>
  <script>
    const isLogin = window.localStorage.getItem('isLogin');
    if (isLogin !== 'true') {
      window.location.href = '/jualbeliternak/login.php';
    }
  </script>
  <script>
    const setItem = JSON.parse(window.sessionStorage.getItem('SET_ITEM'));
  </script>
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
      <h4>Menu</h4>
    </div>
    <div class="w3-bar-block">
      <a href="#" class="w3-bar-item w3-button w3-padding-16 w3-hide-large w3-grey w3-hover-black" onclick="w3_close()" title="Close"><i class="fa fa-remove fa-fw"></i>  Close</a>
      <a href="index.php" class="w3-bar-item w3-button w3-padding"><i class="fa fa-info-circle fa-fw"></i> Status</a>
      <a href="history.php" class="w3-bar-item w3-button w3-padding"><i class="fa fa-history fa-fw"></i> History</a>
    </div>
  </nav>

  <!-- Overlay effect when opening sidebar on small screens -->
  <div class="w3-overlay w3-hide-large w3-animate-opacity" onclick="w3_close()" style="cursor:pointer" title="close side menu" id="myOverlay"></div>

  <!-- !PAGE CONTENT! -->
  <div class="w3-main w3-light-grey" style="margin-left:140px;margin-top:43px;">

    <!-- Feeds panel -->
    <div class="w3-container" style="margin-left:8px;margin-right:8px;margin-top:20px; padding-top:22px">
      <div class="w3-mobile">
        <div class="w3-container w3-center" style="padding-top:22px; display: flex; align-items: center; justify-content: center;">
          <div class='w3-card' style="padding: 48px; padding-top: 24px; width: 40%;">
            <div class="w3-container w3-section w3-padding">
              <h2>Pembelian berhasil</h2>
              <img src="./static/images/sukses.png" alt="sukses" width="256px" />
            </div>
            <a href="/jualbeliternak/"><button class="w3-button w3-teal">Kembali ke home</button></a>
          </div>
        </div>
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