// HTML web page to handle input field json
const char index_html[] PROGMEM = R"rawliteral(
  <!DOCTYPE HTML><html><head>
  <html>
    <head>
      <title>ESP BISINDO-KIRI</title>
      <meta name="viewport" content="width=device-width, initial-scale=1" charset="UTF-8">
      <style>
        form {
          text-align: center;
        }.colform { 
          float:left;
          width:33.333%;
        }
      </style>
      <script>
        function submitMessage() {
          alert("Json saved to ESP SPIFFS");
          setTimeout(function(){ document.location.reload(false); }, 500);
        }
      </script>
    </head>
    <body>
      <form action="" target="hiddenform" method="get" id="jsoninput">
        <textarea form="jsoninput" id="inputJson" name="inputJson" placeholder="Type, paste, cut text here..." style="min-width:500px;max-width:100%;min-height:300px;height:100%;width:99%;"></textarea><br>
        <input type="submit" value="Submit" onclick="submitMessage()">
      </form>
      <br>
      <div>
        <form action="" class="colform" target="hiddenform" method="GET" id="recalibrateflex" onsubmit="return confirm('Do you want to recalibrate Flex sensor?');">
          <input type="submit" value="Recalibrate Flex" id="inputRecalibrateFlex" name="inputRecalibrateFlex">
        </form>
          <form action="" class="colform" target="hiddenform" method="GET" id="recalibratempu" onsubmit="return confirm('Do you want to recalibrate MPU sensor?');">
          <input type="submit" value="Recalibrate MPU" id="inputRecalibrateMPU" name="inputRecalibrateMPU">
        </form>
          <form action="" class="colform" target="hiddenform" method="GET" id="recalibrateall" onsubmit="return confirm('Do you want to recalibrate all sensor?');">
          <input type="submit" value="Recalibrate All" id="inputRecalibrateAll" name="inputRecalibrateAll">
        </form>
      </div>
      <iframe style="display:none" name="hiddenform" id="hiddenform"></iframe>
    </body>
   </html>
)rawliteral";
