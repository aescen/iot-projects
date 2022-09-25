var $$ = Dom7;
var $$data;
var $$fbI;
var $$fbO;
var $$db;
var $$err = false;
var $$devReady = false;
var $$notif = false;
var $$stateNotif = NaN;
var $$stateNotifTmp = NaN;
var $$notifStr = 'Tanggal pemakaian: \n'
const $$headerNotif = 'Status Aki: soak';
const $$engOn = 'Mesin menyala';
const $$engOff = 'Mesin mati';
const $$strOk = 'OK';
const $$strBad = 'soak';

var app = new Framework7({
  root: '#app', // App root element

  id: 'id.ac.plnm.kontrolmobil', // App bundle ID
  name: 'Kontrol Mobil', // App name
  theme: 'md', // Automatic theme detection
  autoDarkTheme : false,
  
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
	  $$('#open-tgl-setting').on('click', function () {
        app.dialog.prompt('Enter date, ex. 31-12-1999:', function (valDate) {
          if (Boolean(valDate.trim())) {
            try {
              let dateParts = valDate.split("-");
              let date = new Date(dateParts[2], (dateParts[1] - 1), dateParts[0]);
              if (String(date) === 'Invalid Date') throw "Error: Invalid Date";
              writeSettingsData('/kong/Tanggal_Aki', date.getTime() / 1000);
            } catch (error) {
              app.dialog.alert(error, 'Set date error', ()=>{});
            }
          }
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
    $$notif = true;
    consoleToast('Notif: ' + headerStr + ':' + bodyStr);
  }
	// var loc = window.location.pathname;
	// var dir = loc.substring(0, loc.lastIndexOf('/'));
	// ////consoleToast('Loc:' + loc + ' Dir:' + dir);
	// console.log('Loc:' + loc + ' Dir:' + dir);
}

function consoleToast(str){
	// Create bottom toast
	var toastBottom = app.toast.create({
	  text: str,
	  closeTimeout: 2000,
	});
	toastBottom.open();
}

function epochToJsDate(ts){
  // ts = epoch timestamp
  // returns date obj
  return new Date(ts*1000);
}

function jsDateToEpoch(d){
  // d = javascript date obj
  // returns epoch timestamp
  return (d.getTime()-d.getMilliseconds())/1000;
}

function writeSettingsData(path, val) {
  let updates = {
    [path]: val,
  };
  // console.log('Prompt: ' + JSON.stringify(updates));
  return firebase.database().ref().update(updates);
}

// Initialize Firebase
function fbInit(){
	var config = {
		//
	};
	firebase.initializeApp(config);
	// Get a reference to the database service
	$$db = firebase.database();
	$$fbI = true;
	console.log("fbInit");
}

function fbOn(){
	/* obtain data when app is starting or data is updated */
	$$db.ref("/").on("value", function(snapshot) {
		$$data = snapshot.child("kong").val();
					
		if($$data.kontrol.relayMesin){
			document.getElementById('img-engine').src = 'assets/g_engine.png';
		} else {
			document.getElementById('img-engine').src = 'assets/engine.png';
		}
		
		if ($$data.Tegangan <= 10.0){
			document.getElementById('img-voltage').src = 'assets/r_batt.png';
		} else if ($$data.Tegangan > 10.0 && $$data.Tegangan <= 11.0 ){
			document.getElementById('img-voltage').src = 'assets/y_batt.png';
		} else if ($$data.Tegangan > 11.0 && $$data.Tegangan <= 12.0){
			document.getElementById('img-voltage').src = 'assets/batt.png';
		} else if ($$data.Tegangan > 12.0 ){
			document.getElementById('img-voltage').src = 'assets/g_batt.png';
		}

		if ($$data.Aki){
			document.getElementById('img-accu').src = 'assets/batt.png';
		} else {
			document.getElementById('img-accu').src = 'assets/batt-grey.png';
		}
		
		//document.getElementById('engine-status').innerHTML = ($$data.Tegangan >= 12.0) ? $$engOn : $$engOff;
		document.getElementById('engine-status').innerHTML = $$data.kontrol.relayMesin ? $$engOn : $$engOff;
		document.getElementById('voltage-status').innerHTML = $$data.Tegangan.toFixed(2) + 'v';
    document.getElementById('accu-date').innerHTML = epochToJsDate($$data.Tanggal_Aki).toDateString();
		document.getElementById('accu-status').innerHTML = $$data.Aki ? $$strOk : $$strBad;
    
    $$stateNotifTmp = $$data.Aki;

    if ( $$stateNotif != $$stateNotifTmp ){
      if (!$$stateNotifTmp) {
        $$notif = false;
        let bodyStr = $$notifStr + epochToJsDate($$data.Tanggal_Aki).toDateString();
        addNotification($$headerNotif, bodyStr);
        $$stateNotif = $$stateNotifTmp;
      }
      $$stateNotif = $$stateNotifTmp;
    }
		
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
			$$db.ref("/").once("value").then(
				function(snapshot) {
					$$data = snapshot.child("kong").val();
					
					if($$data.kontrol.relayMesin){
						document.getElementById('img-engine').src = 'assets/g_engine.png';
					} else {
						document.getElementById('img-engine').src = 'assets/engine.png';
					}
					
					if ($$data.Tegangan <= 10.0){
						document.getElementById('img-voltage').src = 'assets/r_batt.png';
					} else if ($$data.Tegangan > 10.0 && $$data.Tegangan <= 11.0 ){
						document.getElementById('img-voltage').src = 'assets/y_batt.png';
					} else if ($$data.Tegangan > 11.0 && $$data.Tegangan <= 12.0){
						document.getElementById('img-voltage').src = 'assets/batt.png';
					} else if ($$data.Tegangan > 12.0 ){
						document.getElementById('img-voltage').src = 'assets/g_batt.png';
					}

          if ($$data.Aki){
            document.getElementById('img-accu').src = 'assets/batt.png';
          } else {
            document.getElementById('img-accu').src = 'assets/batt-grey.png';
          }
		
					//document.getElementById('engine-status').innerHTML = ($$data.Tegangan >= 12.0) ? $$engOn : $$engOff;
					document.getElementById('engine-status').innerHTML = $$data.kontrol.relayMesin ? $$engOn : $$engOff;
					document.getElementById('voltage-status').innerHTML = $$data.Tegangan.toFixed(2) + 'v';
          document.getElementById('accu-date').innerHTML = epochToJsDate($$data.Tanggal_Aki).toDateString();
					document.getElementById('accu-status').innerHTML = $$data.Aki ? $$strOk : $$strBad;

          if ( $$stateNotif != $$stateNotifTmp ){
            if (!$$stateNotifTmp) {
              $$notif = false;
              let bodyStr = $$notifStr + epochToJsDate($$data.Tanggal_Aki).toDateString();
              addNotification($$headerNotif, bodyStr);
              $$stateNotif = $$stateNotifTmp;
            }
            $$stateNotif = $$stateNotifTmp;
          }
					
					app.preloader.hide();
				}
			)
		}
	} else {
		console.log("Error/device not ready.");
		consoleToast("Error/device not ready.");
		app.preloader.hide();
	}
};

// Pull to refresh content
var $ptrContent = $$('.ptr-content');
$ptrContent.on('ptr:refresh', function (e) {
  setTimeout(function () {
		$$db.ref("/").once("value").then(
			function(snapshot) {
				$$data = snapshot.child("kong").val();
					
				if($$data.kontrol.relayMesin){
					document.getElementById('img-engine').src = 'assets/g_engine.png';
				} else {
					document.getElementById('img-engine').src = 'assets/engine.png';
				}
				
				if ($$data.Tegangan <= 10.0){
					document.getElementById('img-voltage').src = 'assets/r_batt.png';
				} else if ($$data.Tegangan > 10.0 && $$data.Tegangan <= 11.0 ){
					document.getElementById('img-voltage').src = 'assets/y_batt.png';
				} else if ($$data.Tegangan > 11.0 && $$data.Tegangan <= 12.0){
					document.getElementById('img-voltage').src = 'assets/batt.png';
				} else if ($$data.Tegangan > 12.0 ){
					document.getElementById('img-voltage').src = 'assets/g_batt.png';
				}

        if ($$data.Aki){
          document.getElementById('img-accu').src = 'assets/batt.png';
        } else {
          document.getElementById('img-accu').src = 'assets/batt-grey.png';
        }
				
				//document.getElementById('engine-status').innerHTML = ($$data.Tegangan >= 12.0) ? $$engOn : $$engOff;
				document.getElementById('engine-status').innerHTML = $$data.kontrol.relayMesin ? $$engOn : $$engOff;
				document.getElementById('voltage-status').innerHTML = $$data.Tegangan.toFixed(2) + 'v';
        document.getElementById('accu-date').innerHTML = epochToJsDate($$data.Tanggal_Aki).toDateString();
				document.getElementById('accu-status').innerHTML = $$data.Aki ? $$strOk : $$strBad;

        if ( $$stateNotif != $$stateNotifTmp ){
          if (!$$stateNotifTmp) {
            $$notif = false;
            let bodyStr = $$notifStr + epochToJsDate($$data.Tanggal_Aki).toDateString();
            addNotification($$headerNotif, bodyStr);
            $$stateNotif = $$stateNotifTmp;
          }
          $$stateNotif = $$stateNotifTmp;
        }
			}
		);
		console.log("ptr done...");
		//consoleToast("Updated.");
		app.ptr.done();
  }, 1000);
});