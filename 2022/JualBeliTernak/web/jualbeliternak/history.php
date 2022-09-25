<!-- PHP.MySQL.START -->
<?php
@session_start();

if (isset($_POST['resetDate'])) {
  unset($_SESSION['dateselect']);
  unset($_POST['dateselect']);
  unset($dateSelect);
  unset($_SESSION['ymd']);
}
if (isset($_POST['dateselect'])) {
  $_SESSION['dateselect'] = $_POST['dateselect'];
}
if (isset($_SESSION['dateselect'])) {
  $dateSelect = $_SESSION['dateselect'];
} else {
  unset($dateSelect);
  unset($resultsHistory);
}
require_once 'paginator.php';
require_once 'db.php';

$connHistory       = $conn;

$limitHistory      = (isset($_GET['limit'])) ? $_GET['limit'] : 25;
$pageHistory       = (isset($_GET['page'])) ? $_GET['page'] : 1;
$linksHistory      = (isset($_GET['links'])) ? $_GET['links'] : 7;
if (isset($dateSelect)) {
  $startTime = $dateSelect . " 00:00:00.000000";
  $endTime = $dateSelect . " 23:59:59.999999";
  $queryHistory      = "SELECT * FROM `pantauternak_log` WHERE `time_stamp` BETWEEN '$startTime' AND '$endTime' ORDER BY `pantauternak_log`.`time_stamp` DESC";

  $ymd = date("Y-m-d", strtotime($dateSelect));
  $_SESSION['ymd'] = $ymd;
} else {
  $queryHistory      = "SELECT * FROM `pantauternak_log` ORDER BY `pantauternak_log`.`time_stamp` DESC";
}
$paginatorHistory  = new Paginator($connHistory, $queryHistory);
if ($paginatorHistory->getNumRows() > 0) {
  $resultsHistory    = $paginatorHistory->getData($pageHistory, $limitHistory);
}
?>
<!DOCTYPE html>
<html>

<head>
  <title>Jual Beli Ternak</title>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="shortcut icon" type="image/png" href="static/images/favicon.png" />
  <link rel="stylesheet" href="static/styles/w3.css">
  <link rel="stylesheet" href="static/styles/theme.css">
  <link rel="stylesheet" href="static/styles/raleway.css">
  <link rel="stylesheet" href="static/styles/font-awesome.min.css">
  <script src="static/scripts/jquery.min.js"></script>
  <script src="static/scripts/supportVhVw.js"></script>
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
        echo
        '
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
      <a href="index.php" class="w3-bar-item w3-button w3-padding"><i class="fa fa-info-circle fa-fw"></i> Status</a>
      <a href="history.php" class="w3-bar-item w3-button w3-padding w3-grey"><i class="fa fa-history fa-fw"></i><strong> History</strong></a>
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
            <h2>History</h2>
          </div>
        </div>
      </div>
    </header>

    <!-- Feeds panel -->
    <div class="w3-panel w3-center">
      <div class="w3-row w3-container" style="margin:0 -16px">
        <div class="w3-cell-row">
          <div class="w3-left-align">
            <form action="history.php" method="post" onsubmit="return valDate()" required>
              <label for="dateselect">Set tanggal: </label>
              <input type="date" id="dateselect" name="dateselect" min="2019-01-01" max="<?php echo date(" Y-m-d"); ?>" value="<?php echo (isset($_SESSION['ymd']) ? $_SESSION['ymd'] : ""); ?>">
              <input type="submit" value="Pilih">
              <input type="submit" value="Reset" id="resetDate" name="resetDate">
            </form>
          </div>
        </div>
        <div class="w3-cell-row w3-margin-top">
          <table class="w3-table-all w3-centered w3-card-4 w3-white">
            <tr class='w3-teal'>
              <td rowspan="2" style='vertical-align: middle;'>ID</td>
              <td rowspan="2" style='vertical-align: middle;'>Berat</td>
              <td rowspan="2" style='vertical-align: middle;'>Suhu</td>
              <td rowspan="2" style='vertical-align: middle;'>Waktu</td>
              <td rowspan="2" style='vertical-align: middle;'>Harga</td>
              <td colspan="2" style='vertical-align: middle;'>Gambar</td>
            </tr>
            <tr class='w3-teal'>
              <td style='vertical-align: middle;'>Kambing</td>
              <td style='vertical-align: middle;'>Sertifikat</td>
            </tr>
            <?php
            if ($paginatorHistory->getNumRows() > 0) {
              for ($i = 0; $i < count($resultsHistory->data); $i++) :
                echo "<tr>";
                echo "<td style='vertical-align: middle;'>" . ($i + 1) . "</td>";
                echo "<td style='vertical-align: middle;'>" . $resultsHistory->data[$i]['id'] . "</td>";
                echo "<td style='vertical-align: middle;'>" . $resultsHistory->data[$i]['berat'] . "kg</td>";
                echo "<td style='vertical-align: middle;'>" . $resultsHistory->data[$i]['suhu'] . "&deg;C</td>";
                echo "<td style='vertical-align: middle;'>" . $resultsHistory->data[$i]['time_stamp'] . "</td>";
                echo "<td style='vertical-align: middle;'><a href=#'><img id='img-" . $resultsHistory->data[$i]['img_path'] .
                  "'src='./imgs/" . $resultsHistory->data[$i]['img_path'] .
                  "' alt='img-" . $resultsHistory->data[$i]['img_path'] .
                  "' width='90px' height='68px' class='w3-center w3-middle w3-padding'></a></td>";
                echo "<td style='vertical-align: middle;'><a href=#'><img id='img-" . $resultsHistory->data[$i]['img_cert'] .
                  "'src='./imgs/" . $resultsHistory->data[$i]['img_cert'] .
                  "' alt='img-" . $resultsHistory->data[$i]['img_cert'] .
                  "' width='90px' height='68px' class='w3-center w3-middle w3-padding'></a></td>";
                echo "</tr>";
              endfor;
            } else {
              echo "<tr><td colspan='7'>Kosong</td></tr>";
            }
            ?>
          </table>
          <br>
          <?php
          if ($paginatorHistory->getNumRows() > 0) {
            if ($paginatorHistory->getLastPageNum() > 1) {
              echo $paginatorHistory->createLinks($linksHistory, 'w3-bar-item w3-button w3-border');
            }
          }
          ?>
        </div>
        <div id="divLargerImage"></div>
        <div id="divOverlay"></div>
      </div>
    </div>
    <!-- End page content -->
  </div>
  <script>
    // Get the Sidebar
    let mySidebar = document.getElementById("mySidebar");

    // Get the DIV with overlay effect
    let overlayBg = document.getElementById("myOverlay");

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

    function valDate() {
      let valueDate = document.getElementById('dateselect').value;
      if (!Date.parse(valueDate)) {
        alert('Date is invalid or empty!');
        return false;
      }
    }
  </script>
  <script>
    var thw = new SupportVhVw();
    $('a img').click(function() {
      var $img = $(this);
      $('#divLargerImage').html($img.clone().height(480).width(640)).add($('#divOverlay')).fadeIn();
    });

    $('#divLargerImage').add($('#divOverlay')).click(function() {
      $('#divLargerImage').add($('#divOverlay')).fadeOut(function() {
        $('#divLargerImage').empty();
      });
    });
  </script>
</body>

</html>