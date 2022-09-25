<?php
require_once 'db.php';
@session_start();

if (isset($_POST['email']) && isset($_POST['username']) && isset($_POST['password'])) {
	$email = $_POST['email'];
	$username = $_POST['username'];
	$password = $_POST['password'];
	$passwordHash = password_hash($password, PASSWORD_DEFAULT);

	unset($_POST['email']);
	unset($_POST['username']);
	unset($_POST['password']);

	$connCheckUser = $conn;
	$sqlUser = "SELECT `username` FROM `pantauternak_users` WHERE `username` = '" . $username . "' LIMIT 1";
	$result = $connCheckUser->query($sqlUser);
	if ($result->num_rows == 1) {
		if ($row = $result->fetch_assoc()) {
			$_SESSION['isUsernameExist'] = 'true';
		} else {
			throw new Exception("This shouldn't have been happened.");
		}
	} else {
		$_SESSION['isUsernameExist'] = 'false';
		$connRegister = $conn;
		$sqlRegister = "INSERT INTO `pantauternak_users` (`email`, `username`, `password`) VALUES ('" . $email . "', '" . $username . "', '" . $passwordHash . "')";
		if ($connRegister->query($sqlRegister) === TRUE) {
			$_SESSION['isRegisterSuccess'] = 'true';
		} else {
			$_SESSION['isRegisterSuccess'] = 'false';
		}
	}
}

?>
<!DOCTYPE html>
<html>

<head>
	<title>Register</title>
	<meta charset="UTF-8">
	<meta name="viewport" content="initial-scale=1, shrink-to-fit=no, width=device-width">
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
		const isUsernameExist =
			<?php
			echo isset($_SESSION['isUsernameExist']) ? $_SESSION['isUsernameExist'] : 'null';
			unset($_SESSION['isUsernameExist']);
			?>;
		if (isUsernameExist) {
			alert('Username sudah ada!');
		}
		if (!isUsernameExist && isUsernameExist !== null) {
			const isRegisterSuccess =
				<?php
				echo isset($_SESSION['isRegisterSuccess']) ? $_SESSION['isRegisterSuccess'] : 'null';
				unset($_SESSION['isRegisterSuccess']);
				?>;
			if (isRegisterSuccess) {
				window.location.href = '/jualbeliternak/login.php';
			}
			if (!isRegisterSuccess && isRegisterSuccess !== null) {
				window.alert('Mohon maaf registrasi gagal, silakan hubungi admin!')
			}
		}
	</script>
	<script>
		const PASSWORD_LENGTH = 8;
		const isLogin = window.localStorage.getItem('isLogin');
		if (isLogin === 'true') {
			window.location.href = '/jualbeliternak';
		}
		const validasiForm = (nilai) => {
			const errors = {};
			const regex = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/i;
			if (!nilai.email) {
				errors.email = 'Email tidak boleh kosong';
			} else if (!regex.test(nilai.email)) {
				errors.email = 'Format email salah!';
			}
			if (!nilai.username) {
				errors.username = 'Nama anda tidak boleh kosong!';
			}
			if (!nilai.password) {
				errors.password = 'Password anda tidak boleh kosong!';
			} else if (nilai.password.length < PASSWORD_LENGTH) {
				errors.password = 'Password harus lebih dari 8 karakter!';
			}
			if (!nilai.password2) {
				errors.password2 = 'Password anda tidak boleh kosong!';
			} else if (nilai.password2 !== nilai.password) {
				errors.password = 'Password tidak sama!';
				errors.password2 = 'Password tidak sama!';
			}

			return errors;
		};
		const setFormError = (formEl, errorProps) => {
			if (JSON.stringify(errorProps) !== '{}') {
				formEl.querySelector('#emailError').textContent = errorProps.email;
				formEl.querySelector('#usernameError').textContent = errorProps.username;
				formEl.querySelector('#passwordError').textContent = errorProps.password;
				formEl.querySelector('#password2Error').textContent = errorProps.password2;
				setTimeout(() => {
					formEl.querySelector('#emailError').textContent = '';
					formEl.querySelector('#usernameError').textContent = '';
					formEl.querySelector('#passwordError').textContent = '';
					formEl.querySelector('#password2Error').textContent = '';
				}, 2000);
			} else {
				formEl.submit();
			}
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
	</style>
</head>

<body class="w3-light-grey">
	<!-- Top container -->
	<div class="w3-bar w3-top w3-white w3-large" style="z-index:4">
		<button type="button" class="w3-bar-item w3-button w3-hide-large w3-xlarge w3-hover-none w3-hover-text-light-grey" onclick="w3_open();"><i class="fa fa-bars"></i>  Menu</button>
		<span class="w3-bar-item w3-hide-small w3-hide-medium w3-xlarge">Register</span>
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

		<!-- Header -->
		<div class="w3-mobile">
			<form id="formRegister" method="post" class="w3-container w3-center" style="padding-top: 64px; display: flex; align-items: center; justify-content: center;">
				<div class='w3-card' style="padding: 48px; padding-top: 24px; width: 40%;">
					<div class="w3-padding" style="text-align: left;">
						<label class="w3-text-teal"><b>Email</b></label>
						<input class="w3-input w3-border" type="text" id="email" name="email" placeholder="email" />
						<p class="w3-text-red" id="emailError"></p>
					</div>

					<div class="w3-padding" style="text-align: left;">
						<label class="w3-text-teal"><b>Username</b></label>
						<input class="w3-input w3-border" type="text" id="username" name="username" placeholder="username" />
						<p class="w3-text-red" id="usernameError"></p>
					</div>

					<div class="w3-padding" style="text-align: left;">
						<label class="w3-text-teal"><b>Password</b></label>
						<input class="w3-input w3-border" type="password" id="password" name="password" placeholder="password" />
						<p class="w3-text-red" id="passwordError"></p>
					</div>

					<div class="w3-padding" style="text-align: left;">
						<label class="w3-text-teal"><b>Ketik ulang password</b></label>
						<input class="w3-input w3-border" type="password" id="password2" name="password2" placeholder="password2" />
						<p class="w3-text-red" id="password2Error"></p>
					</div>

					<p>Sudah punya akun? <a class="w3-text-teal" style="text-decoration: none; cursor: pointer;" href="./login.php">Login</a></p>
					<button id="submitForm" class="w3-btn w3-teal" type="submit">Register</button>
				</div>
			</form>
		</div>

		<!-- End page content -->
	</div>
	<script>
		document.querySelector('#formRegister').addEventListener('submit', (ev) => {
			ev.preventDefault();
			const formData = new FormData(ev.target);
			const formProps = Object.fromEntries(formData);
			setFormError(ev.target, validasiForm(formProps));
		})
	</script>
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
		function buyItem(id, berat, imgPath, harga) {
			const item = {
				id,
				berat,
				imgPath,
				harga
			};
			window.sessionStorage.setItem('BUY_ITEM', JSON.stringify(item));
			window.location.href = './pembelian.php';
		}
	</script>
</body>

</html>