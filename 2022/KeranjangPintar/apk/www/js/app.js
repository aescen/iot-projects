/* eslint-disable no-use-before-define */
/* eslint-disable prefer-const */
/* eslint-disable no-unused-vars */
/* eslint-disable no-undef */

let errStats = false;
let errMsg = '';
let $ = Dom7;
let device = Framework7.getDevice();
let app = new Framework7({
  name: 'Smart Cart', // App name
  theme: 'md', // Automatic theme detection
  el: '#app', // App root element
  autoDarkTheme: true,
  id: 'id.ac.plnm.smartcart', // App bundle ID
  // App store
  store,
  // App routes
  routes,

  // Input settings
  input: {
    scrollIntoViewOnFocus: device.cordova && !device.electron,
    scrollIntoViewCentered: device.cordova && !device.electron,
  },
  // Cordova Statusbar settings
  statusbar: {
    iosOverlaysWebView: true,
    androidOverlaysWebView: false,
  },
  panel: {
    swipe: true,
    swipeNoFollow: true,
  },
  on: {
    init() {
      let f7 = this;
      if (f7.device.cordova) {
        // Init cordova APIs (see cordova-app.js)
        cordovaApp.init(f7);
      }
    },
  },
});

// alert window
function showAlert(msgs, header, exit = false) {
  const errMsgTmp = msgs;
  if (errMsg !== errMsgTmp) {
    errMsg = errMsgTmp;
    app.dialog.alert(msgs, header, () => {
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
      errStats = false;
    });
  }
}

// Create bottom toast
function consoleToast(str) {
  if (!app.device.cordova) {
    const toastBottom = app.toast.create({
      text: str,
      closeTimeout: 2000,
    });
    toastBottom.open();
  }
}

// QR Scan
function qrScan() {
  window.QRScanner.scan((err, contents) => {
    if (err) {
      if (err.name === 'UNEXPECTED_ERROR') {
        console.error(err._message);
      }
      if (err.name === 'CAMERA_ACCESS_DENIED') {
        console.error('Camera access denied.');
      }
      if (err.name === 'CAMERA_ACCESS_RESTRICTED') {
        console.error('Camera access restricted.');
      }
      if (err.name === 'BACK_CAMERA_UNAVAILABLE') {
        console.error('Back camera unavailable.');
      }
      if (err.name === 'FRONT_CAMERA_UNAVAILABLE') {
        console.error('Front camera unavailable.');
      }
      if (err.name === 'CAMERA_UNAVAILABLE') {
        console.error('No camera found.');
      }
      if (err.name === 'SCAN_CANCELED') {
        console.error('The scan was canceled before a QR code was found.');
      }
      if (err.name === 'LIGHT_UNAVAILABLE') {
        console.error('Light unavailable.');
      }
      if (err.name === 'OPEN_SETTINGS_UNAVAILABLE') {
        console.error('Open settings unavailable.');
      }
    }
    const qr = `The QR Code contains: ${contents}`;
    console.log(qr);
    showAlert(qr, 'QR Scanner');
  });
}

// Cancel QR Scan
function qrCancelScan() {
  window.QRScanner.cancelScan((status) => {
    console.log(status);
  });
}

// Show QR Scanner
function qrShow() {
  window.QRScanner.show((status) => {
    console.log(status);
  });
}

// Hide QR Scannner
function qrHide() {
  window.QRScanner.hide((status) => {
    console.log(status);
  });
}

// Enable camera light
function qrEnableLight() {
  window.QRScanner.enableLight((err, status) => {
    if (err) console.error(err);
    console.log(status);
  });
}

// Disable camera light
function qrDisableLight() {
  window.QRScanner.disableLight((err, status) => {
    if (err) console.error(err);
    console.log(status);
  });
}

// Use back camera
function qrUseBackCamera() {
  window.QRScanner.useBackCamera((err, status) => {
    if (err) console.error(err);
    console.log(status);
  });
}

// Use front camera
function qrUseFrontCamera() {
  window.QRScanner.useFrontCamera((err, status) => {
    if (err) console.error(err);
    console.log(status);
  });
}

// Pause preview
function qrPausePreview() {
  window.QRScanner.pausePreview((status) => {
    console.log(status);
  });
}

// Resume preview
function qrResumePreview() {
  window.QRScanner.resumePreview((status) => {
    console.log(status);
  });
}

// Open app settings
function qrOpenAppSetting() {
  window.QRScanner.getStatus((status) => {
    if (!status.authorized && status.canOpenSettings) {
      app.dialog.confirm(`Would you like to enable QR code scanning?
        You can allow camera access in your settings.`, () => {
        window.QRScanner.openSettings();
      });
    }
  });
}

// QR status
function qrStatus() {
  window.QRScanner.getStatus((status) => {
    console.log(status);
    /* {
      "authorized": Boolean
      "denied": Boolean
      "restricted": Boolean
      "prepared": Boolean
      "scanning": Boolean
      "previewing": Boolean
      "showing": Boolean
      "lightEnabled": Boolean
      "canOpenSettings": Boolean
      "canEnableLight": Boolean
      "currentCamera": Number
    } */
  });
}

// Destroy qr scanner
function qrDestroy() {
  window.QRScanner.destroy((status) => {
    console.log(status);
  });
}

/* overrides */
window.onerror = (msg, url, line) => {
  errStats = true;
  const msgs = `Message: ${msg}<br>
    Line number: ${line}<br>
    Url: ${url}`;
  // Alert
  showAlert(msgs, 'Error');
};
/**/

// Login Screen Demo
$('#login-screen .login-button').on('click', () => {
  const username = $('#login-screen [name="username"]').val();
  const password = $('#login-screen [name="password"]').val();

  // Close login screen
  app.loginScreen.close('#login-screen');

  // Alert username and password
  showAlert(`Username: ${username}<br/>Password: ${password}`, 'Login');
});
