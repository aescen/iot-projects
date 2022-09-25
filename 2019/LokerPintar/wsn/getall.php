<?php
  include('config.php');
  $result = $conn->query("SELECT * FROM `Status` WHERE `Node` = 1 ");
  while($row = mysqli_fetch_assoc($result)){
    echo $row['suhu'].';'.$row['kelembaban'].';'.$row['moisture'].';';
  }
?>
