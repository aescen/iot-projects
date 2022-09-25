<?php
  include("config.php");
   
  if( isset($_GET["data1"]) ){
    $data1 = $_GET['data1'];

    $sql = "INSERT INTO `status` (`id`, `Nama`, `Nilai`) VALUES (NULL, 'data1', '".$data1."')";
    if ($conn->query($sql) === TRUE) {
      echo $data1.":Success</br>";
      unset($_GET['data1']);
    } else {
      echo "Error: " . $sql . "<br>" . $conn->error;
    }
  }

  if( isset($_GET['data2']) ){
    $data2 = $_GET['data2'];

    $sql2 = "INSERT INTO `status` (`id`, `Nama`, `Nilai`) VALUES (NULL, 'data2', '".$data2."')";
    if ($conn->query($sql2) === TRUE) {
      echo $data2.":Success</br>";
      unset($_GET['data2']);
    } else {
      echo "Error: " . $sql2 . "<br>" . $conn->error;
    }
  }
?>