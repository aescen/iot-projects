<!-- PHP.MySQL.START -->
<?php
require_once 'inits.php';
require_once 'db.php';

$sql = "SELECT * FROM `pantauternak`";
?>
<!-- PHP.MySQL.END -->
<div class='w3-card-4 w3-white'>
  <table class='w3-table w3-striped w3-white w3-centered'>
    <thead>
      <tr class='w3-teal'>
        <td rowspan="2" style='vertical-align: middle;'>ID</td>
        <td rowspan="2" style='vertical-align: middle;'>Berat</td>
        <td rowspan="2" style='vertical-align: middle;'>Suhu</td>
        <td rowspan="2" style='vertical-align: middle;'>Waktu</td>
        <td rowspan="2" style='vertical-align: middle;'>Harga</td>
        <td colspan="2" style='vertical-align: middle;'>Gambar</td>
        <td rowspan="2" style='vertical-align: middle;'></td>
      </tr>
      <tr class='w3-teal'>
        <td style='vertical-align: middle;'>Kambing</td>
        <td style='vertical-align: middle;'>Sertifikat</td>
      </tr>
    </thead>
    <tbody>
      <?php
      $result = $conn->query($sql);
      if ($result->num_rows > 0) {
        while ($row = $result->fetch_assoc()) {
          $buyItem = 'buyItem(' .
            '&quot;' . $row['id'] . '&quot;' . ',' .
            '&quot;' . $row['berat'] . '&quot;' . ',' .
            '&quot;./imgs/' . $row['img_path'] . '&quot;' . ',' .
            '&quot;' . $formatter->formatCurrency($row["Harga"], 'IDR') . '&quot;' .
            ');';
          echo "
              <tr'>
                <td style='vertical-align: middle;'>" . $row["id"] . "</td>
                <td style='vertical-align: middle;'>" . $row["berat"] . "kg</td>
                <td style='vertical-align: middle;'>" . $row["suhu"] . "&deg;C</td>
                <td style='vertical-align: middle;'>" . $row["time_stamp"] . "</td>
                <td style='vertical-align: middle;'>" . $formatter->formatCurrency($row["Harga"], 'IDR') . "</td>
                <td style='vertical-align: middle;'><a href=#'><img id='img-" . $row["img_path"] .
            "'src='./imgs/" . $row["img_path"] .
            "' alt='img-" . $row["img_path"] .
            "' width='90px' height='68px' class='w3-center w3-middle w3-padding'></a></td>
            <td style='vertical-align: middle;'><a href=#'><img id='img-" . $row["img_cert"] .
            "'src='./imgs/" . $row["img_cert"] .
            "' alt='img-" . $row["img_cert"] .
            "' width='90px' height='68px' class='w3-center w3-middle w3-padding'></a></td>
                <td style='display: flex; justify-content: center; align-items: center;'>
                  <div style='width: 100%; height: 100%; margin: 0; padding: 1rem;'>
                    <button
                      class='w3-button w3-teal'
                      style='vertical-align: middle;'
                      onclick='" . $buyItem . "');'
                    >
                      Beli
                    </button>
                  </div>
                </td>
              </tr>";
        }
      } else {
        echo "0 results";
      }
      ?>
    </tbody>
  </table>
</div>
<div id="divLargerImage"></div>
<div id="divOverlay"></div>
<script>
  var thw = new SupportVhVw();
  $('a img').click(function() {
    var $img = $(this);
    $('#divLargerImage').html($img.clone().height(480).width(640)).add($('#divOverlay')).fadeIn();
  });

  $('#divLargerImage').add($('#divOverlay')).click(function() {
    $('#divLargerImage').add($('#divOverlay')).fadeOut(function() {
      $('#divLargerImage').empty();
    });
  });
</script>