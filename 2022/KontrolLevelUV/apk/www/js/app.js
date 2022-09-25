let $devReady;
let $mainOk;
let $errMsg;
let $errStat;
let $notifState;
let $stream;
let $serverReady;

const $serverUrl = 'http://localhost:5000';
const $detectionEventSourceRoute = '/api/stream';
const $imageStreamRoute = '/imagestream';
const $imageRoute = '/image';
const $logsUrl = '/kontroluv/api/index.php/loadlogs';

const $storage = window.localStorage;
const $ = Dom7;
const $device = Framework7.getDevice();
const $app = new Framework7({
  name: 'Kontrol UV', // App name
  theme: 'md', // Automatic theme detection
  autoDarkTheme: true,
  el: '#app', // App root element

  id: 'id.ac.plnm.kontroluv', // App bundle ID
  // App routes
  routes: routes,
  
  calendar: {
    dateFormat: 'dd-mm-yyyy',
  },
  
  // panel
  panel: {
    swipe: true,
    swipeNoFollow: true,
  },
  // Input settings
  input: {
    scrollIntoViewOnFocus: $device.cordova && !$device.electron,
    scrollIntoViewCentered: $device.cordova && !$device.electron,
  },
  // Cordova Statusbar settings
  statusbar: {
    iosOverlaysWebView: true,
    androidOverlaysWebView: false,
  },
  on: {
    init: function () {
      let f7 = this;
      if (f7.device.cordova) {
        // Init cordova APIs (see cordova-app.js)
        cordovaApp.init(f7);
      }
      $devReady = true;
    },
  },
});

const checkProtocol = (url) => url.replace(/^(?:(.*:)?\/\/)?(.*)/i, (match, schemma, nonSchemaUrl) => (schemma ? match : `http://${nonSchemaUrl}`));

const urls = () => {
  let l = document.createElement('a');
  l.href = $serverUrl + $logsUrl;
  l = l.protocol + '//' + l.hostname + $logsUrl;
  return {
    server: $serverUrl,
    logsUrl: l,
    image: $serverUrl + $imageRoute,
    imageStream: $serverUrl + $imageStreamRoute,
    detection: $serverUrl + $detectionEventSourceRoute
  }
}

function showAlert(msgs, header, exit = false) {
  const $errMsgTmp = msgs;
  if ($errMsg !== $errMsgTmp) {
    $errMsg = $errMsgTmp;
    $app.dialog.alert(msgs, header, () => {
      if (exit) {
        if (typeof cordova === 'undefined') {
          window.close();
        }
        if (navigator.app) {
          navigator.app.exitApp();
        } else if (navigator.device) {
          navigator.device.exitApp();
        }
      }
      $errStat = false;
    });
  }
}

const $appData = {
  prefsData: {
    serverUrl: $serverUrl,
    logsUrl: $logsUrl,
    imageRoute: $imageRoute,
    imageStreamRoute: $imageStreamRoute,
    detectionEventSourceRoute: $detectionEventSourceRoute,
  },

  config: {
    mode: 0, // 0 nativestorage, 1 localstorage
    isExist: false,
  },

  initialize: () => {
    $appData.checkConfig();
  },

  checkConfig: () => {
    if ($app.device.cordova) {
      NativeStorage.setItem('dummy',
        { dummy: true },
        (_param) => {
          console.info('Set appData mode: 0');
          $appData.config.mode = 0;
          NativeStorage.getString('prefsData',
            (result) => {
              console.info(`Current Stored Value was: ${JSON.parse(result)}`);
              $appData.config.isExist = true;
            },
            (e) => {
              console.error(`Read data failed: ${e.message}`);
              $appData.config.isExist = false;
            });
        },
        (_param) => {
          console.error('Error loading nativeStorage');
          console.info('Set appData mode: 1');
          $appData.config.mode = 1;
          const data = JSON.parse($storage.getItem('prefsData'));
          if (data) {
            $appData.config.isExist = true;
          } else {
            $appData.config.isExist = false;
          }
        });
    } else {
      console.info('Set appData mode: 1');
      $appData.config.mode = 1;
      const data = JSON.parse($storage.getItem('prefsData'));
      if (data) {
        //console.info(`Current Stored Value was: ${$storage.getItem('prefsData')}`);
        $appData.config.isExist = true;
      } else {
        $appData.config.isExist = false;
      }
    }
  },

  updateData: (newData) => {
    $appData.prefsData = newData;
    $appData.saveData();
  },

  saveData: () => {
    if ($appData.config.mode === 0) {
      NativeStorage.setItem('prefsData',
        JSON.stringify($appData.prefsData),
        (result) => {
          console.info(`Saved data: ${result}`);
        },
        (e) => {
          console.error(`Write data failed: ${e.message}`);
        });
    } else {
      $storage.setItem('prefsData', JSON.stringify($appData.prefsData));
      // console.info(`Saved data: ${JSON.stringify($appData.prefsData)}`);
    }
  },

  loadData: () => {
    if ($appData.config.isExist) {
      if ($appData.config.mode === 0) {
        NativeStorage.getString('prefsData',
          (result) => {
            console.info(`Current Stored Value was: ${result}`);
            $appData.prefsData = JSON.parse(result);
          },
          (e) => {
            console.error(`Read data failed: ${e.message}`);
          });
      } else {
        $appData.prefsData = JSON.parse($storage.getItem('prefsData'));
        // console.info(`Current Stored Value was: ${JSON.stringify($appData.prefsData)}`);
      }
    } else {
      console.error('Read data failed! Resetting data...');
      $appData.saveData();
    }
  },
};

function consoleToast(str) {
  // Create bottom toast
  if (!$app.device.cordova) {
    const toastBottom = $app.toast.create({
      text: str,
      closeTimeout: 2000,
    });
    toastBottom.open();
  }
}

// notifications
function addNotification(headerStr, bodyStr) {
  if ($app.device.cordova && $notifState === false) {
    cordovaApp.addNotification(headerStr, bodyStr);
    console.log('Notification added.');
    $notifState = true;
    // consoleToast('Notification added.');
    console.log(`Notif: ${headerStr}, ${bodyStr}`);
  } else {
    consoleToast(`Notif: ${headerStr}, ${bodyStr}`);
  }
  // let loc = window.location.pathname;
  // let dir = loc.substring(0, loc.lastIndexOf('/'));
  // ////consoleToast('Loc:' + loc + ' Dir:' + dir);
  // console.log('Loc:' + loc + ' Dir:' + dir);
}

/* overrides */
window.onerror = (msg, url, line) => {
  $errStat = true;
  const msgs = `Message: ${msg}<br>
    Line number: ${line}<br>
    Url: ${url}`;
  // Alert
  showAlert(msgs, 'Error');
};

function setErrorImage(img) { // (used in index.html)
  img.onerror = () => {};
  img.src = './assets/404.png';
  img.alt = '404 image';
  $serverReady = false;
}

function refreshImagesStream() {
  $('#camera-container').html(`<img id='camera-stream'
    src='${urls().imageStream}'
    alt='Image Stream'
    style='width:82vw;'
    onerror='setErrorImage(this)' />`);
}

function fetchImage() {
  fetch(urls().image, {
    method: 'GET', // *GET, POST, PUT, DELETE, etc.
    // mode: 'no-cors',
  })
    .then((response) => {
      if (!response.ok) {
        console.error('Network response was not ok');
        $serverReady = false;
        refreshImagesStream();
      } else {
        // console.log('Internet connection available');
        $serverReady = true;
        refreshImagesStream();
      }
    })
    .catch((e) => {
      console.error('No Internet connection', e.message);
      $serverReady = false;
      refreshImagesStream();
    });
}

function checkConnection() {
  // check every 8000ms
  setInterval(() => {
    // connection timeout 2000ms
    setTimeout(fetchImage(), 2000);
  }, 8000);
}


async function getLogs(date) {
  return new Promise(resolve => {
    const offset = date[0].getTimezoneOffset();
    date = new Date(date[0].getTime() - (offset * 60 * 1000));
    date = date.toISOString().split('T')[0];
    let xhr = new XMLHttpRequest();
    try{
       // Opera 8.0+, Firefox, Chrome, Safari
       xhr = new XMLHttpRequest();
    }catch (e) {
       // Internet Explorer Browsers
       try{
        xhr = new ActiveXObject("Msxml2.XMLHTTP");
       }catch (e) {
        try{
         xhr = new ActiveXObject("Microsoft.XMLHTTP");
        }catch (e) {
         // Something went wrong
         consoleToast("Your browser broke!");
         return {};
        }
       }
    }

    let logsUrl = urls().logsUrl + '?date=' + date;
    xhr.open("GET", logsUrl, false);
    xhr.setRequestHeader("Content-type", "text/html");
    xhr.onload =  function () {
      resolve(JSON.parse(xhr.responseText));
    }
    xhr.onerror = function () {
      resolve(undefined);
    }
    xhr.send(null);
  });
}



/* main */

const main = () => {
  $appData.initialize();
  if ($appData.config.isExist) {
    $appData.loadData();
    serverUrl = $appData.prefsData.serverUrl;
  }

  checkConnection();
  $mainOk = true;
};

const waitDevReady = () => {
  setInterval(() => {
    if ($devReady) {
      if (!$mainOk) {
        main();
      }
      clearInterval(waitDevReady);
    }
  }, 1500);
};

waitDevReady();

/* end */
