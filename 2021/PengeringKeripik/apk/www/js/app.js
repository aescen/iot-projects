var $$ = Dom7;
var $$data;
var $$fbI;
var $$fbO;
var $$db;
var $$err = false;
var $$devReady = false;
var $$notif = false;
var $$stateRak1 = '';
var $$stateRak2 = '';
var $$stateRak3 = '';
var $$stateRak1Tmp = '';
var $$stateRak2Tmp = '';
var $$stateRak3Tmp = '';
const $$headerRak1 = 'Status Rak1';
const $$headerRak2 = 'Status Rak2';
const $$headerRak3 = 'Status Rak3';
const $$lowStr = 'Kosong';
const $$medStr = 'Matang';
const $$hiStr = 'Process';
const $$treshholdEmpty = 150;
const $$treshholdBakedMin = 150;
const $$treshholdBakedMax = 250;
const $$treshholdProcess = 250;
const $$rootPath = "/Dhini/";

var app = new Framework7({
  root: '#app', // App root element

  id: 'id.ac.plnm.monitoring.pengering.keripik', // App bundle ID
  name: 'Monitor Pengering Keripik', // App name
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
    console.log('Notif: ' + headerStr + ':' + bodyStr)
	} else {
    consoleToast('Notif: ' + headerStr + ':' + bodyStr);
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
    
    // Rak 1
    var weight1 = parseInt($$data.Rak1.Berat1);
    document.getElementById('val-temp1').innerHTML = parseInt($$data.Rak1.Suhu1);
    document.getElementById('val-weight1').innerHTML = weight1;

    if(weight1 < $$treshholdEmpty){
      document.getElementById('val-cassava1').innerHTML =  $$lowStr;
      $$stateRak1Tmp = $$lowStr;
    } else if ( (weight1 >= $$treshholdBakedMin) && (weight1 <= $$treshholdBakedMax) ){
      document.getElementById('val-cassava1').innerHTML =  $$medStr;
      $$stateRak1Tmp = $$medStr;
    } else {
      document.getElementById('val-cassava1').innerHTML =  $$hiStr;
      $$stateRak1Tmp = $$hiStr;
    }

    if ( $$stateRak1 !== $$stateRak1Tmp ){
      $$notif = false;
      addNotification($$headerRak1, $$stateRak1Tmp);
      $$stateRak1 = $$stateRak1Tmp;
    }

    // Rak 2
    var weight2 = parseInt($$data.Rak2.Berat2);
    document.getElementById('val-temp2').innerHTML = parseInt($$data.Rak2.Suhu2);
    document.getElementById('val-weight2').innerHTML = weight2;
    
    if(weight2 < $$treshholdEmpty){
      document.getElementById('val-cassava2').innerHTML =  $$lowStr;
      $$stateRak2Tmp = $$lowStr;
    } else if ( (weight2 >= $$treshholdBakedMin) && (weight2 <= $$treshholdBakedMax) ){
      document.getElementById('val-cassava2').innerHTML =  $$medStr;
      $$stateRak2Tmp = $$medStr;
    } else {
      document.getElementById('val-cassava2').innerHTML =  $$hiStr;
      $$stateRak2Tmp = $$hiStr;
    }

    if ( $$stateRak2 !== $$stateRak2Tmp ){
      $$notif = false;
      addNotification($$headerRak2, $$stateRak2Tmp);
      $$stateRak2 = $$stateRak2Tmp;
    }

    // Rak 3
    var weight3 = parseInt($$data.Rak3.Berat3);
    document.getElementById('val-temp3').innerHTML = parseInt($$data.Rak3.Suhu3);
    document.getElementById('val-weight3').innerHTML = weight3;
    
    if(weight3 < $$treshholdEmpty){
      document.getElementById('val-cassava3').innerHTML =  $$lowStr;
      $$stateRak3Tmp = $$lowStr;
    } else if ( (weight3 >= $$treshholdBakedMin) && (weight3 <= $$treshholdBakedMax) ){
      document.getElementById('val-cassava3').innerHTML =  $$medStr;
      $$stateRak3Tmp = $$medStr;
    } else {
      document.getElementById('val-cassava3').innerHTML =  $$hiStr;
      $$stateRak3Tmp = $$hiStr;
    }

    if ( $$stateRak3 !== $$stateRak3Tmp ){
      $$notif = false;
      addNotification($$headerRak3, $$stateRak3Tmp);
      $$stateRak3 = $$stateRak3Tmp;
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
          
          // Rak 1
          
          var weight1 = parseInt($$data.Rak1.Berat1);
          document.getElementById('val-temp1').innerHTML = parseInt($$data.Rak1.Suhu1);
          document.getElementById('val-weight1').innerHTML = weight1;

          if(weight1 < $$treshholdEmpty){
            document.getElementById('val-cassava1').innerHTML =  $$lowStr;
            $$stateRak1Tmp = $$lowStr;
          } else if ( (weight1 >= $$treshholdBakedMin) && (weight1 <= $$treshholdBakedMax) ){
            document.getElementById('val-cassava1').innerHTML =  $$medStr;
            $$stateRak1Tmp = $$medStr;
          } else {
            document.getElementById('val-cassava1').innerHTML =  $$hiStr;
            $$stateRak1Tmp = $$hiStr;
          }

          if ( $$stateRak1 !== $$stateRak1Tmp ){
            $$notif = false;
            addNotification($$headerRak1, $$stateRak1Tmp);
            $$stateRak1 = $$stateRak1Tmp;
          }

          // Rak 2
          
          var weight2 = parseInt($$data.Rak2.Berat2);
          document.getElementById('val-temp2').innerHTML = parseInt($$data.Rak2.Suhu2);
          document.getElementById('val-weight2').innerHTML = weight2;
          
          if(weight2 < $$treshholdEmpty){
            document.getElementById('val-cassava2').innerHTML =  $$lowStr;
            $$stateRak2Tmp = $$lowStr;
          } else if ( (weight2 >= $$treshholdBakedMin) && (weight2 <= $$treshholdBakedMax) ){
            document.getElementById('val-cassava2').innerHTML =  $$medStr;
            $$stateRak2Tmp = $$medStr;
          } else {
            document.getElementById('val-cassava2').innerHTML =  $$hiStr;
            $$stateRak2Tmp = $$hiStr;
          }

          if ( $$stateRak2 !== $$stateRak2Tmp ){
            $$notif = false;
            addNotification($$headerRak2, $$stateRak2Tmp);
            $$stateRak2 = $$stateRak2Tmp;
          }

          // Rak 3
          
          var weight3 = parseInt($$data.Rak3.Berat3);
          document.getElementById('val-temp3').innerHTML = parseInt($$data.Rak3.Suhu3);
          document.getElementById('val-weight3').innerHTML = weight3;
          
          if(weight3 < $$treshholdEmpty){
            document.getElementById('val-cassava3').innerHTML =  $$lowStr;
            $$stateRak3Tmp = $$lowStr;
          } else if ( (weight3 >= $$treshholdBakedMin) && (weight3 <= $$treshholdBakedMax) ){
            document.getElementById('val-cassava3').innerHTML =  $$medStr;
            $$stateRak3Tmp = $$medStr;
          } else {
            document.getElementById('val-cassava3').innerHTML =  $$hiStr;
            $$stateRak3Tmp = $$hiStr;
          }

          if ( $$stateRak3 !== $$stateRak3Tmp ){
            $$notif = false;
            addNotification($$headerRak3, $$stateRak3Tmp);
            $$stateRak3 = $$stateRak3Tmp;
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
        
        // Rak 1
        
        var weight1 = parseInt($$data.Rak1.Berat1);
        document.getElementById('val-temp1').innerHTML = parseInt($$data.Rak1.Suhu1);
        document.getElementById('val-weight1').innerHTML = weight1;

        if(weight1 < $$treshholdEmpty){
          document.getElementById('val-cassava1').innerHTML =  $$lowStr;
          $$stateRak1Tmp = $$lowStr;
        } else if ( (weight1 >= $$treshholdBakedMin) && (weight1 <= $$treshholdBakedMax) ){
          document.getElementById('val-cassava1').innerHTML =  $$medStr;
          $$stateRak1Tmp = $$medStr;
        } else {
          document.getElementById('val-cassava1').innerHTML =  $$hiStr;
          $$stateRak1Tmp = $$hiStr;
        }

        if ( $$stateRak1 !== $$stateRak1Tmp ){
          $$notif = false;
          addNotification($$headerRak1, $$stateRak1Tmp);
          $$stateRak1 = $$stateRak1Tmp;
        }

        // Rak 2
        
        var weight2 = parseInt($$data.Rak2.Berat2);
        document.getElementById('val-temp2').innerHTML = parseInt($$data.Rak2.Suhu2);
        document.getElementById('val-weight2').innerHTML = weight2;
        
        if(weight2 < $$treshholdEmpty){
          document.getElementById('val-cassava2').innerHTML =  $$lowStr;
          $$stateRak2Tmp = $$lowStr;
        } else if ( (weight2 >= $$treshholdBakedMin) && (weight2 <= $$treshholdBakedMax) ){
          document.getElementById('val-cassava2').innerHTML =  $$medStr;
          $$stateRak2Tmp = $$medStr;
        } else {
          document.getElementById('val-cassava2').innerHTML =  $$hiStr;
          $$stateRak2Tmp = $$hiStr;
        }

        if ( $$stateRak2 !== $$stateRak2Tmp ){
          $$notif = false;
          addNotification($$headerRak2, $$stateRak2Tmp);
          $$stateRak2 = $$stateRak2Tmp;
        }

        // Rak 3
        
        var weight3 = parseInt($$data.Rak3.Berat3);
        document.getElementById('val-temp3').innerHTML = parseInt($$data.Rak3.Suhu3);
        document.getElementById('val-weight3').innerHTML = weight3;
        
        if(weight3 < $$treshholdEmpty){
          document.getElementById('val-cassava3').innerHTML =  $$lowStr;
          $$stateRak3Tmp = $$lowStr;
        } else if ( (weight3 >= $$treshholdBakedMin) && (weight3 <= $$treshholdBakedMax) ){
          document.getElementById('val-cassava3').innerHTML =  $$medStr;
          $$stateRak3Tmp = $$medStr;
        } else {
          document.getElementById('val-cassava3').innerHTML =  $$hiStr;
          $$stateRak3Tmp = $$hiStr;
        }

        if ( $$stateRak3 !== $$stateRak3Tmp ){
          $$notif = false;
          addNotification($$headerRak3, $$stateRak3Tmp);
          $$stateRak3 = $$stateRak3Tmp;
        }
        
      }
    );
    console.log("ptr done...");
    consoleToast("Updated.");
    app.ptr.done();
  }, 2000);
});

