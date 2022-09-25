<!-- PHP.MySQL.START -->
<?php
	@session_start();

	require_once 'db.php';
  $connForm = $conn;
  
  // Performing SQL query
  $sql = "SELECT
            `keranjang_produk`.`nama`,
            `keranjang_produk`.`deskripsi`,
            `keranjang_produk`.`harga`,
            `keranjang_produk`.`sisa`,
            `keranjang_produk`.`img_url`,
            `keranjang_history`.`jumlah`,
            `keranjang_history`.`time_stamp`
          FROM
            `keranjang_history`
          INNER JOIN
            `keranjang_keranjang`
           ON
              `keranjang_keranjang`.`id` = `keranjang_history`.`id_keranjang`
          INNER JOIN `keranjang_user`
           ON
              `keranjang_user`.`id` = `keranjang_history`.`id_user`
          INNER JOIN `keranjang_produk`
           ON 
            `keranjang_produk`.`id` = `keranjang_history`.`id_produk`";
  $result = $conn->query($sql);
?>
<!DOCTYPE html>
<html>
	<head>
		<title>Riwayat Penjualan</title>
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
			<a href="index.php" class="w3-bar-item w3-button w3-padding"><i class="fa fa-info-circle fa-fw"></i>  Dashboard</a>
      <a href="history.php" class="w3-bar-item w3-button w3-padding w3-light-blue"><i class="fa fa-history fa-fw"></i>  History</a>
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

                  <!-- PUT TABLE HERE -->
                  <?php	
                    $i = 0;
                    if ( $result->num_rows > 0 ){
                      echo '<div class="w3-card-4 w3-white">
                              <div class="w3-large w3-indigo" style="vertical-align:middle; text-align:center;">';
                      echo '<table class="w3-table w3-centered w3-white">
                        <thead>
                        <tr class="w3-indigo">
                          <th style="vertical-align: middle;">No</th>
                          <th style="vertical-align: middle;">Gambar</th>
                          <th style="vertical-align: middle;">Waktu</th>
                          <th style="vertical-align: middle;">Produk</th>
                          <th style="vertical-align: middle;">Jumlah</th>
                          <th style="vertical-align: middle;">Harga</th>
                          <th style="vertical-align: middle;">Total</th>
                        </tr>
                        </thead>';
                      while( $row = $result->fetch_assoc() ){
                          echo "<tr>";
                          echo "<td style='vertical-align: middle;'>".($i+=1)."</td>";
                          echo "<td style='vertical-align: middle;'>
                                 <img src='".$row['img_url']."' alt='gambar_produk' width='72px' />
                               </td>";
                          echo "<td style='vertical-align: middle;'>".$row['time_stamp']."</td>";
                          echo "<td style='vertical-align: middle;'>".$row['nama']."</td>";
                          echo "<td style='vertical-align: middle;'>".$row['jumlah']."</td>";
                          echo "<td style='vertical-align: middle;'>Rp. ".$row['harga']."</td>";
                          echo "<td style='vertical-align: middle;'>Rp. ".$row['jumlah'] * $row['harga']."</td>";
                          echo "</tr>";
                       }
                     echo '</table>
                         </div>
                        </div>';
                     } else {
                       echo '<div id="not-found-cart" style="text-align: center; margin-top: 32px">
                              <img src="./static/images/not_found_cart.svg" alt="not found cart" style="height: 70% !important;" />
                            </div>';
                     }
                   ?>
              
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