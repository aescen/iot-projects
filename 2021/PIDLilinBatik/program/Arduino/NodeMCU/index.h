const char index_html[] PROGMEM = R"=====(
<!doctype html>
<html lang="en">
<head>
 <meta charset="utf-8" />
 <meta name="viewport" content="width=device-width" />
 <title>PID Tungku</title>
 <meta name="description" content="PID Tungku">
 <meta name="author" content="AHMAD AFIF MUDHOFAR">
 <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.2.0/chart.min.js"></script>
 <link rel="icon" type="image/png"
  href="https://www.liquidinstruments.com/wp-content/uploads/2019/10/icon-instrument-03-PID@2x.png">
 <style>
  canvas {
   -webkit-user-select: auto;
   -ms-user-select: auto;
   user-select: auto;
  }
  #dataTable {
   font-family: "Trebuchet MS", Arial, Helvetica, sans-serif;
   border-collapse: collapse;
   width: 100%;
  }
  #dataTable td,
  #dataTable th {
   border: 1px solid #ddd;
   padding: 8px;
  }
  #dataTable tr:nth-child(even) {
   background-color: #f2f2f2;
  }
  #dataTable tr:hover {
   background-color: #ddd;
  }
  #dataTable th {
   padding-top: 12px;
   padding-bottom: 12px;
   text-align: left;
   background-color: #4CAF50;
   color: white;
  }
  .download-wrapper {
   cursor: pointer;
   margin-top: -100px;
  }
  .download-wrapper:hover {
   opacity: 0.7;
  }
  .download-wrapper i.material-icons {
   font-size: 30px;
   color: #fff;
   height: 30px;
   width: 30px;
   margin: auto;
   display: block;
  }
  .download-wrapper p {
   text-align: center;
   color: #fff;
   margin: auto;
   height: 30px;
   font-size: 22px;
   font-family: "Abel", sans-serif;
  }
 </style>
</head>
<body>
 <div style="text-align:center;"><br>ANALISIS PERFORMANCE</b><br>SISTEM KONTROL PID UNTUK OTOMASI
  KENDALI</b><br>TEMPERATURE TUNGKU PENCAIR LILIN BATIK</div>
 <div style="text-align:center;">SKRIPSI OLEH :<br>AHMAD AFIF MUDHOFAR</div>
 <div class="chart-container" style="position: relative; height:350px;width:100%"><canvas id="Chart" width="400"
   height="400"></canvas></div>
 <div>
  <table id="dataTable">
   <tr>
    <th>Suhu (&deg;C)</th>
    <th>PID</th>
    <th>Eror</th>
    <th>Sudut</th>
    <th>Waktu</th>
    <th>Keterangan (<span class="download-wrapper" onclick="downloadCSV()">Download CSV</span>)</th>
   </tr>
  </table>
 </div>
 <br>
 <br>
 <script>
  var tableTitle = 'Data-Kontrol-PID';
  var tableHeaders = {
   temp: "Suhu (*C)",
   pid: "PID",
   error: "Error",
   angle: "Sudut",
   clock: "Waktu",
   constants: "Keterangan",
  };
  var tableItems = [];
  const table = document.getElementById("dataTable");
  const ctx = document.getElementById("Chart").getContext('2d');
  const chart = new Chart(ctx, {
   type: 'line',
   data: {
    labels: [],
    datasets: [{
     label: "TEMPERATURE",
     fill: false,
     backgroundColor: 'rgba( 243, 156, 18 , 1)',
     borderColor: 'rgba( 243, 156, 18 , 1)',
     data: [],
    }],
   },
   options: {
    interaction: {
     mode: 'dataset'
    },
    responsive: true,
    animation: {
     duration: 1500,
    },
    hover: {
     animationDuration: 1500,
    },
    responsiveAnimationDuration: 1500,
    title: {
     display: true,
    },
    maintainAspectRatio: false,
    elements: {
     line: {
      tension: 0.5
     }
    },
    scales: {
     yAxes: [{
      ticks: {
       beginAtZero: true
      }
     }],
     y: {
      display: true,
      type: 'logarithmic'
     }
    }
   }
  });
  function addData(chart, label, data) {
   chart.data.labels.push(label);
   chart.data.datasets.forEach((dataset) => {
    dataset.data.push(data);
   });
   chart.update();
  }
  function getData() {
   const xhttp = new XMLHttpRequest();
   xhttp.onreadystatechange = function () {
    if (this.readyState == 4 && this.status == 200) {
     const jsonObj = JSON.parse(this.responseText);
     tableItems.push(jsonObj);
     addData(chart, jsonObj.clock, jsonObj.temp);
     let row = table.insertRow(1);
     let cell1 = row.insertCell(0);
     let cell2 = row.insertCell(1);
     let cell3 = row.insertCell(2);
     let cell4 = row.insertCell(3);
     let cell5 = row.insertCell(4);
     let cell6 = row.insertCell(5);
     cell1.innerHTML = jsonObj.temp;
     cell2.innerHTML = jsonObj.pid;
     cell3.innerHTML = jsonObj.error;
     cell4.innerHTML = jsonObj.angle;
     cell5.innerHTML = jsonObj.clock;
     cell6.innerHTML = jsonObj.constants;
    }
   };
   xhttp.open("GET", "datas", true);
   xhttp.send();
  }
  setInterval(function () {
   getData();
  }, 1000);
  function convertToCSV(objArray) {
   var array = typeof objArray != 'object' ? JSON.parse(objArray) : objArray;
   var str = '';
   for (var i = 0; i < array.length; i++) {
    var line = '';
    for (var index in array[i]) {
     if (line != '') line += ','
     line += array[i][index];
    }
    str += line + '\r\n';
   }
   return str;
  }
  function exportCSVFile(headers, items, fileTitle) {
   if (headers) {
    items.unshift(headers);
   }

   // Convert Object to JSON
   var jsonObject = JSON.stringify(items);

   var csv = this.convertToCSV(jsonObject);

   var exportedFilenmae = fileTitle + '.csv' || 'export.csv';

   var blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
   if (navigator.msSaveBlob) { // IE 10+
    navigator.msSaveBlob(blob, exportedFilenmae);
   } else {
    var link = document.createElement("a");
    if (link.download !== undefined) { // feature detection
     // Browsers that support HTML5 download attribute
     var url = URL.createObjectURL(blob);
     link.setAttribute("href", url);
     link.setAttribute("download", exportedFilenmae);
     link.style.visibility = 'hidden';
     document.body.appendChild(link);
     link.click();
     document.body.removeChild(link);
    }
   }
  }
  function downloadCSV() {
   exportCSVFile(tableHeaders, tableItems, tableTitle);
  }
 </script>
</body>
</html>
)=====";
