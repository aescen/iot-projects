<?php
$servername = "localhost";
$username = "root";
$password = "";
$dbname = "pi";

if (strtoupper(substr(PHP_OS, 0, 3)) === 'WIN') {
  // echo 'This is a server using Windows!';
  null;
} else {
  // echo 'This is a server not using Windows!';
  $username = "pi";
  $password = "raspberry";
}

// Create connection
$conn = new mysqli($servername, $username, $password, $dbname);
// Check connection
if ($conn->connect_error) {
  die("Connection failed: " . $conn->connect_error);
}
