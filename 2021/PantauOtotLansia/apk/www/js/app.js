var $$ = Dom7;
var $$data;
var $$fbI;
var $$fbO;
var $$db;
var $$err = false;
var $$devReady = false;
var $$statusLansia = 0;
const $$strStatus = [
  'Tidak Diketahui',
  'Aman',
  'Lansia Sakit',
  'Otot Kaku',
  'Sakit & Kaku'
];

const $$rootPath = "/Diar/";

var app = new Framework7({
  root: '#app', // App root element

  id: 'id.ac.plnm.monitoring.ototlansia', // App bundle ID
  name: 'Monitor Otot Lansia', // App name
  theme: 'md', // Automatic theme detection
  autoDarkTheme : false,
  // App root data
  data() {
  return {
    foo: 'bar'
  };
  },
  // App root methods
  methods: {
  doSomething() {
    // ...
  }
  },


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
    },
  },
});

var mainView = app.views.create('.view-main', {
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

function consoleToast(str){
  // Create bottom toast
  if (app.device.cordova) {
    let toastBottom = app.toast.create({
    text: str,
    closeTimeout: 2000,
    });
    toastBottom.open();
  }
}

function isTempHipo(valTemp, valTreshhold = 36){
    return (valTemp < valTreshhold);
}

function isTempNormal(valTemp, valTreshholdLow = 36, valTreshholdHi = 37.5){
    return (valTreshholdLow < valTemp && valTemp <= valTreshholdHi);
}

function isTempFever(valTemp, valTreshholdLow = 37.5, valTreshholdHi = 40){
    return (valTreshholdLow < valTemp && valTemp <= valTreshholdHi);
}

function isTempHiper(valTemp, valTreshhold = 40){
    return (valTemp > valTreshhold);
}

function isFreqRelax(valFreq, valTreshhold = 6){
    return (valFreq <= valTreshhold);
}

function isFreqNormal(valFreq, valTreshholdLow = 6, valTreshholdHi = 10){
    return (valTreshholdLow < valFreq && valFreq < valTreshholdHi);
}

function isFreqStiff(valFreq, valTreshholdLow = 10, valTreshholdHi = 20){
    return (valTreshholdLow <= valFreq && valFreq <= valTreshholdHi);
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
    appId: "1:342265162233:web:7be4279bafb6d396467528"
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
    /*
    'Tidak Diketahui',
    'Aman',
    'Lansia Sakit',
    'Otot Kaku',
    'Sakit & Kaku'
    */
    let valTemp = parseFloat($$data.Suhu);
    let valFreq = parseFloat($$data.Otot);
    if ( isTempNormal(valTemp) && isFreqNormal(valFreq) ) {
      $$statusLansia = 1;
    } else if ( (isTempHipo(valTemp) || isTempFever(valTemp) || isTempHiper(valTemp)) && !isFreqStiff(valFreq) ){
      $$statusLansia = 2;
    } else if ( isTempNormal(valTemp) && isFreqStiff(valFreq) ){
      $$statusLansia = 3;
    } else if ( (isTempHipo(valTemp) || isTempFever(valTemp) || isTempHiper(valTemp)) && isFreqStiff(valFreq) ){
      $$statusLansia = 4;
    } else{
      $$statusLansia = 0;
    }
    document.getElementById('val-status-color').src = ($$statusLansia >= 2 ? './assets/ellipse-red.png' : ($$statusLansia == 1 ? './assets/ellipse-green.png' : './assets/ellipse-grey.png'));
    document.getElementById('val-status').innerHTML = $$strStatus[$$statusLansia];
    document.getElementById('val-otot').innerHTML = $$data.Otot;
    document.getElementById('val-suhu').innerHTML = $$data.Suhu;
    
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
          let valTemp = parseFloat($$data.Suhu);
          let valFreq = parseFloat($$data.Otot);
          if ( isTempNormal(valTemp) && isFreqNormal(valFreq) ) {
            $$statusLansia = 1;
          } else if ( (isTempHipo(valTemp) || isTempFever(valTemp) || isTempHiper(valTemp)) && !isFreqStiff(valFreq) ){
            $$statusLansia = 2;
          } else if ( isTempNormal(valTemp) && isFreqStiff(valFreq) ){
            $$statusLansia = 3;
          } else if ( (isTempHipo(valTemp) || isTempFever(valTemp) || isTempHiper(valTemp)) && isFreqStiff(valFreq) ){
            $$statusLansia = 4;
          } else{
            $$statusLansia = 0;
          }
          document.getElementById('val-status-color').src = ($$statusLansia >= 2 ? './assets/ellipse-red.png' : ($$statusLansia == 1 ? './assets/ellipse-green.png' : './assets/ellipse-grey.png'));
          document.getElementById('val-status').innerHTML = $$strStatus[$$statusLansia];
          document.getElementById('val-otot').innerHTML = $$data.Otot;
          document.getElementById('val-suhu').innerHTML = $$data.Suhu;
          
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
        let valTemp = parseFloat($$data.Suhu);
        let valFreq = parseFloat($$data.Otot);
        if ( isTempNormal(valTemp) && isFreqNormal(valFreq) ) {
          $$statusLansia = 1;
        } else if ( (isTempHipo(valTemp) || isTempFever(valTemp) || isTempHiper(valTemp)) && !isFreqStiff(valFreq) ){
          $$statusLansia = 2;
        } else if ( isTempNormal(valTemp) && isFreqStiff(valFreq) ){
          $$statusLansia = 3;
        } else if ( (isTempHipo(valTemp) || isTempFever(valTemp) || isTempHiper(valTemp)) && isFreqStiff(valFreq) ){
          $$statusLansia = 4;
        } else{
          $$statusLansia = 0;
        }
        document.getElementById('val-status-color').src = ($$statusLansia >= 2 ? './assets/ellipse-red.png' : ($$statusLansia == 1 ? './assets/ellipse-green.png' : './assets/ellipse-grey.png'));
        document.getElementById('val-status').innerHTML = $$strStatus[$$statusLansia];
        document.getElementById('val-otot').innerHTML = $$data.Otot;
        document.getElementById('val-suhu').innerHTML = $$data.Suhu;
        
      }
    );
    console.log("ptr done...");
    consoleToast("Updated.");
    app.ptr.done();
  }, 2000);
});
