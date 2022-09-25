<?php
require_once "../db.php";

$valBpm = null;
$valOxy = null;
$valTemp = null;
$valLoc = null;
$nodeId = null;
$dataOk = false;

if (isset($_GET['valBpm'])) {
  $valBpm = $_GET['valBpm'];
  unset($_GET['valBpm']);
  $dataOk = true;
} else $dataOk = false;
if (isset($_GET['valOxy'])) {
  $valOxy = $_GET['valOxy'];
  unset($_GET['valOxy']);
  if (!is_null($valBpm)) $dataOk = true;
} else $dataOk = false;
if (isset($_GET['valTemp'])) {
  $valTemp = $_GET['valTemp'];
  unset($_GET['valTemp']);
  if (!is_null($valOxy)) $dataOk = true;
} else $dataOk = false;
if (isset($_GET['valLoc'])) {
  $valLoc = $_GET['valLoc'];
  unset($_GET['valLoc']);
  if (!is_null($valTemp)) $dataOk = true;
} else $dataOk = false;
if (isset($_GET['nodeId'])) {
  $nodeId = $_GET['nodeId'];
  unset($_GET['nodeId']);
  if (!is_null($valTemp)) $dataOk = true;
} else $dataOk = false;

if ($dataOk) {
  $pantauKaryawanSql = "UPDATE `pantaukaryawan` SET `valBpm` = '" . $valBpm . "', `valOxy` = '" . $valOxy . "', `valTemp` = '" . $valTemp . "', `valLoc` = '" . $valLoc . "', `timeStamp` = CURRENT_TIMESTAMP WHERE `pantaukaryawan`.`nodeId` = '" . $nodeId . "';";
  if ($conn->query($pantauKaryawanSql) === TRUE) {
    echo "Update db pantaukaryawan: " . $pantauKaryawanSql;
  } else echo "Error: " . $pantauKaryawanSql . "<br>" . $conn->error;
} else echo "Error: data not complete<br>";
