var $$ = Dom7;
var $$data;
var $$fbI;
var $$fbO;
var $$db;
var $$err = false;
var $$devReady = false;
var $$notif = false;
var $$stateTempe = '';
var $$stateTempeTmp = '';
const $$headerTempe = 'Status Tempe';
const $$tempeStr = 'Tempe sudah matang';
const $$treshTempeLow = 43;
const $$treshTempeHi = 50;
const $$rootPath = "/Adit/";

var app = new Framework7({
  root: '#app', // App root element
  id: 'id.ac.plnm.monitoring.tempe', // App bundle ID
  name: 'Pantau Tempe', // App name
  theme: 'md', // Automatic theme detection
  autoDarkTheme : true,
  // App routes
  routes: routes,
  // Input settings
  input: {
    scrollIntoViewOnFocus: Framework7.device.cordova && !Framework7.device.electron,
    scrollIntoViewCentered: Framework7.device.cordova && !Framework7.device.electron,
  },
  // Cordova Statusbar settings
  statusbar: {
    iosOverlaysWebView: true,
    androidOverlaysWebView: false,
    androidBackgroundColor: '#000000ff',
    androidTextColor: 'white',
  },
  popup: {
    closeByBackdropClick: true,
  },
  on: {
    init: function () {
      var f7 = this;
      if (f7.device.cordova) {
        // Init cordova APIs (see cordova-app.js)
        cordovaApp.init(f7);
      }
    },
    pageInit: function () {
      console.log('Page initialized');
      $$devReady = true;
      refOnce();
      // Prompt
      $$('#open-pwm-setting').on('click', function () {
        app.dialog.prompt('Enter PWM value:', function (valPwm) {
          writeSettingsData($$rootPath + 'valPWM', parseInt(valPwm));
        });
      });
    },
  },
});

app.views.create('.view-main', {
  url: '/'
});

window.onerror = function (msg, url, line) {
  $$err = true;
  app.preloader.hide();
  let msgs = "Message : " + msg + "<br>Line number : " + line + "<br>Url : " + url ;
  // Alert
  app.dialog.alert(msgs, 'Error', function(){
    if (typeof cordova !== 'undefined') {
      if (navigator.app) {
        navigator.app.exitApp();
      }
      else if (navigator.device) {
        navigator.device.exitApp();
      }
    } else {
      window.close();
    }
  });
}

//notifications
function addNotification(headerStr, bodyStr) {
  if (app.device.cordova && $$notif == false) {
    cordovaApp.addNotification(headerStr, bodyStr);
    console.log("Notification added.");
    $$notif = true;
  //consoleToast("Notification added.");
    console.log('Notif: ' + headerStr + ': ' + bodyStr)
  } else {
      consoleToast('Notif: ' + headerStr + ': ' + bodyStr);
  }
  // var loc = window.location.pathname;
  // var dir = loc.substring(0, loc.lastIndexOf('/'));
  // ////consoleToast('Loc:' + loc + ' Dir:' + dir);
  // console.log('Loc:' + loc + ' Dir:' + dir);
}

function consoleToast(str){
  // Create bottom toast
  //if (app.device.cordova) {
    let toastBottom = app.toast.create({
    text: str,
    closeTimeout: 2000,
    });
    toastBottom.open();
  //}
}

function writeSettingsData(path, val) {
  /* let updates = {
    [path]: val,
  };
  // console.log('Prompt: ' + JSON.stringify(updates));
  return firebase.database().ref().update(updates); */
}

function writeButtonData(relay, modes) {
  /* var updates = {};
  if(modes == "bulb") {
    updates[$$rootPath + 'Lampu'] = relay;
  } else if(modes == "pwm") {
    updates[$$rootPath + 'PWM'] = relay;
  } else return false;

  return firebase.database().ref().update(updates); */
}

// Initialize Firebase
function fbInit(){
  var config = {
    apiKey: "AIzaSyBk0RIfTPuNx8LHOYx9XOywhw2aOYP2w7s",
    authDomain: "ycmlg-2021.firebaseapp.com",
    databaseURL: "https://ycmlg-2021-default-rtdb.firebaseio.com",
    projectId: "ycmlg-2021",
    storageBucket: "ycmlg-2021.appspot.com",
    messagingSenderId: "342265162233",
    appId: "1:342265162233:web:cf4733c5e3f75149467528"
  };
  // Initialize Firebase
  firebase.initializeApp(config);
  
  $$db = firebase.database();
  $$fbI = true;
  console.log("fbInit");
  
}

function fbOn(){
  /* obtain data when app is starting or data is updated */
  $$db.ref($$rootPath).on("value", function(snapshot) {
    $$data = snapshot.val();
    //console.log($$data);
    let valNH3 = parseFloat($$data.Ammonia);
    $$stateTempeTmp = ( valNH3 >= $$treshTempeLow && valNH3 <= $$treshTempeHi ? $$tempeStr : '' );
    if ( $$stateTempe != $$stateTempeTmp ){
      $$notif = false;
      addNotification($$headerTempe, $$stateTempeTmp);
      $$stateTempe = $$stateTempeTmp;
    }

    document.getElementById('img-nh3').src = 'assets/nh3.png';
    document.getElementById('val-nh3').innerHTML = $$data.Ammonia;

    document.getElementById('img-moist').src = 'assets/moist.png';
    document.getElementById('val-moist').innerHTML = $$data.Moist;

    document.getElementById('img-temp').src = 'assets/temp.png';
    document.getElementById('val-temp').innerHTML = $$data.Suhu;

    document.getElementById('img-bulb').src = 'assets/bulb.png';
    if(parseInt($$data.Lampu) == 1){
      $$('#btn-bulb-off').removeClass('button-active');
      $$('#btn-bulb-on').addClass('button-active');
    } else {
      $$('#btn-bulb-on').removeClass('button-active');
      $$('#btn-bulb-off').addClass('button-active');
    }

    document.getElementById('img-pwm').src = 'assets/pwm.png';
    if(parseInt($$data.PWM) >= 1){
      $$('#btn-pwm-off').removeClass('button-active');
      $$('#btn-pwm-on').addClass('button-active');
    } else {
      $$('#btn-pwm-on').removeClass('button-active');
      $$('#btn-pwm-off').addClass('button-active');
    }
    
    console.log("fbOn");
    
    app.preloader.hide();
    $$fbO = true;
    }, function (error) {
  });
}

/* obtain data once */
function refOnce(){
  if(!$$err && $$devReady){
    if(!$$fbI){
      fbInit();
      if(!$$fbO){
        fbOn();
      }
    } else {
      $$db.ref($$rootPath).once("value").then(
        function(snapshot) {
          $$data = snapshot.val();
          //console.log($$data);
          let valNH3 = parseFloat($$data.Ammonia);
          $$stateTempeTmp = ( valNH3 >= $$treshTempeLow && valNH3 <= $$treshTempeHi ? $$tempeStr : '' );
          if ( $$stateTempe != $$stateTempeTmp ){
            $$notif = false;
            addNotification($$headerTempe, $$stateTempeTmp);
            $$stateTempe = $$stateTempeTmp;
          }

          document.getElementById('img-nh3').src = 'assets/nh3.png';
          document.getElementById('val-nh3').innerHTML = $$data.Ammonia;

          document.getElementById('img-moist').src = 'assets/moist.png';
          document.getElementById('val-moist').innerHTML = $$data.Moist;

          document.getElementById('img-temp').src = 'assets/temp.png';
          document.getElementById('val-temp').innerHTML = $$data.Suhu;

          document.getElementById('img-bulb').src = 'assets/bulb.png';
          if(parseInt($$data.Lampu) == 1){
            $$('#btn-bulb-off').removeClass('button-active');
            $$('#btn-bulb-on').addClass('button-active');
          } else {
            $$('#btn-bulb-on').removeClass('button-active');
            $$('#btn-bulb-off').addClass('button-active');
          }

          document.getElementById('img-pwm').src = 'assets/pwm.png';
          if(parseInt($$data.PWM) >= 1){
            $$('#btn-pwm-off').removeClass('button-active');
            $$('#btn-pwm-on').addClass('button-active');
          } else {
            $$('#btn-pwm-on').removeClass('button-active');
            $$('#btn-pwm-off').addClass('button-active');
          }
          
          console.log("fbOnce");
          app.preloader.hide();
        }
      )
    }
  } else {
    console.log("Error/device not ready.");
    //consoleToast("Error/device not ready.");
    app.preloader.hide();
  }
};

// Pull to refresh content
var $ptrContent = $$('.ptr-content');
$ptrContent.on('ptr:refresh', function (e) {
  setTimeout(function () {
  $$db.ref($$rootPath).once("value").then(
      function(snapshot) {
        $$data = snapshot.val();
        //console.log($$data);
        let valNH3 = parseFloat($$data.Ammonia);
        $$stateTempeTmp = ( valNH3 >= $$treshTempeLow && valNH3 <= $$treshTempeHi ? $$tempeStr : '' );
        if ( $$stateTempe != $$stateTempeTmp ){
          $$notif = false;
          addNotification($$headerTempe, $$stateTempeTmp);
          $$stateTempe = $$stateTempeTmp;
        }

        document.getElementById('img-nh3').src = 'assets/nh3.png';
        document.getElementById('val-nh3').innerHTML = $$data.Ammonia;

        document.getElementById('img-moist').src = 'assets/moist.png';
        document.getElementById('val-moist').innerHTML = $$data.Moist;

        document.getElementById('img-temp').src = 'assets/temp.png';
        document.getElementById('val-temp').innerHTML = $$data.Suhu;

        document.getElementById('img-bulb').src = 'assets/bulb.png';
        if(parseInt($$data.Lampu) == 1){
          $$('#btn-bulb-off').removeClass('button-active');
          $$('#btn-bulb-on').addClass('button-active');
        } else {
          $$('#btn-bulb-on').removeClass('button-active');
          $$('#btn-bulb-off').addClass('button-active');
        }

        document.getElementById('img-pwm').src = 'assets/pwm.png';
        if(parseInt($$data.PWM) >= 1){
          $$('#btn-pwm-off').removeClass('button-active');
          $$('#btn-pwm-on').addClass('button-active');
        } else {
          $$('#btn-pwm-on').removeClass('button-active');
          $$('#btn-pwm-off').addClass('button-active');
        }
        
      }
    );
    console.log("ptr done...");
    consoleToast("Updated.");
    app.ptr.done();
  }, 2000);
});
