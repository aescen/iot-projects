<?php
	$servername = "localhost";
	$username = "alfansht_alfan";
	$password = "!pPm9Sm-86";
	$dbname = "alfansht_alfan";
	
	// Create connection
	$conn = new mysqli($servername, $username, $password, $dbname);
	// Check connection
	if ( $conn->connect_error ) {
		die("Connection failed: " . $conn->connect_error);
	}
?>