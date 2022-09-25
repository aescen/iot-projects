<!-- PHP.MySQL.START -->
<?php
	@session_start();

	if(isset($_POST['valza'])){
		$NPK = $_POST['valza'];
    unset($_POST['valza']);
	
    if(isset($_POST['valponska'])){
      $ponska = $_POST['valponska'];
      unset($_POST['valponska']);
	
      if(isset($_POST['valkompos'])){
        $kompos = $_POST['valkompos'];
        unset($_POST['valkompos']);
        
        require_once 'db.php';
        $connForm = $conn;
        $sqlForm = "UPDATE `pupuk_warehouse` SET `za` = '" . $NPK . "', `ponska` = '" . $ponska . "', `kompos` = '" . $kompos . "' WHERE `pupuk_warehouse`.`id` = 1";
        
        if($connForm->query( $sqlForm ) === TRUE) {
          //echo "<script>alert('Data berhasil disimpan');</script>";
        } else {
          //echo "Data gagal disimpan!\n" . $sql . "\n" . $connForm->error;
          //echo "<script>alert('Data gagal disimpan!');</script>";
        }
      }
    }
  }
?>
<!DOCTYPE html>
<html>
	<head>
		<title>Gudang</title>
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
      <a href="warehouse.php" class="w3-bar-item w3-button w3-padding w3-light-blue"><i class="fa fa-info-circle fa-fw"></i>  Gudang</a>
      <a href="history.php" class="w3-bar-item w3-button w3-padding"><i class="fa fa-history fa-fw"></i>  History</a>
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
            
              <?php
                require_once 'db.php';
                $sqlPupuk = "SELECT * FROM `pupuk_warehouse`";
                $resultPupuk = $conn->query($sqlPupuk);
                
                if ( $resultPupuk->num_rows > 0 ) {
                  while( $rowPupuk = $resultPupuk->fetch_assoc() ) {
              ?>
              <!-- pupuk pupuk start -->
              <div class='w3-card-4 w3-white'>
                <div class='w3-large w3-indigo' style='vertical-align:middle; text-align:center; padding: 8px; padding-top: 0px;'>
                  <h1>Ketersediaan Pupuk</h1>
                  <div class='w3-large w3-white'>
                    <div class='w3-center' style='display: flex; flex-wrap: wrap; justify-content: space-evenly; align-items:ceter; vertical-align:middle; text-align:center; padding: 8px 0px;'>
                      <!-- pupuk 1 -->
                      <div class='w3-container w3-cell w3-cell-middle w3-mobile'>
                        <div class='w3-large w3-white'>
                          <table>
                            <tr>
                              <td><img src='static/images/fertilizer.png' alt='status' width='56px' height='56px' class='w3-circle'></td>
                            </tr>
                            <tr class='w3-white'>
                              <td>Pupuk ZA:<br><?php echo $rowPupuk['za'];?> sak</td>
                            </tr>
                          </table>
                        </div>
                      </div>
                      <!-- pupuk 2 -->
                      <div class='w3-container w3-cell w3-cell-middle w3-mobile'>
                        <div class='w3-large w3-white'>
                          <table>
                            <tr>
                              <td><img src='static/images/fertilizer.png' alt='status' width='56px' height='56px' class='w3-circle'></td>
                            </tr>
                            <tr class='w3-white'>
                              <td>Pupuk Ponska:<br><?php echo $rowPupuk['ponska'];?> sak</td>
                            </tr>
                          </table>
                        </div>
                      </div>
                      <!-- pupuk 3 -->
                      <div class='w3-container w3-cell w3-cell-middle w3-mobile'>
                        <div class='w3-large w3-white'>
                          <table>
                            <tr>
                              <td><img src='static/images/fertilizer.png' alt='status' width='56px' height='56px' class='w3-circle'></td>
                            </tr>
                            <tr class='w3-white'>
                              <td>Pupuk Kompos:<br><?php echo $rowPupuk['kompos'];?> sak</td>
                            </tr>
                          </table>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <?php
                  }
                }
              ?>
            
              <div class='w3-card-4 w3-white'>
                <div class='w3-large w3-indigo' style='vertical-align:middle; text-align:center; padding: 8px; padding-top: 0px;'>
                  <div class="w3-cell-row">
                    <h1>Perbarui Jumlah Pupuk</h1>
                    <div class="w3-left-align">
                      <form id='fertform' action="warehouse.php" method="post">
                        <?php
                          require_once 'db.php';
                          require_once 'inits.php';

                          $sqlWarehouse = "SELECT * FROM `pupuk_warehouse`";
                          $resultWarehouse = $conn->query($sqlWarehouse);

                          if ( $resultWarehouse->num_rows > 0 ) {
                            if( $rowWarehouse = $resultWarehouse->fetch_assoc() ) {
                              $arkey = array_keys($rowWarehouse);
                              unset($arkey[0]);
                              $arkey = $arkey;
                              unset($rowWarehouse['id']);
                              $rowWarehouse = $rowWarehouse;
                              foreach ($arkey as $k) {
                                echo "<div id='input" . $k . "' name='input" . $k . "'>";
                                echo "<label for='val" . $k . "'>" . strtoupper($k) . "</label>";
                                echo "<input class='w3-input' type='text' id='val" . $k . "' name='val" . $k . "' value='0'>";
                                echo "<br/></div>";
                              }
                            }
                          }
                        ?>
                        <input class="w3-btn w3-light-blue" type="submit" value="Simpan" onclick="return confirm('Apakah anda yakin untuk menyimpan?');">
                      </form>
                      <br>
                    </div>
                  </div>
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
      
		</script>
	</body>
</html>