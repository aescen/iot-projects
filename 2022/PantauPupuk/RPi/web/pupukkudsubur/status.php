<?php
	require_once 'db.php';
  require_once 'inits.php';
  $za = 300;
  $ponska = 0;
  $compost = 'Tidak diperlukan karena kondisi tanah sudah baik';
	
	$sqlSensor = "SELECT * FROM `pupuk_sensor`";
	$resultSensor = $conn->query($sqlSensor);
	
	if ( $resultSensor->num_rows > 0 ) {
		while( $rowSensor = $resultSensor->fetch_assoc() ) {
      $ph = floatval($rowSensor['ph']);
      $moist = floatval($rowSensor['moist']);
?>

<div class='w3-cell-row w3-center'>
  <!-- sensors start -->
  <div class='w3-container w3-cell w3-cell-top w3-mobile'>
    <div class='w3-card-4 w3-white'>
      <div class='w3-large w3-indigo' style='vertical-align:middle; text-align:center; padding: 8px; padding-top: 0px;'>
        <h1>Kualitas Lahan</h1>
        <!-- sensor row 1 -->
        <div class='w3-large w3-white'>
          <div class='w3-center' style='display: flex; flex-wrap: wrap; justify-content: space-evenly; align-items:ceter; vertical-align:middle; text-align:center; padding: 8px 0px;'>
            <!-- sensor dht moisture -->
            <div class='w3-container w3-cell w3-cell-middle w3-mobile'>
              <div class='w3-large w3-white'>
                <img src='static/images/moist.png' alt='status' width='56px' height='56px' class='w3-circle'>
                <br />
                <p>Moisture: <?php echo $rowSensor['moist'];?>%</p>
              </div>
            </div>
            <!-- sensor ph -->
            <div class='w3-container w3-cell w3-cell-middle w3-mobile'>
              <div class='w3-large w3-white'>
                <img src='static/images/ph.png' alt='status' width='56px' height='56px' class='w3-circle'>
                <br />
                <p>pH: <?php echo $rowSensor['ph'];?></p>
              </div>
            </div>
          </div>
          
          <!-- sensor row 2 -->
          <div class='w3-large w3-white'>
            <div class='w3-center' style='display: flex; flex-wrap: wrap; justify-content: space-evenly; align-items:ceter; vertical-align:middle; text-align:center; padding: 8px 0px;'>
              <!-- sensor n -->
              <div class='w3-container w3-cell w3-cell-middle w3-mobile'>
                <div class='w3-large w3-white'>
                  <img src='static/images/fertilizer.png' alt='status' width='56px' height='56px' class='w3-circle'>
                  <br/>
                  <p>N: <?php echo $rowSensor['n'];?>ppm</p>
                </div>
              </div>
              <!-- sensor n -->
              <div class='w3-container w3-cell w3-cell-middle w3-mobile'>
                <div class='w3-large w3-white'>
                  <img src='static/images/fertilizer.png' alt='status' width='56px' height='56px' class='w3-circle'>
                  <br/>
                  <p>P: <?php echo $rowSensor['p'];?>ppm</p>
                </div>
              </div>
              <!-- sensor n -->
              <div class='w3-container w3-cell w3-cell-middle w3-mobile'>
                <div class='w3-large w3-white'>
                  <img src='static/images/fertilizer.png' alt='status' width='56px' height='56px' class='w3-circle'>
                  <br/>
                  <p>K: <?php echo $rowSensor['k'];?>ppm</p>
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
          <div class='w3-center' style='display: flex; flex-wrap: wrap; justify-content: space-evenly; align-items:ceter; vertical-align:middle; text-align:center; padding: 8px 0px;'>
            <!-- pupuk 1 -->
            <div class='w3-container w3-cell w3-cell-middle w3-mobile'>
              <div class='w3-large w3-white'>
                <table>
                  <tr>
                    <td><img src='static/images/fertilizer.png' alt='status' width='56px' height='56px' class='w3-circle'></td>
                  </tr>
                  <tr class='w3-white'>
                    <td>Pupuk ZA:<br><?php echo $rowPupuk['za'];?> sak</td>
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
                    <td>Pupuk Ponska:<br><?php echo $rowPupuk['ponska'];?> sak</td>
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
                    <td>Pupuk Kompos:<br><?php echo $rowPupuk['kompos'];?> sak</td>
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
          <div class='w3-container w3-cell w3-mobile' style='vertical-align:middle; text-align:left; padding: 8px;'>
            <?php
              if ( (6 <= $ph) && ($ph <= 7.5)) {
                $ponska = map($ph, 6, 7.5, 400, 10);
              }
              else if ((7.5 < $ph) && ($ph <= 10)){
                $za = 600; 
                $ponska = map($ph, 7.6, 10, 200, 10 );
              }
              else if ((4 <= $ph) && ($ph < 7.5)){
                $ponska = map($ph, 4, 7.4, 600, 200 );
              }
              
              if ( $moist <= 80) {
                $compost= map($moist, 0, 80, 100, 0);
              }
              
              echo '<h3>Pupuk ZA: ' . $za . ' kg</h3>';
              echo '<h3>Pupuk Ponska: ' . $ponska . ' kg</h3>';
              echo '<h3>Pupuk Kompos: ' . $compost . ($compost != 0.0 ? ' kg</h3>' : $compost . '</h3>');
            ?>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>
<!-- prop pupuk end -->

<!-- history pupuk start -->
<div class='w3-cell-row w3-center'>  
  <div class='w3-container w3-cell w3-cell-top w3-mobile'>
    <div class='w3-card-4 w3-white'>
      <div class='w3-large w3-indigo' style='vertical-align:middle; text-align:center; padding: 8px; padding-top: 0px;'>
        <h1>Riwayat Pengambilan</h1>
          <?php
            $sqlHistoryTime = "SELECT * FROM `pupuk_history` ORDER BY `pupuk_history`.`time_stamp` DESC LIMIT 1";
            $resultHistory = $conn->query($sqlHistoryTime);

            if ( $resultHistory->num_rows > 0 ) {
              if( $rowHistory = $resultHistory->fetch_assoc() ) {
                $historyTime = date( "Y-m-d", strtotime( $rowHistory['time_stamp'] ) );
                $historyTimeStart = $historyTime . " 00:00:00.000000";
                $historyTimeEnd = $historyTime . " 23:59:59.999999";
                $sqlHistory = "SELECT * FROM `pupuk_history` WHERE `time_stamp` BETWEEN '$historyTimeStart' AND '$historyTimeEnd' ORDER BY `pupuk_history`.`time_stamp` DESC";
              ?>
                <?php
                $resultHistory = $conn->query($sqlHistory);
                if ( $resultHistory->num_rows > 0 ) {
                  while( $rowHistory = $resultHistory->fetch_assoc() ) {
                ?>            
                <div class='w3-large w3-white' style='display: flex;'>
                  <div class='w3-container w3-cell w3-mobile' style='vertical-align:middle; text-align:left; padding: 8px;'>
                    <?php
                      echo "<hr/><h3>Alamat: " . $rowHistory['address'] . "</h3>";
                      echo "<h4>Tanggal: " . $rowHistory['time_stamp'] . "</h4>";
                      echo "<h4>Pupuk ZA: " . $rowHistory['za'] . " sak</h4>";
                      echo "<h4>Pupuk Ponska: " . $rowHistory['ponska'] . " sak</h4>";
                      echo "<h4>Pupuk Kompos: " . $rowHistory['kompos'] . " sak</h4>";
                    ?>
                  </div>
                </div>
                <?php
                  }
                }
                ?>
            <?php
              }
            } else {
              echo "<div class='w3-large w3-white' style='display: flex;'>
                      <div class='w3-container w3-cell w3-mobile' style='vertical-align:middle; text-align:left; padding: 8px;'>
                        <h1>Kosong</h1>
                      </div>
                    </div>";
            }
          ?>
      </div>
    </div>
  </div>
</div>
<!-- history pupuk end -->