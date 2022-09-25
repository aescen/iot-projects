<?php
@session_start();
require_once 'db.php';

$connCert = $conn;

if (isset($_POST['upload'])) {
  $itemId = $_POST["itemId"];
  $filename = $_FILES["uploadfile"]["name"];
  $tempname = $_FILES["uploadfile"]["tmp_name"];
  $folder = "./imgs/" . $filename;

  $sql = "UPDATE `pantauternak` SET `img_cert` = '" . $filename . "' WHERE `pantauternak`.`id` = '" . $itemId . "'";
  if ($conn->query($sql) === TRUE) {
    if (move_uploaded_file($tempname, $folder)) {
      echo "<script>window.alert('File upload success.')</script>";
    } else {
      echo "<script>window.alert('File upload failed!')</script>";
    }
  } else {
    echo "<script>window.alert('File upload failed!')</script>";
  }

  unset($_POST['upload']);
}

$sqlCert = "SELECT `img_cert` FROM `pantauternak` WHERE `id` = '" . $itemId . "'";
$result = $conn->query($sqlCert);
if ($result->num_rows == 1) {
  if ($row = $result->fetch_assoc()) {
    $imgCert = $row['img_cert'];
  } else {
    unset($imgCert);
  }
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

    <!-- Header -->
    <header class="w3-container" style="padding-top:22px">
      <div class='w3-card-4'>
        <div class="w3-cell-row w3-teal">
          <div class="w3-container w3-cell">
            <h2>Upload Sertifikat</h2>
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

        <div class="w3-container">
          <div class='w3-cell-row'>
            <div class="w3-cell">
              <div class='w3-cell-row'>
                <div class="w3-container">
                  <div class='w3-card'>
                    <header class="w3-container w3-teal">
                      <h3>Data Kambing</h3>
                    </header>
                    <div class="w3-container w3-section w3-padding">
                      <div class="w3-center">
                        <img id="item-img" src="" alt="produk" width='480px'>
                      </div>
                      <div class='w3-cell-row w3-margin-top'>
                        <h4 class='w3-cell'>ID</h4>
                        <h4 id='item-id' class='w3-cell w3-right-align'>...</h4>
                      </div>
                      <div class='w3-cell-row'>
                        <h4 class='w3-cell'>Berat</h4>
                        <h4 id='item-berat' class='w3-cell w3-right-align'>...</h4>
                      </div>
                      <div class='w3-cell-row'>
                        <h4 class='w3-cell'>Suhu</h4>
                        <h4 id='item-suhu' class='w3-cell w3-right-align'>...</h4>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div class='w3-cell-row'>
                <div class="w3-container">
                  <div class='w3-card'>
                    <header class="w3-container w3-teal">
                      <h3>Sertifikat</h3>
                    </header>
                    <div class="w3-container w3-section w3-padding">
                      <div class="w3-center">
                        <img id="item-img-cert" src="" alt="produk" width='480px'>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

            </div>
            <div class="w3-cell">
              <div class="w3-container">
                <form id="formUpload" method="post" enctype="multipart/form-data" class="w3-container w3-center">
                  <div class='w3-card' style="padding: 6rem;">
                    <h4>Upload Sertifikat Baru</h4>
                    <input id="formItemId" type="text" name="itemId" value="" hidden />
                    <input type="file" name="uploadfile" value="" class="w3-input" />
                    <br />
                    <button id="submitForm" class="w3-btn w3-teal" type="submit" name="upload">Upload</button>
                  </div>
                </form>
              </div>
            </div>
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
    document.querySelector('#formItemId').src = `${setItem.id}`;
    document.querySelector('#item-img').src = `${setItem.imgPath}`;
    document.querySelector('#item-img-cert').src = `<?php echo isset($imgCert) ? './imgs/' . $imgCert : '${setItem.imgCertPath}'; ?>`;
    document.querySelector('#item-id').textContent = `${setItem.id}`;
    document.querySelector('#item-berat').textContent = `${setItem.berat}kg`;
    document.querySelector('#item-suhu').textContent = `${setItem.suhu}°C`;
  </script>
</body>

</html>