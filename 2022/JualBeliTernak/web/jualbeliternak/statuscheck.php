<?php
require_once 'inits.php';
require_once 'db.php';

$sql = "SELECT * FROM `pantauternak`";
?>

<script>
  var dbData = JSON.parse(window.sessionStorage.getItem('dbData'));
  var newDbData = [];
</script>

<?php
$result = $conn->query($sql);
if ($result->num_rows > 0) {
  while ($row = $result->fetch_assoc()) {
    echo "
        <script>
        {
          const newData = {
            id: `" . $row['id'] . "`,
            berat: `" . $row['berat'] . "`,
            suhu: `" . $row['suhu'] . "`,
            time_stamp: `" . $row['time_stamp'] . "`,
            img_path: `" . $row['img_path'] . "`,
          };
          newDbData.push(newData);
        }
        </script>";
  }
}
?>

<script>
  var result = newDbData.filter((item2) => !dbData.find((item1) => (
    item1.id === item2.id &&
    item1.berat === item2.berat &&
    item1.suhu === item2.suhu &&
    item1.time_stamp === item2.time_stamp &&
    item1.img_path === item2.img_path
  )));

  if (result.length !== 0) {
    window.sessionStorage.setItem('dbData', JSON.stringify(newDbData));
    window.sessionStorage.setItem('dataChange', true);
  }
</script>