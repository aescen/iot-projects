/* framework7 app start */

let $fbI;
let $fbO;
let $db;
let $devReady;
let $mainOk;
let $errMsg;
let $errStat;
let $notifState;
let $stream;
let $stateTotalRisky;
let $stateTotalRiskyTmp;
let $serverReady;
let $serverUrl = 'http://localhost:5000';

const $detectionEventSourceRoute = '/api/stream';
const $imageStreamRoute = '/imagestream';
const $imageRoute = '/image';
const $logsRoute = '/api/logs';
const $rootPath = "/Aisya/";
const $headerRisky = 'Status Riskan';
const $riskyStr = 'Jumlah riskan: ';
const $treshRisky = 0;
const $ = Dom7;
const $device = Framework7.getDevice();
const $storage = window.localStorage;
const $app = new Framework7({
  name: 'Si Deteksi', // App name
  theme: 'md', // use 'auto' for Automatic theme detection
  autoDarkTheme: true,
  el: '#app', // App root element
  id: 'id.ac.plnm.deteksijarak', // App bundle ID
  // App routes
  routes,
  
  calendar: {
    dateFormat: 'dd-mm-yyyy'
  },

  // App root data
  data() {
    return {
      foo: 'bar',
    };
  },
  // App root methods
  methods: {
    doSomething() {
      // ...
    },
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
    init() {
      const f7 = this;
      if (f7.device.cordova) {
        // Init cordova APIs (see cordova-app.js)
        cordovaApp.init(f7);
      }
      $devReady = true;
    },
  },
});

/* methods */

const checkProtocol = (url) => url.replace(/^(?:(.*:)?\/\/)?(.*)/i, (match, schemma, nonSchemaUrl) => (schemma ? match : `http://${nonSchemaUrl}`));

const newDate = (id) => {
  let d = new Date(id);
  d = {
    hh: d.getHours(),
    mm: d.getMinutes(),
    ss: d.getSeconds(),
    ms: d.getMilliseconds(),
    DD: d.getDate(),
    MM: d.getMonth() + 1,
    YY: d.getFullYear(),
    day: d.getDay(),
    year: d.getYear(),
    clock: `${d.getHours()}:${d.getMinutes()}`,
    date: `${d.getDate()}-${d.getMonth()+1}-${d.getFullYear()}`,
    datetime: `${d.getDate()}-${d.getMonth()+1}-${d.getFullYear()} ${d.getHours()}:${d.getMinutes()}`,
    hhu: d.getUTCHours(),
    mmu: d.getUTCMinutes(),
    ssu: d.getUTCSeconds(),
    msu: d.getUTCMilliseconds(),
    DDU: d.getUTCDate(),
    MMU: d.getUTCMonth() + 1,
    YYU: d.getUTCFullYear(),
    dayUTC: d.getUTCDay(),
    clockUTC: `${d.getUTCHours()}:${d.getUTCMinutes()}`,
    dateUTC: `${d.getUTCDate()}-${d.getUTCMonth()+1}-${d.getUTCFullYear()}`,
    datetimeUTC: `${d.getUTCDate()}-${d.getUTCMonth()+1}-${d.getUTCFullYear()} ${d.getUTCHours()}:${d.getUTCMinutes()}`,
    time: d.getTime(),
    tz: d.getTimezoneOffset()/60
  }

  return d;
}

const urls = () => {
  return {
    server: $serverUrl,
    logs: $serverUrl + $logsRoute,
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
    logsRoute: $logsRoute,
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

// Initialize Firebase
function fbInit(){
  const config = {
    //
  };
  // Initialize Firebase
  firebase.initializeApp(config);

  $db = firebase.database();
  $fbI = true;
  console.log("fbInit");
}

function getDates(start, end) {
  let date = [];
  
  return dates
}

async function refOnceLogs(dates) {
  if (!$fbI) {
    fbInit();
    if (!$fbO) {
      fbOn();
    }
  }

  let data = [];
  if (dates.end) {
    const ref = $db.ref($rootPath + 'logs/').orderByChild('id')
      .startAt(dates.start.time).endAt(dates.end.time).limitToLast(100);
    await ref.once('value').then(function(snapshot) {
      snapshot.forEach(function(child) {
        data.push(child.val());
      });
    });
  } else {
    const ref = $db.ref($rootPath + 'logs/').orderByChild('id')
      .startAt(dates.start.time).limitToLast(100);
    await ref.once('value').then(function(snapshot) {
      snapshot.forEach(function(child) {
        data.push(child.val());
      });
    });
  }
  return data;
}

function fbOn(reset = false) {
  /* obtain data when app is starting or data is updated */
  if (reset) $db.ref($rootPath + 'events/').off();
  $db.ref($rootPath + 'events/').on("value", function(snapshot) {
    try {
      $('#total-person').html(snapshot.val().person);
      $('#total-person-img').html(snapshot.val().person);
      $('#total-risky').html(snapshot.val().risky_distance);
      $('#total-risky-img').html(snapshot.val().risky_distance);
      $('#total-no-mask').html(snapshot.val().no_mask);
      $('#total-no-mask-img').html(snapshot.val().no_mask);
      $('#total-incorrect-mask').html(snapshot.val().incorrect_mask);
      $('#total-incorrect-mask-img').html(snapshot.val().incorrect_mask);
      $('#total-mask').html(snapshot.val().mask);
      $('#total-mask-img').html(snapshot.val().mask);
      $stateTotalRiskyTmp = (parseInt(snapshot.val().risky, 10) > $treshRisky);

      if ($stateTotalRiskyTmp !== $stateTotalRisky) {
        if ($stateTotalRiskyTmp) {
          $notifState = false;
          addNotification($headerRisky, $riskyStr + snapshot.val().risky);
          refreshImages();
        }
        $stateTotalRisky = $stateTotalRiskyTmp;
      }
      
      $fbO = true;
      console.log("fbOn");
    } catch(e) { console.error(e); }
  }, (error) => {});
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
        refreshImages();
      } else {
        // console.log('Internet connection available');
        $serverReady = true;
        refreshImagesStream();
        refreshImages();
      }
    })
    .catch((e) => {
      console.error('No Internet connection', e.message);
      $serverReady = false;
      refreshImagesStream();
      refreshImages();
    });
}

function checkConnection() {
  // check every 8000ms
  setInterval(() => {
    // connection timeout 1500ms
    setTimeout(fetchImage(), 1500);
  }, 8000);
}

/* main */

const main = () => {
  $appData.initialize();
  if ($appData.config.isExist) {
    $appData.loadData();
    serverUrl = $appData.prefsData.serverUrl;
  }

  checkConnection();
  fbInit();
  fbOn();
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
