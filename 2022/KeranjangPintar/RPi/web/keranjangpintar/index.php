<?php
  @session_start();

  if(isset($_GET['resetId']) || isset($_SESSION['resetId'])){
		unset($_SESSION['idKeranjang']);
    unset($_SESSION['resetId']);
    unset($_SESSION['idKeranjang']);
    unset($_GET['resetId']);
    unset($_GET['checkout']);
		unset($_GET['idKeranjang']);
		
		unset($idKeranjang);
    unset($result);
	}
  if(isset($_GET['idKeranjang'])){
		$_SESSION['idKeranjang'] = $_GET['idKeranjang'];
	}
	if(isset($_SESSION['idKeranjang'])){
		$idKeranjang = $_SESSION['idKeranjang'];
	}
	else{
		unset($idKeranjang);
		unset($results);
	}


  if (isset($idKeranjang)) {
		require_once 'inits.php';
    require_once 'db.php';
    $connForm = $conn;

    $sql = "SELECT
              `keranjang_user`.`nama` AS nama_user,
              `keranjang_produk`.`nama` AS nama_produk,
              `keranjang_produk`.`deskripsi`,
              `keranjang_produk`.`harga`,
              `keranjang_produk`.`sisa`,
              `keranjang_produk`.`img_url`,
              `keranjang_pos`.*
            FROM
              `keranjang_pos`
            INNER JOIN
              `keranjang_keranjang`
             ON
              `keranjang_keranjang`.`id` = `keranjang_pos`.`id_keranjang`
            INNER JOIN `keranjang_user`
             ON
              `keranjang_user`.`id` = `keranjang_pos`.`id_user`
            INNER JOIN `keranjang_produk`
             ON 
              `keranjang_produk`.`id` = `keranjang_pos`.`id_produk`
            WHERE `keranjang_keranjang`.`id` = '".$idKeranjang."'";

    $result = $conn->query($sql);
	}
  
  if(isset($_GET['checkout'])){
    if (isset($result)) {
      if ( $result->num_rows > 0 ){
        while( $row = $result->fetch_assoc() ){
          $addHistoryRes = checkoutCart($conn, $row['id_keranjang'], $row['id_produk'], $row['id_user'], $row['jumlah']);
          usleep(50);
          $delPosRes = deleteCart($conn, $row['id']);
          usleep(50);
        }
      }
    }
    unset($_GET['checkout']);
    $_SESSION['resetId'] = 'Reset';
    header("Refresh:0");
	}
?>

<!DOCTYPE html>
<html>
	<head>
		<title>Keranjang Pintar</title>
		<meta charset="UTF-8">
		<meta name="viewport" content="width=device-width, initial-scale=1">
		<link rel="shortcut icon" type="image/png" href="static/images/favicon.png"/>
		<link rel="stylesheet" href="static/styles/w3.css">
		<link rel="stylesheet" href="static/styles/theme.css">
    <link rel="stylesheet" href="static/styles/raleway.css">
		<link rel="stylesheet" href="static/styles/font-awesome.min.css">
    <link rel="stylesheet" href="static/styles/app.css">
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
      <div class="w3-bar-block" >
        <a href="#" class="w3-bar-item w3-button w3-padding-16 w3-hide-large w3-grey w3-hover-black" onclick="w3_close()" title="Close"><i class="fa fa-remove fa-fw"></i>  Close</a>
        <a href="index.php" class="w3-bar-item w3-button w3-padding w3-light-blue"><i class="fa fa-info-circle fa-fw"></i><strong>  Dashboard</strong></a>
        <a href="history.php" class="w3-bar-item w3-button w3-padding"><i class="fa fa-history fa-fw"></i>  History</a>
		  </div>
		</nav>

		<!-- Overlay effect when opening sidebar on small screens -->
		<div class="w3-overlay w3-hide-large w3-animate-opacity" onclick="w3_close()" style="cursor:pointer" title="close side menu" id="myOverlay"></div>

		<!-- !PAGE CONTENT! -->
		<div class="w3-main w3-light-grey" style="margin-left:140px;margin-top:43px;">

		  <!-- Main panel -->
		  <div class="w3-container" style="margin-left:8px;margin-right:8px;margin-top:auto;padding-bottom: 64px;">

        <div style="margin-left: 2em; margin-top: 2em;">
          <form>
            <input
              id="idKeranjang"
              title="idKeranjang"
              name="idKeranjang"
              value="<?php echo isset($idKeranjang) ? $idKeranjang : '';?>"
              placeholder="ID Keranjang"
              class="w3-input w3-border w3-round"
              style="width: auto; display: inline;"/>
            <button id="btnSetKeranjang" type="submit" class="w3-btn w3-indigo" style="margin-left: 16px;">Set</button>
            <input type="submit" value="Reset" id="resetId" title="resetId" name="resetId" class="w3-btn w3-indigo" style="margin-left: 4px;">
          </form>
        </div>

          <?php
            if (isset($result)) {
              if ( $result->num_rows > 0 ){
                echo '<div id="cart">
                      <div class="w3-card cart cart-container" style="background-color: white; border-radius: 8px;">

                      <div class="cart-header">
                        <h3 class="cart-heading">Shopping Cart</h3>
                      </div>
                      <hr style="width: 90%;"/>';

                $totalProduct = 0;
                $totalPrice = 0;
                echo "<div style='padding-left: 24px; padding-right: 24px;'>";
                while( $row = $result->fetch_assoc() ){
                  $totalProduct += $row['jumlah'];
                  $totalPrice += $row['harga'] * $row['jumlah'];
                  echo "<div class='cart-items' style='background-color: white; border-radius: 8px; margin: 0;'>
                          <div class='cart-item-image-box'>
                            <img src='".$row['img_url']."' style='width: 100%; height: auto; border-radius: 4px;' />
                            <div class='cart-item-about'>
                              <h1 class='cart-item-title'>".$row['nama_produk']."</h1>
                              <h3 class='cart-item-subtitle'>".$row['deskripsi']."</h3>
                            </div>
                          </div>
                          <div>
                            <div class='cart-item-prices'>
                              <div class='price-amount'>Rp. ".$row['harga']."</div>
                            </div>
                            <div class='cart-item-prices'>
                              <div class='price-amount'>".$row['jumlah']." item</div>
                            </div>
                          </div>
                        </div>
                        <hr style='width: 37%; margin: 0;'/>";
                }

                echo "</div>";
                echo '<div style="margin-top: 32px;">
                          <div class="cart-checkout-total">
                            <div>
                              <div class="cart-checkout-subtotal">Sub-Total</div>
                              <div class="cart-checkout-items">'.$totalProduct.' item</div>
                            </div>
                          <div class="cart-checkout-total-amount">Rp. '.$totalPrice.'</div>
                          </div>
                          <form>
                            <input
                              type="submit"
                              value="Checkout"
                              name="checkout"
                              id="checkout"
                              class="w3-indigo cart-checkout-button"
                              style="border-radius: 4px; margin-top: 16px;" />
                          </form>
                        </div>

                      </div>
                    </div>';
              } else {
                echo '<div id="not-found-cart" style="text-align: center; margin-top: 32px">
                      <img src="./static/images/not_found_cart.svg" alt="not found cart" style="height: 70% !important;" />
                    </div>';
              }
            } else {
              echo '<div id="no-cart" style="text-align: center; margin-top: 32px">
                      <img src="./static/images/add_to_cart.svg" alt="add to cart" height="80%" />
                    </div>';
            }
        ?>

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
			//setInterval('updateClock()', 1000 );

		</script>
	</body>
</html>
