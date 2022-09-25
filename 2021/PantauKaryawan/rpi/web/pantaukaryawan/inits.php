<?php
require_once 'db.php';

if (session_id() == '') {
  session_start();
}

$threshTemp = 37.5;
$tempOk = "fa fa-check w3-large w3-green w3-hover-lime";
$tempBad = "fa fa-times w3-xlarge w3-red w3-hover-orange";
$statusStr1 = "<i type='button' class='";
$statusStr2 = "'></i>";
