<!-- PHP.MySQL.START -->
<?php
	@session_start();

	if(isset($_POST['pupukza'])){
		$pupukza = intval($_POST['pupukza']);
    unset($_POST['pupukza']);
	
    if(isset($_POST['pupukponska'])){
      $pupukponska = intval($_POST['pupukponska']);
      unset($_POST['pupukponska']);
      
      if(isset($_POST['pupukkompos'])){
        $pupukkompos = intval($_POST['pupukkompos']);
        unset($_POST['pupukkompos']);
        
        if(isset($_POST['fertaddress'])){
          $fertaddress = $_POST['fertaddress'];
          unset($_POST['fertaddress']);
          
          $total = $pupukza + $pupukponska + $pupukkompos;
          
          require_once 'db.php';
          $sqlForm = "INSERT INTO `pupuk_history` (`id`, `za`, `ponska`, `kompos`, `total`, `address`, `time_stamp`) ";
          $sqlForm .= "VALUES (NULL, '" . $pupukza . "', '" . $pupukponska . "', '" . $pupukkompos . "', '" . $total . "', '" . $fertaddress . "', current_timestamp())";
          
          $connForm = $conn;
          if($connForm->query( $sqlForm ) === TRUE) {
            //echo "<script>alert('Data berhasil disimpan');</script>";
            $connWarehouse = $conn;
            $sqlWarehouse = "SELECT * FROM `pupuk_warehouse`";
            $resultWarehouse = $connWarehouse->query($sqlWarehouse);
            $whza = 0;
            $whponska = 0;
            $whkompos = 0;
            if ( $resultWarehouse->num_rows > 0 ) {
              if( $row = $resultWarehouse->fetch_assoc() ) {
                $whza = abs(intval($row['za']) - $pupukza);
                $whponska = abs(intval($row['ponska']) - $pupukponska);
                $whkompos = abs(intval($row['kompos']) - $pupukkompos);
                
                $sqlUpdate = "UPDATE `pupuk_warehouse` SET `za` = '".$whza."', `ponska` = '".$whponska."', `kompos` = '".$whkompos."' WHERE `pupuk_warehouse`.`id` = '1'";
                $connWhUpdate = $conn;
                if($connWhUpdate->query( $sqlUpdate ) === TRUE) {
                  //echo "<script>console.log('Data berhasil disimpan!', '".$whza.":".$whponska.":".$whkompos."');</script>";
                } else {
                  echo "Data gagal disimpan!\n" . "\n" . $connWhUpdate->error;
                }
              }
            }
          } else {
            echo "Data gagal disimpan!\n" . "\n" . $connForm->error;
            //echo "<script>alert('Data gagal disimpan!');</script>";
          }
        }
      }
    }
  }
	
  require_once 'paginator.php';
	require_once 'db.php';
  $connHistory = $conn;
  if(isset($_POST['resetDate'])){
		unset($_SESSION['dateselect']);
		unset($_POST['dateselect']);
		unset($dateSelect);
		unset($_SESSION['ymd']);
	}
	if(isset($_POST['dateselect'])){
		$_SESSION['dateselect'] = $_POST['dateselect'];
	}
	if(isset($_SESSION['dateselect'])){
		$dateSelect = $_SESSION['dateselect'];
	}
	else{
		unset($dateSelect);
		unset($resultsHistory);
	}
 
	$limitHistory      = ( isset( $_GET['limit'] ) ) ? $_GET['limit'] : 25;
	$pageHistory       = ( isset( $_GET['page'] ) ) ? $_GET['page'] : 1;
	$linksHistory      = ( isset( $_GET['links'] ) ) ? $_GET['links'] : 7;
	if( isset($dateSelect) ){
		$startTime = $dateSelect . " 00:00:00.000000";
		$endTime = $dateSelect . " 23:59:59.999999";
		$queryHistory      = "SELECT * FROM `pupuk_history` WHERE `time_stamp` BETWEEN '$startTime' AND '$endTime' ORDER BY `pupuk_history`.`time_stamp` DESC";
		
		$ymd = date("Y-m-d", strtotime($dateSelect));
		$_SESSION['ymd'] = $ymd;
		
	} else{
		$queryHistory      = "SELECT * FROM `pupuk_history` ORDER BY `pupuk_history`.`time_stamp` DESC";
	}
	$PaginatorHistory  = new Paginator( $connHistory, $queryHistory);
	if ($PaginatorHistory->getNumRows() > 0){
		$resultsHistory    = $PaginatorHistory->getData( $pageHistory, $limitHistory );
	}
?>
<!DOCTYPE html>
<html>
	<head>
		<title>Riwayat Distribusi</title>
		<meta charset="UTF-8">
		<meta name="viewport" content="width=device-width, initial-scale=1">
		<link rel="shortcut icon" type="image/png" href="static/images/favicon.png"/>
		<link rel="stylesheet" href="static/styles/w3.css">
		<link rel="stylesheet" href="static/styles/theme.css">
		<link rel="stylesheet" href="static/styles/raleway.css">
		<link rel="stylesheet" href="static/styles/font-awesome.min.css">
		<script src="static/scripts/jquery.min.js"></script>
		<style>
			html,body,h1,h2,h3,h4,h5,h6 {font-family: "Raleway", sans-serif}
      tr:nth-child(even) {
        background-color: #DEE8F9;
      }
		</style>
	</head>
	<body class="w3-light-grey">
		<!-- Top container -->
		<div class="w3-bar w3-top w3-white w3-large" style="z-index:4">
		  <button type="button" class="w3-bar-item w3-button w3-hide-large w3-xlarge w3-hover-none w3-hover-text-light-grey" onclick="w3_open();"><i class="fa fa-bars"></i>  Menu</button>
      <span class="w3-bar-item w3-hide-small w3-hide-medium w3-xlarge">DASHBOARD</span>
		  <a href="#"><span class="w3-hover-grayscale w3-bar-item w3-right w3-medium" style="margin-top:8px;color:#3f51b5;">Hello, admin</span></a>
		</div>

		<!-- Sidebar/menu -->
		<nav class="w3-sidebar w3-bar-block w3-collapse w3-indigo w3-animate-left" style="z-index:3;width:140px;" id="mySidebar"><br>
		  <div class="w3-container w3-indigo">
			<h5>Menu</h5>
		  </div>
		  <div class="w3-bar-block">
			<a href="#" class="w3-bar-item w3-button w3-padding-16 w3-hide-large w3-grey w3-hover-black" onclick="w3_close()" title="Close"><i class="fa fa-remove fa-fw"></i>  Close</a>
			<a href="index.php" class="w3-bar-item w3-button w3-padding"><i class="fa fa-info-circle fa-fw"></i>  Status</a>
      <a href="warehouse.php" class="w3-bar-item w3-button w3-padding"><i class="fa fa-info-circle fa-fw"></i>  Gudang</a>
      <a href="history.php" class="w3-bar-item w3-button w3-padding w3-light-blue"><i class="fa fa-history fa-fw"></i>  Riwayat</a>
		  </div>
		</nav>

		<!-- Overlay effect when opening sidebar on small screens -->
		<div class="w3-overlay w3-hide-large w3-animate-opacity" onclick="w3_close()" style="cursor:pointer" title="close side menu" id="myOverlay"></div>

		<!-- !PAGE CONTENT! -->
		<div class="w3-main w3-light-grey" style="margin-left:140px;margin-top:43px;">
		  
		  <!-- Feeds panel -->
		  <div class="w3-panel">
        <div class="w3-row-padding w3-container" style="margin:0 -16px;margin-top:32px;">
          <div class='w3-cell-row w3-center'>  
            <div class='w3-container w3-cell w3-cell-top w3-mobile'>
              <div class='w3-card-4 w3-white'>
                <div class='w3-large w3-indigo' style='vertical-align:middle; text-align:center; padding: 8px; padding-top: 0px;'>
                  
                  <div class="w3-cell-row">
                    <div class="w3-left-align">
                      <h1>Tambah Pengiriman</h1>
                      <form id='fertform' action="history.php" method="post">
                        <div class="w3-row" style='display: flex; justify-content: space-evenly;'>
                          <div class="w3-cell" style='margin: auto'>
                            <label for="pupukza">Pupuk ZA: </label>
                            <input class="w3-input" type="number" id="pupukza" name="pupukza" value=0 required>
                          </div>
                          <div class="w3-cell" style='margin: auto'>
                            <label for="pupukponska">Pupuk Ponska: </label>
                            <input class="w3-input" type="number" id="pupukponska" name="pupukponska" value=0 required>
                          </div>
                          <div class="w3-cell" style='margin: auto'>
                            <label for="pupukkompos">Pupuk Kompos: </label>
                            <input class="w3-input" type="number" id="pupukkompos" name="pupukkompos" value=0 required>
                          </div>
                        </div>
                        <br/>
                        <label for="fertaddress">Alamat: </label>
                        <input class="w3-input" type="text" id="fertaddress" name="fertaddress" required>
                        <br>
                        <input class="w3-btn w3-light-blue" type="submit" value="Simpan" onclick="return confirm('Apakah anda yakin untuk menyimpan?');">
                        <input class="w3-btn w3-light-blue" type="submit" value="Reset" id="resetform" name="resetform" onclick="resetForm(this);">
                      </form>
                    </div>
                  </div>
                </div>
              </div>
              <br/>
              <div class='w3-card-4 w3-white'>
                <div class='w3-large w3-indigo' style='vertical-align:middle; text-align:center; padding: 8px; padding-top: 0px;'>
                  <div class="w3-cell-row">
                    <div class="w3-left-align">
                      <h1>Set Tanggal Riwayat</h1>
                      <form id='dateform' action="history.php" method="post">
                        <label for="dateselect">Set tanggal: </label>
                        <div class="w3-cell">
                          <input class="w3-input w3-animate-input" type="date" id="dateselect" name="dateselect" min="2022-01-01" max="<?php echo date("Y-m-d"); ?>" value="<?php echo (isset($_SESSION['ymd']) ? $_SESSION['ymd'] : ""); ?>">
                        </div>
                        <br>
                        <input class="w3-btn w3-light-blue" type="submit" value="Pilih" onclick="return valDate();">
                        <input class="w3-btn w3-light-blue" type="submit" value="Reset" id="resetDate" name="resetDate" onclick="resetForm(this);">
                      </form>
                    </div>
                  </div>
                  <br>
                  <!-- PUT TABLE HERE -->
                  <table class="w3-table w3-centered w3-white w3-bordered">
                        <thead>
                        <tr class='w3-indigo'>
                          <th rowspan='2' style="vertical-align: middle;">No</th>
                          <th rowspan='2' style="vertical-align: middle;">Timestamp</th>
                          <th colspan='3' style="vertical-align: middle;">Pupuk</th>
                          <th rowspan='2' style="vertical-align: middle;">Jumlah</th>
                          <th rowspan='2' style="vertical-align: middle;">Alamat</th>
                        </tr>
                        <tr class='w3-indigo'>
                          <th style="vertical-align: middle;">ZA</th>
                          <th style="vertical-align: middle;">Ponska</th>
                          <th style="vertical-align: middle;">Kompos</th>
                        </tr>
                        </thead>
                        <?php	
                          if ($PaginatorHistory->getNumRows() > 0) {
                            for( $i = 0; $i < count( $resultsHistory->data ); $i++ ) :
                              echo "<tr>";
                                echo "<td>".($i+1)."</td>";
                                echo "<td>".$resultsHistory->data[$i]['time_stamp']."</td>";
                                echo "<td>".$resultsHistory->data[$i]['za']."</td>";
                                echo "<td>".$resultsHistory->data[$i]['ponska']."</td>";
                                echo "<td>".$resultsHistory->data[$i]['kompos']."</td>";
                                echo "<td>".$resultsHistory->data[$i]['total']."</td>";
                                echo "<td>".$resultsHistory->data[$i]['address']."</td>";
                              echo "</tr>";
                            endfor;
                          }
                          else{
                            echo "<tr><td colspan='7'>Kosong</td></tr>";
                          }
                      ?>
                  </table>
                  <br>
                  <?php
                    if ($PaginatorHistory->getNumRows() > 0){
                      if ($PaginatorHistory->getLastPageNum() > 1){
                        echo $PaginatorHistory->createLinks( $linksHistory, 'w3-bar-item w3-button w3-border' );
                      }
                    }
                  ?>
                </div>
              </div>
            </div>
          </div>
        </div>
		  </div>
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
      
      function valDate(){
				let valueDate = document.getElementById('dateselect').value;
				if(!Date.parse(valueDate)){
					alert('Date is invalid or empty!');
					return false;
				}
			}
      
      function resetForm(form){
        form.reset();
      }
		</script>
	</body>
</html>