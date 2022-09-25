<?php
require_once 'inits.php';

header("Cache-Control: no-store, no-cache, must-revalidate"); // HTTP/1.1
header("Cache-Control: post-check=0, pre-check=0", false);
header("Expires: Sat, 26 Jul 1997 05:00:00 GMT"); // Date in the past
header("Pragma: no-cache"); // HTTP/1.0
header("Last-Modified: " . gmdate("D, d M Y H:i:s") . " GMT");

$TRESHOLD_BPM = 0;
/* $TRESHOLD_OXY = 60; */
$valBpm = 0;
$valOxy = 0;

$sql = "SELECT * FROM `pantausopir` WHERE `nodeId` = '0'";
$result = $conn->query($sql);

if ($result->num_rows > 0) {
  if ($row = $result->fetch_assoc()) {
    $valBpm = floatval($row['bpmVal']);
    $valOxy = floatval($row['oxyVal']);
  }
}

$_SESSION['alarm'] = (intval($valBpm) < $TRESHOLD_BPM) ? true : false;

?>

<div class='w3-card-4 w3-white'>
  <div class='w3-large w3-block w3-blue-grey'>
    <div class='w3-padding'><strong>Captured Picture<span></span></strong></div>
  </div>
  <div class='w3-cell-row'>
    <div class='w3-container w3-cell w3-cell-middle w3-center w3-mobile'>
      <!-- <img src='<?php echo $IMAGE_SRC; ?>' alt='videofeed' width='480px' height='360px' class='w3-center w3-middle w3-padding'> -->
      <img src='<?php echo './imgs/2021-07-13_11.22.00.jpg'; ?>' alt='videofeed' width='480px' height='360px' class='w3-center w3-middle w3-padding'>
    </div>
  </div>
  <div class='w3-large w3-block <?php echo ($_SESSION['alarm']) ? 'w3-red' : 'w3-blue-grey'; ?>'>
    <div class="w3-cell-row">
      <div class="w3-cell">
        <div class='w3-padding-16 w3-margin-left'><strong>BPM: <?php echo $valBpm; ?></strong></div>
      </div>
      <div class="w3-cell">
        <div class='w3-padding-16 w3-margin-right w3-right-align'><strong>Oxy: <?php echo $valOxy; ?></strong></div>
      </div>
    </div>
  </div>
</div>

<?php

if (!isset($_SESSION['play'])) {
  $_SESSION['play'] = false;
} else {
  $play = $_SESSION['play'];
}

if (!isset($_SESSION['alarm'])) {
  $_SESSION['alarm'] = false;
  $alarm = false;
} else {
  $alarm = $_SESSION['alarm'];
}

if (!isset($play)) {
  $play = $_SESSION['play'];
}

if ($alarm == true) {
  if ($play == false) {
    echo "<script>alarmAudio.sound.play();</script>";
    /* echo "<script>console.log('Alarm:on');</script>"; */
    $play = true;
    $_SESSION['play'] = true;
  } else if ($play == true) {
    /* echo "<script>console.log('Alarm:on:playing');</script>"; */
  }
} else if ($alarm == false) {
  if ($play == true) {
    echo "<script>alarmAudio.sound.pause();</script>";
    /* echo "<script>console.log('Alarm:off');</script>"; */
    $play = false;
    $_SESSION['play'] = false;
  } else if ($play == false) {
    /* echo "<script>console.log('Alarm:off:stopped');</script>"; */
  }
}
?>