<?php
	require_once 'db.php';
	
	$sqlSensor = "SELECT * FROM `pupuk_sensor`";
	$resultSensor = $conn->query($sqlSensor);
	
	if ( $resultSensor->num_rows > 0 ) {
		while( $rowSensor = $resultSensor->fetch_assoc() ) {
?>

<div class='w3-cell-row w3-center'>
  <!-- sensors start -->
  <div class='w3-container w3-cell w3-cell-top w3-mobile'>
    <div class='w3-card-4 w3-white'>
      <div class='w3-large w3-indigo' style='vertical-align:middle; text-align:center; padding: 8px; padding-top: 0px;'>
        <h1>Kualitas Lahan</h1>
        <!-- sensor row 1 -->
        <div class='w3-large w3-white'>
          <div class='w3-cell-row w3-center' style='vertical-align:middle; text-align:center; padding: 8px;'>
            <!-- sensor dht moisture -->
            <div class='w3-container w3-cell w3-cell-middle w3-mobile'>
              <div class='w3-large w3-white'>
                <table>
                  <tr>
                    <td><img src='static/images/moist.png' alt='status' width='56px' height='56px' class='w3-circle'></td>
                  </tr>
                  <tr class='w3-white'>
                    <td>Moisture: <?php echo $rowSensor['moist'];?>%</td>
                  </tr>
                </table>
              </div>
            </div>
            <!-- sensor ph -->
            <div class='w3-container w3-cell w3-cell-middle w3-mobile'>
              <div class='w3-large w3-white'>
                <table>
                  <tr>
                    <td><img src='static/images/ph.png' alt='status' width='56px' height='56px' class='w3-circle'></td>
                  </tr>
                  <tr class='w3-white'>
                    <td>pH: <?php echo $rowSensor['ph'];?></td>
                  </tr>
                </table>
              </div>
            </div>
            <!-- sensor humid -->
            <div class='w3-container w3-cell w3-cell-middle w3-mobile'>
              <div class='w3-large w3-white'>
                <table>
                <tr>
                  <td><img src='static/images/humid.png' alt='status' width='56px' height='56px' class='w3-circle'></td>
                </tr>
                <tr class='w3-white'>
                  <td>Humidity: <?php echo $rowSensor['dht_humid'];?>%</td>
                </tr>
              </table>
              </div>
            </div>
          </div>
          
          <!-- sensor row 2 -->
          <div class='w3-large w3-white'>
            <div class='w3-cell-row w3-center' style='vertical-align:middle; text-align:center; padding: 8px;'>
              <!-- sensor npk -->
              <div class='w3-container w3-cell w3-cell-middle w3-mobile'>
                <div class='w3-large w3-white'>
                  <table>
                  <tr>
                    <td><img src='static/images/fertilizer.png' alt='status' width='56px' height='56px' class='w3-circle'></td>
                  </tr>
                  <tr class='w3-white'>
                    <td>NPK: <?php echo $rowSensor['npk'];?>ppm</td>
                  </tr>
                </table>
                </div>
              </div>
              <!-- sensor voltage -->
              <div class='w3-container w3-cell w3-cell-middle w3-mobile'>
                <div class='w3-large w3-white'>
                  <table>
                  <tr>
                    <td><img src='static/images/battery.png' alt='status' width='56px' height='56px' class='w3-circle'></td>
                  </tr>
                  <tr class='w3-white'>
                    <td>Voltage: <?php echo $rowSensor['voltage'];?>v</td>
                  </tr>
                </table>
                </div>
              </div>
              <!-- sensor dht temp -->
              <div class='w3-container w3-cell w3-cell-middle w3-mobile'>
                <div class='w3-large w3-white'>
                  <table>
                    <tr>
                      <td><img src='static/images/temp.png' alt='status' width='56px' height='56px' class='w3-circle'></td>
                    </tr>
                    <tr class='w3-white'>
                      <td>Temp 1: <?php echo $rowSensor['lm35_temp'];?>&deg;C</td>
                    </tr>
                  </table>
                </div>
              </div>
              <!-- sensor lm35 temp -->
              <div class='w3-container w3-cell w3-cell-middle w3-mobile'>
                <div class='w3-large w3-white'>
                  <table>
                    <tr>
                      <td><img src='static/images/temp.png' alt='status' width='56px' height='56px' class='w3-circle'></td>
                    </tr>
                    <tr class='w3-white'>
                      <td>Temp 2: <?php echo $rowSensor['dht_temp'];?>&deg;C</td>
                    </tr>
                  </table>
                </div>
              </div>
              
            </div>
          </div>
          
        </div>
      </div>
    </div>
  </div>
  <?php
      }
    }
  ?>
  <!-- sensors end -->

  <?php
    $sqlPupuk = "SELECT * FROM `pupuk_warehouse`";
    $resultPupuk = $conn->query($sqlPupuk);
    
    if ( $resultPupuk->num_rows > 0 ) {
      while( $rowPupuk = $resultPupuk->fetch_assoc() ) {
  ?>
  <!-- pupuk pupuk start -->
  <div class='w3-container w3-cell w3-cell-top w3-mobile'>
    <div class='w3-card-4 w3-white'>
      <div class='w3-large w3-indigo' style='vertical-align:middle; text-align:center; padding: 8px; padding-top: 0px;'>
        <h1>Ketersediaan Pupuk</h1>
        <div class='w3-large w3-white'>
          <div class='w3-cell-row w3-center' style='vertical-align:middle; text-align:center; padding: 8px;'>
            <!-- pupuk 1 -->
            <div class='w3-container w3-cell w3-cell-middle w3-mobile'>
              <div class='w3-large w3-white'>
                <table>
                  <tr>
                    <td><img src='static/images/fertilizer.png' alt='status' width='56px' height='56px' class='w3-circle'></td>
                  </tr>
                  <tr class='w3-white'>
                    <td>Pupuk 1: <?php echo $rowPupuk['fertilizer_1'];?></td>
                  </tr>
                </table>
              </div>
            </div>
            <!-- pupuk 2 -->
            <div class='w3-container w3-cell w3-cell-middle w3-mobile'>
              <div class='w3-large w3-white'>
                <table>
                  <tr>
                    <td><img src='static/images/fertilizer.png' alt='status' width='56px' height='56px' class='w3-circle'></td>
                  </tr>
                  <tr class='w3-white'>
                    <td>Pupuk 2: <?php echo $rowPupuk['fertilizer_2'];?></td>
                  </tr>
                </table>
              </div>
            </div>
            <!-- pupuk 3 -->
            <div class='w3-container w3-cell w3-cell-middle w3-mobile'>
              <div class='w3-large w3-white'>
                <table>
                  <tr>
                    <td><img src='static/images/fertilizer.png' alt='status' width='56px' height='56px' class='w3-circle'></td>
                  </tr>
                  <tr class='w3-white'>
                    <td>Pupuk 3: <?php echo $rowPupuk['fertilizer_3'];?></td>
                  </tr>
                </table>
              </div>
            </div>
            <!-- pupuk 4 -->
            <div class='w3-container w3-cell w3-cell-middle w3-mobile'>
              <div class='w3-large w3-white'>
                <table>
                  <tr>
                    <td><img src='static/images/fertilizer.png' alt='status' width='56px' height='56px' class='w3-circle'></td>
                  </tr>
                  <tr class='w3-white'>
                    <td>Pupuk 4: <?php echo $rowPupuk['fertilizer_4'];?></td>
                  </tr>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  <?php
      }
    }
  ?>
  <!-- pupuk pupuk end -->
</div>

<?php
  $fert1 = 1;
  $fert2 = 2;
  $fert3 = 3;
  $fert4 = 4;
?>
<!-- prop pupuk start -->
<div class='w3-cell-row w3-center'>
  <div class='w3-container w3-cell w3-cell-top w3-mobile'>
    <div class='w3-card-4 w3-white'>
      <div class='w3-large w3-indigo' style='vertical-align:middle; text-align:center; padding: 8px; padding-top: 0px;'>
        <h1>Proporsi Pupuk</h1>
        <div class='w3-large w3-white'>
          <div class='w3-container w3-cell w3-mobile'>
            <p>
              <?php
                echo "<span>X1 @ " . $fert1 . " gram</span><br>";
                echo "<span>X2 @ " . $fert2 . " gram</span><br>";
                echo "<span>X3 @ " . $fert3 . " gram</span><br>";
                echo "<span>X4 @ " . $fert4 . " gram</span>";
              ?>
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>
<!-- prop pupuk end -->

<!-- history pupuk start -->
<?php
  $sqlHistory = "SELECT * FROM `pupuk_history` ORDER BY `pupuk_history`.`time_stamp` DESC LIMIT 1";
  $resultHistory = $conn->query($sqlHistory);
  
  if ( $resultHistory->num_rows > 0 ) {
    while( $rowHistory = $resultHistory->fetch_assoc() ) {
?>
<div class='w3-cell-row w3-center'>  
  <div class='w3-container w3-cell w3-cell-top w3-mobile'>
    <div class='w3-card-4 w3-white'>
      <div class='w3-large w3-indigo' style='vertical-align:middle; text-align:center; padding: 8px; padding-top: 0px;'>
        <h1>Riwayat Pengiriman</h1>
        <div class='w3-large w3-white'>
          <div class='w3-container w3-cell w3-mobile' style='vertical-align:middle; text-align:left; padding: 8px;'>
            <?php
              echo "<span>Tanggal: " . $rowHistory['time_stamp'] . "</span><br>";
              echo "<span>Pupuk: " . $rowHistory['fertilizer'] . "@" . $rowHistory['total'] . "pak</span><br>";
              echo "<span>Alamat: " . $rowHistory['address'] . "</span>";
            ?>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>
<?php
    }
  }
?>
<!-- history pupuk end -->
