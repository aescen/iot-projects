<?php
@session_start();
?>
<!DOCTYPE html>
<html>

<head>
  <title>Beli Ternak</title>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="shortcut icon" type="image/png" href="./static/images/favicon.png" />
  <link rel="stylesheet" href="./static/styles/css.css">
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
    const setItem = JSON.parse(window.sessionStorage.getItem('SET_ITEM'));
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
    <span class="w3-bar-item w3-hide-small w3-hide-medium w3-xlarge">Pembelian</span>
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
      <a href="index.php" class="w3-bar-item w3-button w3-padding"><i class="fa fa-info-circle fa-fw"></i> Status</a>
      <a href="history.php" class="w3-bar-item w3-button w3-padding"><i class="fa fa-history fa-fw"></i> History</a>
    </div>
  </nav>

  <!-- Overlay effect when opening sidebar on small screens -->
  <div class="w3-overlay w3-hide-large w3-animate-opacity" onclick="w3_close()" style="cursor:pointer" title="close side menu" id="myOverlay"></div>

  <!-- !PAGE CONTENT! -->
  <div class="w3-main w3-light-grey" style="margin-left:140px;margin-top:43px;">

    <!-- Feeds panel -->
    <div class="w3-container" style="margin-left:8px;margin-right:8px;margin-top:20px;">
      <div class="w3-row-padding" style="margin:0 -16px; display: flex; align-items: center; justify-content: center;">
        <div class='w3-cell-row'>
          <div class='w3-cell'>
            <div class="w3-container" style="padding-top:22px">
              <div class='w3-card-4'>
                <header class="w3-container w3-teal">
                  <h3>Pembelian</h3>
                </header>
                <div class="w3-container w3-section w3-padding">
                  <div class="w3-center" style="width: 100%;">
                    <img id="item-img" src="" alt="produk" width='480px'>
                  </div>
                  <div class='w3-cell-row w3-margin-top'>
                    <h5 class='w3-cell'>ID</h5>
                    <h5 id='item-id' class='w3-cell w3-right-align'>...</h5>
                  </div>
                  <div class='w3-cell-row'>
                    <h5 class='w3-cell'>Berat</h5>
                    <h5 id='item-berat' class='w3-cell w3-right-align'>...</h5>
                  </div>
                  <div class='w3-cell-row'>
                    <h5 class='w3-cell'><b>Harga</b></h5>
                    <h5 id='item-harga' class='w3-cell w3-right-align'><b>...</b></h5>
                  </div>
                </div>
              </div>

              <div class='w3-card-4'>
                <header class="w3-container w3-teal">
                  <h3>Alamat Pengiriman</h3>
                </header>
                <div class="w3-container w3-section w3-padding">
                  <div>
                    <label for='namapenerima'>Nama penerima</label>
                    <input class="w3-input w3-border" type='text' id='namapenerima' name='namapenerima' placeholder="nama penerima" />
                  </div>

                  <div class="w3-margin-top">
                    <label for='alamatpenerima'>Alamat penerima</label>
                    <input class="w3-input w3-border" type='text' id='alamatpenerima' name='namapenerima' placeholder="alamat penerima" />
                  </div>

                  <div class="w3-section">
                    <label for='nohp'>Nomor kontak</label>
                    <input class="w3-input w3-border" type='text' id='nohp' name='nohp' placeholder="nomor kontak" />
                  </div>

                </div>
              </div>

            </div>
          </div>
          <div class='w3-cell'>
            <div class="w3-container" style="padding-top:22px">
              <div class='w3-card-4'>
                <header class="w3-container w3-teal">
                  <h3>Pembayaran</h3>
                </header>
                <div class="w3-container w3-section">
                  <hr style="border-top: 1px solid #999; margin: 0.5rem 0; padding: 0;" />
                  <h5>Online Wallet</h5>
                  <hr style="border-top: 1px solid #999; margin: 0.5rem 0; padding: 0;" />
                  <div class="w3-margin">
                    <input type='radio' name='pembayaran' value='Gopay' checked />
                    <img src="./static/images/gopay.png" height='24px' alt="gopay"> Gopay
                  </div>
                  <div class="w3-margin">
                    <input type='radio' name='pembayaran' value='Dana' />
                    <img src="./static/images/dana.png" height='24px' alt="dana"> Dana
                  </div>
                  <div class="w3-margin">
                    <input type='radio' name='pembayaran' value='ShopeePay' />
                    <img src="./static/images/shopeepay.png" height='24px' alt="shopeepay"> Shopee Pay
                  </div>

                  <hr style="border-top: 1px solid #999; margin: 0.5rem 0; padding: 0;" />
                  <h5>Virtual Account Bank</h5>
                  <hr style="border-top: 1px solid #999; margin: 0.5rem 0; padding: 0;" />
                  <div class="w3-margin">
                    <input type='radio' name='pembayaran' value='vbca' />
                    <img src="./static/images/bca.png" height='24px' alt="vbca"> BCA
                  </div>
                  <div class="w3-margin">
                    <input type='radio' name='pembayaran' value='vbni' />
                    <img src="./static/images/bni.png" height='24px' alt="vbni"> BNI
                  </div>
                  <div class="w3-margin">
                    <input type='radio' name='pembayaran' value='vbri' />
                    <img src="./static/images/bri.png" height='24px' alt="vbri"> BRI
                  </div>
                  <div class="w3-margin">
                    <input type='radio' name='pembayaran' value='vmandiri' />
                    <img src="./static/images/mandiri.png" height='24px' alt="vmandiri"> Mandiri
                  </div>
                  <hr style="border-top: 1px solid #999; margin: 0.5rem 0; padding: 0;" />
                  <h5>Transfer Bank</h5>
                  <hr style="border-top: 1px solid #999; margin: 0.5rem 0; padding: 0;" />
                  <div class="w3-margin">
                    <input type='radio' name='pembayaran' value='vbca' />
                    <img src="./static/images/bca.png" height='24px' alt="tbca"> BCA
                  </div>
                  <div class="w3-margin">
                    <input type='radio' name='pembayaran' value='vbni' />
                    <img src="./static/images/bni.png" height='24px' alt="tbni"> BNI
                  </div>
                  <div class="w3-margin">
                    <input type='radio' name='pembayaran' value='vbri' />
                    <img src="./static/images/bri.png" height='24px' alt="tbri"> BRI
                  </div>
                  <div class="w3-margin">
                    <input type='radio' name='pembayaran' value='vmandiri' />
                    <img src="./static/images/mandiri.png" height='24px' alt="tmandiri"> Mandiri
                  </div>
                  <hr style="border-top: 1px solid #999; margin: 0.5rem 0; padding: 0;" />
                </div>

                <button class="w3-button w3-large w3-block w3-dark-grey" onclick="document.getElementById('id01').style.display='block'">Lanjutkan Pembelian</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div id="id01" class="w3-modal">
      <div class="w3-modal-content">
        <div class="w3-container w3-padding w3-center">
          <h3>Item ID: <span id="modalItemId"></span></h3>
          <img src="./static/images/qr.png" alt="qr" class="w3-margin" />
          <form id="formBeli" method="POST" action="./lanjutbeli.php">
            <input id="formItemId" type="text" name="itemId" value="" hidden />
            <button class="w3-button w3-large w3-block w3-dark-grey" name="beli" value="beli">Lanjutkan Pembelian</button>
          </form>
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
  <script>
    document.querySelector('#modalItemId').textContent = `${setItem.id}`;
    document.querySelector('#formItemId').value = `${setItem.id}`;
    document.querySelector('#item-img').src = `${setItem.imgPath}`;
    document.querySelector('#item-id').textContent = `${setItem.id}`;
    document.querySelector('#item-berat').textContent = `${setItem.berat}kg`;
    document.querySelector('#item-harga').textContent = `${setItem.harga}`;
  </script>
</body>

</html>