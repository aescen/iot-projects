<?php
require_once 'db.php';

if (session_id() == '') {
  session_start();
}

function checkServer($host = '127.0.0.1', $port = '8080', $timeout = 20)
{
  try {
    $socket = @fsockopen($host, $port, $errno, $errstr, $timeout);
    if ($socket) {
      return true;
    } else {
      throw new Exception("Cannot connect to host on port");
    }
  } catch (Exception $e) {
    return false;
  }
}

function loadResource()
{
  if (checkServer() !== false) {
    return 'http://127.0.0.1:8080/image';
  } else {
    return './imgs/captured.jpg';
  }
}

$IMAGE_SRC = loadResource();
