var $$ = Dom7;
var $$data;
var $$fbI;
var $$fbO;
var $$db;
var $$err = false;
var $$devReady = false;
var $$notif = false;
var $$stateDriver1 = '';
var $$stateDriver2 = '';
var $$stateDriver3 = '';
var $$stateDriver1Tmp = '';
var $$stateDriver2Tmp = '';
var $$stateDriver3Tmp = '';
const $$headerDriver1 = 'Status Sopir 1';
const $$headerDriver2 = 'Status Sopir 2';
const $$headerDriver3 = 'Status Sopir 3';
const $$bpmStr = 'Sopir kelelahan';
const $$treshBpm = 60;
const $$rootPath = "/RezaSupir/";

var app = new Framework7({
  root: '#app', // App root element

  id: 'id.ac.plnm.monitoring.sopir', // App bundle ID
  name: 'Pantau Sopir', // App name
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
    androidBackgroundColor: '#000000ff',
    androidTextColor: 'white',
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

app.views.create('.view-main', {
  url: '/'
});

window.onerror = function (msg, url, line) {
  $$err = true;
  app.preloader.hide();
  var msgs = "Message : " + msg + "<br>Line number : " + line + "<br>Url : " + url ;
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
  if (!app.device.cordova) {
    var toastBottom = app.toast.create({
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
  
  $$db = firebase.database();
  $$fbI = true;
  console.log("fbInit");
}

function fbOn(){
  /* obtain data when app is starting or data is updated */
  $$db.ref($$rootPath).on("value", function(snapshot) {
    $$data = snapshot.val();
    //console.log($$data);
    
    // Driver 1
    $$stateDriver1Tmp = (parseInt($$data.Supir1.Jantung) < $$treshBpm ? $$bpmStr : '' );
    if ( $$stateDriver1 != $$stateDriver1Tmp ){
      $$notif = false;
      addNotification($$headerDriver1, $$stateDriver1Tmp);
      $$stateDriver1 = $$stateDriver1Tmp;
    }
    document.getElementById('val-jantung1').innerHTML = $$data.Supir1.Jantung + ' bpm';
    document.getElementById('val-oksigen1').innerHTML = $$data.Supir1.Oksigen + ' %';

    // Driver 2
    $$stateDriver2Tmp = (parseInt($$data.Supir2.Jantung) < $$treshBpm ? $$bpmStr : '' );
    if ( $$stateDriver2 != $$stateDriver2Tmp ){
      $$notif = false;
      addNotification($$headerDriver2, $$stateDriver2Tmp);
      $$stateDriver2 = $$stateDriver2Tmp;
    }
    document.getElementById('val-jantung2').innerHTML = $$data.Supir2.Jantung + ' bpm';
    document.getElementById('val-oksigen2').innerHTML = $$data.Supir2.Oksigen + ' %';

    // Driver 3
    $$stateDriver3Tmp = (parseInt($$data.Supir3.Jantung) < $$treshBpm ? $$bpmStr : '' );
    if ( $$stateDriver3 != $$stateDriver3Tmp ){
      $$notif = false;
      addNotification($$headerDriver3, $$stateDriver3Tmp);
      $$stateDriver3 = $$stateDriver3Tmp;
    }
    document.getElementById('val-jantung3').innerHTML = $$data.Supir3.Jantung + ' bpm';
    document.getElementById('val-oksigen3').innerHTML = $$data.Supir3.Oksigen + ' %';
    
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
          
          // Driver 1
          $$stateDriver1Tmp = (parseInt($$data.Supir1.Jantung) < $$treshBpm ? $$bpmStr : '' );
          if ( $$stateDriver1 != $$stateDriver1Tmp ){
            $$notif = false;
            addNotification($$headerDriver1, $$stateDriver1Tmp);
            $$stateDriver1 = $$stateDriver1Tmp;
          }
          document.getElementById('val-jantung1').innerHTML = $$data.Supir1.Jantung + ' bpm';
          document.getElementById('val-oksigen1').innerHTML = $$data.Supir1.Oksigen + ' %';

          // Driver 2
          $$stateDriver2Tmp = (parseInt($$data.Supir2.Jantung) < $$treshBpm ? $$bpmStr : '' );
          if ( $$stateDriver2 != $$stateDriver2Tmp ){
            $$notif = false;
            addNotification($$headerDriver2, $$stateDriver2Tmp);
            $$stateDriver2 = $$stateDriver2Tmp;
          }
          document.getElementById('val-jantung2').innerHTML = $$data.Supir2.Jantung + ' bpm';
          document.getElementById('val-oksigen2').innerHTML = $$data.Supir2.Oksigen + ' %';

          // Driver 3
          $$stateDriver3Tmp = (parseInt($$data.Supir3.Jantung) < $$treshBpm ? $$bpmStr : '' );
          if ( $$stateDriver3 != $$stateDriver3Tmp ){
            $$notif = false;
            addNotification($$headerDriver3, $$stateDriver3Tmp);
            $$stateDriver3 = $$stateDriver3Tmp;
          }
          document.getElementById('val-jantung3').innerHTML = $$data.Supir3.Jantung + ' bpm';
          document.getElementById('val-oksigen3').innerHTML = $$data.Supir3.Oksigen + ' %';
          
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
        
        // Driver 1
        $$stateDriver1Tmp = (parseInt($$data.Supir1.Jantung) < $$treshBpm ? $$bpmStr : '' );
        if ( $$stateDriver1 != $$stateDriver1Tmp ){
          $$notif = false;
          addNotification($$headerDriver1, $$stateDriver1Tmp);
          $$stateDriver1 = $$stateDriver1Tmp;
        }
        document.getElementById('val-jantung1').innerHTML = $$data.Supir1.Jantung + ' bpm';
        document.getElementById('val-oksigen1').innerHTML = $$data.Supir1.Oksigen + ' %';

        // Driver 2
        $$stateDriver2Tmp = (parseInt($$data.Supir2.Jantung) < $$treshBpm ? $$bpmStr : '' );
        if ( $$stateDriver2 != $$stateDriver2Tmp ){
          $$notif = false;
          addNotification($$headerDriver2, $$stateDriver2Tmp);
          $$stateDriver2 = $$stateDriver2Tmp;
        }
        document.getElementById('val-jantung2').innerHTML = $$data.Supir2.Jantung + ' bpm';
        document.getElementById('val-oksigen2').innerHTML = $$data.Supir2.Oksigen + ' %';

        // Driver 3
        $$stateDriver3Tmp = (parseInt($$data.Supir3.Jantung) < $$treshBpm ? $$bpmStr : '' );
        if ( $$stateDriver3 != $$stateDriver3Tmp ){
          $$notif = false;
          addNotification($$headerDriver3, $$stateDriver3Tmp);
          $$stateDriver3 = $$stateDriver3Tmp;
        }
        document.getElementById('val-jantung3').innerHTML = $$data.Supir3.Jantung + ' bpm';
        document.getElementById('val-oksigen3').innerHTML = $$data.Supir3.Oksigen + ' %';
        
      }
    );
    console.log("ptr done...");
    consoleToast("Updated.");
    app.ptr.done();
  }, 2000);
});

