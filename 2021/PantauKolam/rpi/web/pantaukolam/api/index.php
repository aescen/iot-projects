<?php
require_once "../db.php";

$valPhA = null;
$valPhB = null;
$valRpm = null;
$valDaya = null;
$valDebitA = null;
$valDebitB = null;
$valTurbidity = null;
$setTable = null;
$nodeId = null;
$dataOk = false;
$tbOk = false;

if (isset($_GET['setTable'])) {
  $setTable = strval($_GET['setTable']);
  unset($_GET['setTable']);
  $tbOk = true;
} else $tbOk = false;

if ($tbOk) {
  if ($setTable === "kolam") {
    if (isset($_GET['valPhB'])) {
      $valPhB = $_GET['valPhB'];
      unset($_GET['valPhB']);
      $dataOk = true;
    } else $dataOk = false;
    if (isset($_GET['valTurbidity'])) {
      $valTurbidity = $_GET['valTurbidity'];
      unset($_GET['valTurbidity']);
      if (!is_null($valPhB)) $dataOk = true;
    } else $dataOk = false;
    if (isset($_GET['nodeId'])) {
      $nodeId = $_GET['nodeId'];
      unset($_GET['nodeId']);
      if (!is_null($valTurbidity)) $dataOk = true;
    } else $dataOk = false;
    
    if ($dataOk) {
        $pantauKolam_KolamSql = "UPDATE `pantaukolam_kolam` SET `valPhB` = '" . $valPhB . "', `valTurbidity` = '" . $valTurbidity . "', `timeStamp` = CURRENT_TIMESTAMP WHERE `pantaukolam_kolam`.`id` = " . $nodeId . "";
        if ($conn->query($pantauKolam_KolamSql) === TRUE) {
          echo "Update db pantausopir: " . $pantauKolam_KolamSql . "<br><br>";
        } else echo "Error: " . $pantauKolam_KolamSql . "<br>" . $conn->error;
    } else echo "Error: data kolam not complete<br>";
  } else if ($setTable === "turbin") {
    if (isset($_GET['valPhA'])) {
      $valPhA = $_GET['valPhA'];
      unset($_GET['valPhA']);
      $dataOk = true;
    } else $dataOk = false;
    if (isset($_GET['valRpm'])) {
      $valRpm = $_GET['valRpm'];
      unset($_GET['valRpm']);
      if (!is_null($valPhA)) $dataOk = true;
    } else $dataOk = false;
    if (isset($_GET['valDaya'])) {
      $valDaya = $_GET['valDaya'];
      unset($_GET['valDaya']);
      if (!is_null($valRpm)) $dataOk = true;
    } else $dataOk = false;
    if (isset($_GET['valDebitA'])) {
      $valDebitA = $_GET['valDebitA'];
      unset($_GET['valDebitA']);
      if (!is_null($valDaya)) $dataOk = true;
    } else $dataOk = false;
    if (isset($_GET['valDebitB'])) {
      $valDebitB = $_GET['valDebitB'];
      unset($_GET['valDebitB']);
      if (!is_null($valDebitA)) $dataOk = true;
    } else $dataOk = false;
    if (isset($_GET['nodeId'])) {
      $nodeId = $_GET['nodeId'];
      unset($_GET['nodeId']);
      if (!is_null($valDebitB)) $dataOk = true;
    } else $dataOk = false;

    if ($dataOk) {
      $pantauKolam_TurbinSql = "UPDATE `pantaukolam_turbin` SET `valRpm` = '" . $valRpm . "', `valDaya` = '" . $valDaya . "', `valDebitA` = '" . $valDebitA . "', `valDebitB` = '" . $valDebitB . "', `valPhA` = '" . $valPhA . "', `timeStamp` = CURRENT_TIMESTAMP WHERE `pantaukolam_turbin`.`id` = '" . $nodeId . "'";
      if ($conn->query($pantauKolam_TurbinSql) === TRUE) {
        echo "Update db pantausopir: " . $pantauKolam_TurbinSql . "<br><br>";
      } else echo "Error: " . $pantauKolam_TurbinSql . "<br>" . $conn->error;
    } else echo "Error: data turbin not complete<br>";
  } else {
    echo "Error: unknown table name<br>";
  }
} else echo "Error: unknown table name<br>";
