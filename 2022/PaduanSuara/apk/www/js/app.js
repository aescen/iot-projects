var $ = Dom7;
var $data;
var $fbI;
var $fbO;
var $db;
var $err = false;
var $devReady = false;

const $rootPath = "/Irma/";

var app = new Framework7({
  root: '#app', // App root element

  id: 'id.ac.plnm.paduansuara', // App bundle ID
  name: 'Aplikasi Paduan Suara', // App name
  theme: 'md', // Automatic theme detection
  autoDarkTheme : true,
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
      $devReady = true;
      refOnce();
    },
  },
});

var mainView = app.views.create('.view-main', {
  url: '/'
});

window.onerror = function (msg, url, line) {
  $err = true;
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

// Initialize Firebase
function fbInit(){
  var config = {
    // config here
  };
  // Initialize Firebase
  firebase.initializeApp(config);
  
  $db = firebase.database();
  $fbI = true;
  console.log("fbInit");
  
}

function getItem(id, arr) {
  return arr.filter((item) => item.id === id)[0];
}

function loadData(d) {
  const person = getItem(d.nama, d.listNama);
  const vocal = getItem(d.kode, d.vocalCode);

  document.querySelector('#personName').innerText = person.name;
  document.querySelector('#vocalType').innerText = vocal.info;
  document.querySelector('#amplitudeValue').innerText = d.amplitudo;
  document.querySelector('#frequencyValue').innerText = `${d.frekuensi}Hz`;

  document.querySelector('#iconPerson').src = "./assets/person.webp";
  document.querySelector('#iconVocal').src = "./assets/vocal.webp";
  document.querySelector('#iconVocalType').src = `./assets/${vocal.name}.webp`;
  document.querySelector('#iconAmplitude').src = "./assets/amplitude.webp";
  document.querySelector('#iconFrequency').src = "./assets/frequency.webp";
}

function fbOn(){
  /* obtain data when app is starting or data is updated */
  $db.ref($rootPath).on("value", function(snapshot) {
    $data = snapshot.val();
    //console.log($data);
    loadData($data);
    
    console.log("fbOn");
    app.preloader.hide();
    $fbO = true;
    }, function (error) {
  });
}

/* obtain data once */
function refOnce(){
  if(!$err && $devReady){
    if(!$fbI){
      fbInit();
      if(!$fbO){
        fbOn();
      }
    } else {
      $db.ref($rootPath).once("value").then(
        function(snapshot) {
          $data = snapshot.val();
          loadData($data);
          
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
var $ptrContent = $('.ptr-content');
$ptrContent.on('ptr:refresh', function (e) {
  setTimeout(function () {
  $db.ref($rootPath).once("value").then(
      function(snapshot) {
        $data = snapshot.val();
        loadData($data);
        
      }
    );
    console.log("ptr done...");
    consoleToast("Updated.");
    app.ptr.done();
  }, 2222);
});
