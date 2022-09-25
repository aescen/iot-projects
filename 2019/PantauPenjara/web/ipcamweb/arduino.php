<?php
  include("config.php");
   
  if( isset($_GET["m1"]) ){
    $m1 = $_GET['m1'];

    $sql = "UPDATE `status` SET `Nilai` = '".$m1."' WHERE `Status`.`Nama` = 'm1'";
    if ($conn->query($sql) === TRUE) {
      echo $m1.":Success</br>";
      unset($_GET['m1']);
    } else {
      echo "Error: " . $sql . "<br>" . $conn->error;
    }
  }

  if( isset($_GET['m2']) ){
    $m2 = $_GET['m2'];

    $sql2 = "UPDATE `status` SET `Nilai` = '".$m2."' WHERE `Status`.`Nama` = 'm2'";
    if ($conn->query($sql2) === TRUE) {
      echo $m2.":Success</br>";
      unset($_GET['m2']);
    } else {
      echo "Error: " . $sql2 . "<br>" . $conn->error;
    }
  }

  if( isset($_GET['m3']) ){
    $m3 = $_GET['m3'];

    $sql3 = "UPDATE `status` SET `Nilai` = '".$m3."' WHERE `Status`.`Nama` = 'm3'";
    if ($conn->query($sql3) === TRUE) {
      echo $m3.":Success</br>";
      unset($_GET['m3']);
    } else {
      echo "Error: " . $sql3 . "<br>" . $conn->error;
    }
  }

  if( isset($_GET['m4']) ){
    $m4 = $_GET['m4'];

    $sql4 = "UPDATE `status` SET `Nilai` = '".$m4."' WHERE `Status`.`Nama` = 'm4'";
    if ($conn->query($sql4) === TRUE) {
      echo $m4.":Success</br>";
      unset($_GET['m4']);
    } else {
      echo "Error: " . $sql4 . "<br>" . $conn->error;
    }
  }
  ?>