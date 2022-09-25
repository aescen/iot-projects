/* eslint-disable no-use-before-define */
/* eslint-disable eqeqeq */
/* eslint-disable no-undef */
const $$ = Dom7;
const $$enableNotif = false;
const $$debugMode = false;
let $$data;
let $$fbI;
let $$fbO;
let $$db;
let $$err = false;
let $$devReady = false;
// let $$notif = false;
const $$ROOT_PATH = '/IkanAsin/';
const $$STR_ON = 'ON';
const $$STR_OFF = 'OFF';
const $$STR_TERANG = 'TERANG';
const $$STR_GELAP = 'GELAP';
const $$STR_PROCESS = 'PROSES PENGERINGAN';
const $$STR_DONE = 'PENGERINGAN SELESAI';

const app = new Framework7({
  root: '#app', // App root element

  id: 'id.ac.plnm.monitoring.pengering.ikanasin', // App bundle ID
  name: 'Pengering Ikan Asin', // App name
  theme: 'md', // Automatic theme detection
  autoDarkTheme: false,
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

  // App routes
  routes,

  // Input settings
  input: {
    scrollIntoViewOnFocus: Framework7.device.cordova && !Framework7.device.electron,
    scrollIntoViewCentered: Framework7.device.cordova && !Framework7.device.electron,
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
    },
    pageInit() {
      console.log('Page initialized');
      $$devReady = true;
      refOnce();
    },
  },
});

app.views.create('.view-main', {
  url: '/',
});

window.onerror = (msg, url, line) => {
  $$err = true;
  app.preloader.hide();
  const msgs = `Message : ${msg}<br>Line number : ${line}<br>Url : ${url}`;
  // Alert
  app.dialog.alert(msgs, 'Error', () => {
    if (!$$debugMode) {
      if (typeof cordova !== 'undefined') {
        if (navigator.app) {
          navigator.app.exitApp();
        } else if (navigator.device) {
          navigator.device.exitApp();
        }
      } else {
        window.close();
      }
    }
  });
};

// notifications
// eslint-disable-next-line no-unused-vars
function addNotification(headerStr, bodyStr) {
  if ($$enableNotif) {
    if (app.device.cordova && $$notif == false) {
      cordovaApp.addNotification(headerStr, bodyStr);
      console.log('Notification added.');
      $$notif = true;
      // consoleToast("Notification added.");
      console.log(`Notif: ${headerStr}:${bodyStr}`);
    } else {
      consoleToast(`Notif: ${headerStr}:${bodyStr}`);
    }
  }
}

function consoleToast(str) {
  // Create bottom toast
  if (!app.device.cordova) {
    const toastBottom = app.toast.create({
      text: str,
      closeTimeout: 2000,
    });
    toastBottom.open();
  }
}

// function map(x, inMin, inMax, outMin, outMax) {
//   return ((x - inMin) * (outMax - outMin)) / (inMax - inMin) + outMin;
// }

function updateUI(id, val) {
  try {
    if (typeof val === 'function') {
      document.getElementById(`val-${id}`).innerHTML = val();
    } else {
      document.getElementById(`val-${id}`).innerHTML = val;
    }
    document.getElementById(`img-${id}`).src = `assets/${id}.png`;
  } catch (error) {
    console.error(error);
    document.getElementById(`img-${id}`).src = `assets/${id}-grey.png`;
    if (!(error instanceof TypeError)) {
      throw error;
    }
  }
}

// Initialize Firebase
function fbInit() {
  const config = {
    // config here
  };
  // Initialize Firebase
  firebase.initializeApp(config);

  $$db = firebase.database();
  $$fbI = true;
  console.log('fbInit');
}

function fbOn() {
  /* obtain data when app is starting or data is updated */
  $$db.ref($$ROOT_PATH).on('value', (snapshot) => {
    $$data = snapshot.val();
    // console.log($$data);

    updateUI('temp', () => $$data.temp);
    updateUI('humid', () => $$data.humid);
    //updateUI('lux', () => $$data.lux);
    updateUI('lux', () => (parseInt($$data.cahaya, 10) > 0 ? $$STR_TERANG : $$STR_GELAP));
    updateUI('fan', () => (parseInt($$data.fan, 10) > 0 ? $$STR_ON : $$STR_OFF));
    updateUI('heater', () => (parseInt($$data.heater, 10) > 0 ? $$STR_ON : $$STR_OFF));
    updateUI('dryer', () => (parseInt($$data.pengeringan, 10) > 0 ? $$STR_PROCESS : $$STR_DONE));

    console.log('fbOn');

    app.preloader.hide();
    $$fbO = true;
  }, (error) => {
    console.error(error);
  });
}

/* obtain data once */
function refOnce() {
  if (!$$err && $$devReady) {
    if (!$$fbI) {
      fbInit();
      if (!$$fbO) {
        fbOn();
      }
    } else {
      $$db.ref($$ROOT_PATH).once('value').then(
        (snapshot) => {
          $$data = snapshot.val();
          // console.log($$data);

          updateUI('temp', () => $$data.temp);
          updateUI('humid', () => $$data.humid);
          //updateUI('lux', () => $$data.lux);
          updateUI('lux', () => (parseInt($$data.cahaya, 10) > 0 ? $$STR_TERANG : $$STR_GELAP));
          updateUI('fan', () => (parseInt($$data.fan, 10) > 0 ? $$STR_ON : $$STR_OFF));
          updateUI('heater', () => (parseInt($$data.heater, 10) > 0 ? $$STR_ON : $$STR_OFF));
          updateUI('dryer', () => (parseInt($$data.pengeringan, 10) > 0 ? $$STR_PROCESS : $$STR_DONE));

          console.log('fbOnce');
          app.preloader.hide();
        },
      );
    }
  } else {
    console.log('Error/device not ready.');
    // consoleToast("Error/device not ready.");
    app.preloader.hide();
  }
}

// Pull to refresh content
const $ptrContent = $$('.ptr-content');
// eslint-disable-next-line no-unused-vars
$ptrContent.on('ptr:refresh', (event) => {
  setTimeout(() => {
    $$db.ref($$ROOT_PATH).once('value').then(
      (snapshot) => {
        $$data = snapshot.val();
        // console.log($$data);

        updateUI('temp', () => $$data.temp);
        updateUI('humid', () => $$data.humid);
        //updateUI('lux', () => $$data.lux);
        updateUI('lux', () => (parseInt($$data.cahaya, 10) > 0 ? $$STR_TERANG : $$STR_GELAP));
        updateUI('fan', () => (parseInt($$data.fan, 10) > 0 ? $$STR_ON : $$STR_OFF));
        updateUI('heater', () => (parseInt($$data.heater, 10) > 0 ? $$STR_ON : $$STR_OFF));
        updateUI('dryer', () => (parseInt($$data.pengeringan, 10) > 0 ? $$STR_PROCESS : $$STR_DONE));
      },
    );
    console.log('ptr done...');
    consoleToast('Updated.');
    app.ptr.done();
  }, 2000);
});
