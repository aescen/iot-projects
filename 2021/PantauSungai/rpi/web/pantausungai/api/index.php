<?php
  require_once "../db.php";
   
  if( isset($_GET['valTurbidity']) ){
    $turbidity = $_GET['valTurbidity'];

    $turbiditySql = "UPDATE `pantausungai` SET `sensorVal` = '" . $turbidity . "' WHERE `pantausungai`.`sensorType` = 'turbidity'";
    if ($conn->query($turbiditySql) === TRUE) {
      echo "Update turbidity sensor value: " . $turbidity;
      unset($_GET['valTurbidity']);
    } else {
      echo "Error: " . $turbiditySql . "<br>" . $conn->error;
    }
  } else {
      echo "Error: no data";
  }
?>