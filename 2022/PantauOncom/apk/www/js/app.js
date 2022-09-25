const $mockData = {
  color: {
    r: 123,
    g: 12,
    b: 1,
  },
  session: 'Terhenti',
  moist: 12.3,
  temp: 23.4,
};
const $sessionInfo = {
  isEnded: 'Selesai', // 0
  isStarted: 'Berjalan', // 1
  isStopped: 'Terhenti', // 2
};

const $rootPath = 'jtd/Oncom';
const $sessionPath = 'jtd/Oncom/session';
const $serverurlPath = 'jtd/Oncom/serverurl';
const $isFlipedPath = 'jtd/Oncom/isFlipped';
const $isLiftedPath = 'jtd/Oncom/isLifted';
let $currentSession = '...';
let $fbI;
let $fbO;
let $firebaseApp;
let $storage;
let $db;
let $errMsg;
let $errStat;
let $devReady;
let $mainOk;
let $notifState = true;

let $serverUrl = 'http://localhost:8080';

const $detectionEventSourceRoute = '/api/stream';
const $imageStreamRoute = '/imagestream';
const $imageRoute = '/image';

const $urls = {
  server: $serverUrl,
  image: $serverUrl + $imageRoute,
  imageStream: $serverUrl + $imageStreamRoute,
}


const $ = Dom7;
const $device = Framework7.getDevice();
const $app = new Framework7({
  name: 'Pantau Oncom', // App name
  theme: 'md', // Automatic theme detection
  autoDarkTheme: false,
  el: '#app', // App root element

  id: 'id.ac.plnm.monitoring.oncom', // App bundle ID
  // App store
  // store: store,
  // App routes
  routes,

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
      let f7 = this;
      if (f7.device.cordova) {
        cordovaApp.init(f7);
      }
      $devReady = true;
      // useMock();
    },
  },
});

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
          navigator.$app.exitApp();
        } else if (navigator.device) {
          navigator.$device.exitApp();
        }
      }
      $errStat = false;
    });
  }
}

function consoleToast(str) {
  // Create bottom toast
  if (!$app.device.cordova) {
    const toastBottom = $app.toast.create({
      text: str,
      closeTimeout: 1234,
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
    console.log(`Notif: ${headerStr}, ${bodyStr}`);
  } else {
    $notifState = true;
    consoleToast(`Notif: ${headerStr}, ${bodyStr}`);
  }
}

function useMock() {
  const color = `RGB ( ${$mockData.color.r}, ${$mockData.color.g}, ${$mockData.color.b} )`;
  document.getElementById('color').innerHTML = color.replace(/\s/g, '');
  document.getElementById('color-style').style.backgroundColor = color.replace(/\s/g, '');
  document.getElementById('moist').innerHTML = $mockData.moist;
  document.getElementById('temp').innerHTML = $mockData.temp;
  document.getElementById('info').innerHTML = $mockData.session;

  document.getElementById('img-color').src = 'assets/color.png';
  document.getElementById('img-info').src = 'assets/info.png';
  document.getElementById('img-hairdryer').src = 'assets/hairdryer.png';
  document.getElementById('img-moist').src = 'assets/moist.png';
  document.getElementById('img-temp').src = 'assets/temp.png';
}

function writeServerUrl(url) {
  let updates = {};  
  updates[$serverurlPath] = url;
  return $db.ref().update(updates);
}

function startSession() {
  $('#start-session').addClass('button-fill');
  document.querySelector('#start-session').innerText = 'Proses';
}

function sessionFlipped() {
  let updates = {};  
  updates[$isFlipedPath] = false;
  $('#start-session').addClass('color-orange');
  $('#start-session').addClass('button-fill');
  document.querySelector('#start-session').innerText = 'Proses';
  return $db.ref().update(updates);
}

function stopSession() {
  let updates = {};  
  updates[$isFlipedPath] = false;
  updates[$isLiftedPath] = false;
  document.querySelector('#start-session').innerText = 'Mulai';
  $('#start-session').removeClass('button-fill');
  $session = 0;
  return $db.ref().update(updates);
}

function writeSessionData(mode) {
  let updates = {};
  if (parseInt(mode) === 1) {
    if ($currentSession === $sessionInfo.isEnded || $currentSession === $sessionInfo.isStopped) {
      $app.dialog.confirm('Mulai sesi fermentasi baru?', 'Perhatian!', () => {
        $currentSession = $sessionInfo.isStarted;
        updates[$sessionPath] = $currentSession;
        // updates[$sessionPath] = Number(1);
        return $db.ref().update(updates);
      });
    }
  }

  if (parseInt(mode) === 0) {
    if ($currentSession === $sessionInfo.isStarted) {
      $app.dialog.confirm('Hentikan sesi yang sedang berjalan?', 'Peringatan!', () => {
        $currentSession = $sessionInfo.isStopped;
        updates[$sessionPath] = $currentSession;
        // updates[$sessionPath] = Number(2);
        
      });
    }
  }
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

// Initialize Firebase
function fbInit() {
  const config = {
    // config here
  };
  // Initialize Firebase
  $firebaseApp = firebase.initializeApp(config);

  $db = firebase.database();
  $storage = firebase.storage();
  $fbI = true;
  // console.log('fbInit');
}

function fbOn(reset = false) {
  /* obtain data when app is starting or data is updated */
  if (reset) $db.ref($rootPath).off();
  $db.ref($rootPath).on(
    'value',
    (snapshot) => {
      $data = snapshot.val();
      // console.log($data);

      const color = `RGB ( ${$data.color.r}, ${$data.color.g}, ${$data.color.b} )`;
      try {
        document.getElementById('color').innerHTML = color.replace(/\s/g, '');
        document.getElementById('moist').innerHTML = $data.moist;
        document.getElementById('temp').innerHTML = $data.temp;
        document.getElementById('info').innerHTML =
          $data.session[0].toUpperCase() + $data.session.slice(1);
        document.getElementById('hairdryer').innerHTML =
          $data.hairdryer[0].toUpperCase() + $data.hairdryer.slice(1);

        document.getElementById('img-color').src = 'assets/color.png';
        document.getElementById('img-info').src = 'assets/info.png';
        document.getElementById('img-hairdryer').src = 'assets/hairdryer.png';
        document.getElementById('img-moist').src = 'assets/moist.png';
        document.getElementById('img-temp').src = 'assets/temp.png';
        document.getElementById('cam-moist').innerHTML = $data.moist;
        document.getElementById('cam-temp').innerHTML = $data.temp;
        document.getElementById('url-server').innerText = $data.serverurl;
        
        if ($serverUrl !== $data.serverurl) {
          $serverUrl = $data.serverurl;
          $urls.server = $serverUrl;
          $urls.image = $serverUrl + $imageRoute;
          $urls.imageStream = $serverUrl + $imageStreamRoute;
          refreshImagesStream();
        }
      } catch (error) {
        console.warn(error);
      }

      $currentSession = $data.session;

      /*
      // isStarted
      if ($data.session === $sessionInfo.isStarted) {
        $('#start-session').removeClass('button-active');
        $('#stop-session').addClass('button-active');
      }

      // isStopped or isEnded
      if ($data.session === $sessionInfo.isEnded || $data.session === $sessionInfo.isStopped) {
        $('#stop-session').removeClass('button-active');
        $('#start-session').addClass('button-active');
      }
      */
      
      if ($data.isFlipped && $notifState) {
        $notifState = false;
        addNotification('Pantau Oncom', 'Waktunya dibalik!');
        $('#start-session').removeClass('color-orange');
        $('#start-session').addClass('color-blue');
        $('#start-session').addClass('button-fill');
        document.querySelector('#start-session').removeEventListener('click', ()=>false);
        document.querySelector('#start-session').addEventListener('click', ()=>{
          sessionFlipped();
        });
      } else if ($data.isLifted && $notifState) {
        $notifState = false;
        addNotification('Pantau Oncom', 'Waktunya diangkat!');
        $('#start-session').removeClass('color-blue');
        $('#start-session').addClass('color-orange');
        $('#start-session').addClass('button-fill');
        document.querySelector('#start-session').removeEventListener('click', ()=>false);
        document.querySelector('#start-session').addEventListener('click', ()=>{
          startSession();
        });
      } else {
        $('#start-session').removeClass('color-blue');
        $('#start-session').addClass('color-orange');
      }

      // console.log('fbOn');

      $app.preloader.hide();
      $fbO = true;
    },
    (error) => {
      console.error(error);
    },
  );

  /* $storage
    .ref()
    .child('mountain_and_sea.jpg')
    .getDownloadURL()
    .then((url) => {
      const img = document.getElementById('img-test');
      img.setAttribute('src', url);
    })
    .catch((error) => {
      console.log(error);
    });
  */
}

function refOnce() {
  if (!$errStat && $devReady) {
    if (!$fbI) {
      fbInit();
      if (!$fbO) {
        fbOn();
      }
    } else {
      $db
        .ref($rootPath)
        .once('value')
        .then((snapshot) => {
          $data = snapshot.val();
          // console.log($data);

          const color = `RGB ( ${$data.color.r}, ${$data.color.g}, ${$data.color.b} )`;
          try {
            document.getElementById('color').innerHTML = color.replace(/\s/g, '');
            document.getElementById('moist').innerHTML = $data.moist;
            document.getElementById('temp').innerHTML = $data.temp;
            document.getElementById('info').innerHTML =
              $data.session[0].toUpperCase() + $data.session.slice(1);
            document.getElementById('hairdryer').innerHTML =
              $data.hairdryer[0].toUpperCase() + $data.hairdryer.slice(1);

            document.getElementById('img-color').src = 'assets/color.png';
            document.getElementById('img-info').src = 'assets/info.png';
            document.getElementById('img-hairdryer').src = 'assets/hairdryer.png';
            document.getElementById('img-moist').src = 'assets/moist.png';
            document.getElementById('img-temp').src = 'assets/temp.png';
            document.getElementById('cam-moist').innerHTML = $data.moist;
            document.getElementById('cam-temp').innerHTML = $data.temp;
            document.getElementById('url-server').innerText = $data.serverurl;
            
            if ($serverUrl !== $data.serverurl) {
              $serverUrl = $data.serverurl;
              $urls.server = $serverUrl;
              $urls.image = $serverUrl + $imageRoute;
              $urls.imageStream = $serverUrl + $imageStreamRoute;
              refreshImagesStream();
            }
          } catch (error) {
            console.warn(error);
          }

          $currentSession = $data.session;

          /*
          // isStarted
          if ($data.session === $sessionInfo.isStarted) {
            $('#start-session').removeClass('button-active');
            $('#stop-session').addClass('button-active');
          }

          // isStopped or isEnded
          if ($data.session === $sessionInfo.isEnded || $data.session === $sessionInfo.isStopped) {
            $('#stop-session').removeClass('button-active');
            $('#start-session').addClass('button-active');
          }
          */
          
          if ($data.isFlipped && $notifState) {
            $notifState = false;
            addNotification('Pantau Oncom', 'Waktunya dibalik!');
            $('#start-session').removeClass('color-orange');
            $('#start-session').addClass('color-blue');
            document.querySelector('#start-session').removeEventListener('click', ()=>false);
            document.querySelector('#start-session').addEventListener('click', ()=>{
              sessionFlipped();
            });
          } else if ($data.isLifted && $notifState) {
            $notifState = false;
            addNotification('Pantau Oncom', 'Waktunya diangkat!');
            $('#start-session').removeClass('color-blue');
            $('#start-session').addClass('color-orange');
            document.querySelector('#start-session').removeEventListener('click', ()=>false);
            document.querySelector('#start-session').addEventListener('click', ()=>{
              startSession();
            });
          } else {
            $('#start-session').removeClass('color-blue');
            $('#start-session').addClass('color-orange');
          }

          // console.log('fbOnce');
          $app.preloader.hide();
        });
    }
  } else {
    console.log('Error/device not ready.');
    // consoleToast('Error/device not ready.');
    $app.preloader.hide();
  }
}

function setErrorImage(img) { // (used in index.html)
  img.onerror = () => {};
  img.src = './assets/404.png';
  img.alt = '404 image';
  $serverReady = false;
}

function refreshImages() {
  $('#image-container').html(`<img id='camera-image'
    src='${$urls.image}'
    alt='Image'
    style='width:82vw;'
    onerror='setErrorImage(this)' />`);
}

function refreshImagesStream() {
  $('#camera-container').html(`<img id='camera-stream'
    src='${$urls.imageStream}'
    alt='Image Stream'
    style='width:82vw;'
    onerror='setErrorImage(this)' />`);
}

function fetchImage() {
  fetch(urls.image, {
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

const checkProtocol = (url) => url.replace(/^(?:(.*:)?\/\/)?(.*)/i, (match, schemma, nonSchemaUrl) => (schemma ? match : `http://${nonSchemaUrl}`));

function checkConnection() {
  setInterval(() => {
    setTimeout(fetchImage(), 1000);
  }, 3333);
}

/* main */

const main = () => {
  refOnce();
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
  }, 333);
};

waitDevReady();

/* end */
