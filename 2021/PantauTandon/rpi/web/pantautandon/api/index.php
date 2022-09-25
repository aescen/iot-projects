<?php
require_once "../db.php";

$valPh = null;
$valConductivity = null;
$valTurbidity = null;
$valUltrasonic = null;
$nodeId = null;
$dataOk = false;


if (isset($_GET['valPh'])) {
  $valPh = $_GET['valPh'];
  unset($_GET['valPh']);
  $dataOk = true;
} else $dataOk = false;
if (isset($_GET['valConductivity'])) {
  $valConductivity = $_GET['valConductivity'];
  unset($_GET['valConductivity']);
  if (!is_null($valPh)) $dataOk = true;
} else $dataOk = false;
if (isset($_GET['valTurbidity'])) {
  $valTurbidity = $_GET['valTurbidity'];
  unset($_GET['valTurbidity']);
  if (!is_null($valConductivity)) $dataOk = true;
} else $dataOk = false;
if (isset($_GET['valUltrasonic'])) {
  $valUltrasonic = $_GET['valUltrasonic'];
  unset($_GET['valTurbidity']);
  if (!is_null($valConductivity)) $dataOk = true;
} else $dataOk = false;
if (isset($_GET['nodeId'])) {
  $nodeId = $_GET['nodeId'];
  unset($_GET['nodeId']);
  if (!is_null($valUltrasonic)) $dataOk = true;
} else $dataOk = false;

if ($dataOk) {
  $pantauTandonSql1 = "UPDATE `pantautandon` SET `valObject` = '" . $valPh . "', `timeStamp` = CURRENT_TIMESTAMP WHERE `pantautandon`.`objectType` = 'ph' AND `pantautandon`.`nodeId` = '" . $nodeId . "';";
  if ($conn->query($pantauTandonSql1) === TRUE) {
    echo "Update db pantausopir: " . $pantauTandonSql1 . "<br><br>";
  } else echo "Error: " . $pantauTandonSql1 . "<br>" . $conn->error;

  $pantauTandonSql2 = "UPDATE `pantautandon` SET `valObject` = '" . $valConductivity . "', `timeStamp` = CURRENT_TIMESTAMP WHERE `pantautandon`.`objectType` = 'conductivity' AND `pantautandon`.`nodeId` = '" . $nodeId . "';";
  if ($conn->query($pantauTandonSql2) === TRUE) {
    echo "Update db pantausopir: " . $pantauTandonSql2 . "<br><br>";
  } else echo "Error: " . $pantauTandonSql2 . "<br>" . $conn->error;

  $pantauTandonSql3 = "UPDATE `pantautandon` SET `valObject` = '" . $valTurbidity . "', `timeStamp` = CURRENT_TIMESTAMP WHERE `pantautandon`.`objectType` = 'turbidity' AND `pantautandon`.`nodeId` = '" . $nodeId . "';";
  if ($conn->query($pantauTandonSql3) === TRUE) {
    echo "Update db pantausopir: " . $pantauTandonSql3 . "<br><br>";
  } else echo "Error: " . $pantauTandonSql3 . "<br>" . $conn->error;

  $pantauTandonSql4 = "UPDATE `pantautandon` SET `valObject` = '" . $valUltrasonic . "', `timeStamp` = CURRENT_TIMESTAMP WHERE `pantautandon`.`objectType` = 'ultrasonic' AND `pantautandon`.`nodeId` = '" . $nodeId . "';";
  if ($conn->query($pantauTandonSql4) === TRUE) {
    echo "Update db pantausopir: " . $pantauTandonSql4 . "<br><br>";
  } else echo "Error: " . $pantauTandonSql4 . "<br>" . $conn->error;
  
} else echo "Error: data not complete<br>";
