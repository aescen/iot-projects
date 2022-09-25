<?php
require_once "../db.php";

$valBpm = null;
$valOxy = null;
$valIsCapturePicture = null;
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
if (isset($_GET['valIsCapturePicture'])) {
  $valIsCapturePicture = $_GET['valIsCapturePicture'];
  unset($_GET['valIsCapturePicture']);
  if (!is_null($valOxy)) $dataOk = true;
} else $dataOk = false;
if (isset($_GET['nodeId'])) {
  $nodeId = $_GET['nodeId'];
  unset($_GET['nodeId']);
  if (!is_null($valIsCapturePicture)) $dataOk = true;
} else $dataOk = false;

if ($dataOk) {
  $pantauSopirSql = "UPDATE `pantausopir` SET `bpmVal` = '" . $valBpm . "', `oxyVal` = '" . $valOxy . "', `IsCapturePicture` = '" . $valIsCapturePicture . "', `nodeId` = '" . $nodeId . "' WHERE `pantausopir`.`nodeId` = " . $nodeId;
  if ($conn->query($pantauSopirSql) === TRUE) {
    echo "Update db pantausopir: " . $pantauSopirSql;
  } else echo "Error: " . $pantauSopirSql . "<br>" . $conn->error;
} else echo "Error: data not complete<br>";
