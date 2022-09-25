<?php
  define('TOTAL_INFO_COLOR', array('NORMAL' => 'green', 'BERLEBIH' => 'red'));
  define('WATT_TOTAL_BERLEBIH', 1000.0);

  define('NODE_INFO', array('0' => 'NORMAL', '1' => 'BERLEBIH'));
  define('NODE_INFO_COLOR', array('NORMAL' => 'blue', 'BERLEBIH' => 'red'));

  $totalWattColor = 'green';
  $totalWatt = 0;

  $nodeStatus = array(
    '1' => 0,
    '2' => 0,
    '3' => 0,
    '4' => 0,
    '5' => 0,
    '6' => 0,
    '7' => 0,
    '8' => 0
  );

  $sql = "SELECT * FROM `otobus`";

  function getColorForWatt($watt, $thres, $colors) {
    $watt = floatval($watt);
    if ($watt > $thres) {
      return $colors['BERLEBIH'];
    } else {
      return $colors['NORMAL'];
    }
  }
?>
