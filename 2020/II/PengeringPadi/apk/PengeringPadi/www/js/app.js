var $$ = Dom7;
var $$data;
var $$fbI;
var $$fbO;
var $$db;
var $$err = false;
var $$devReady = false;
var $$notif = false;

var app = new Framework7({
  root: '#app', // App root element

  id: 'id.ycmlg.pengeringpadi', // App bundle ID
  name: 'Pengering Padi', // App name
  theme: 'auto', // Automatic theme detection
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
  
  navbar: {
    hideOnPageScroll: false,
    mdCenterTitle: false,
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
	  console.log('App initialized');
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
function addNotification() {
	if (app.device.cordova && $$notif == false) {
		cordovaApp.addNotification('Suhu: ' + $$data.Soil.toFixed(2) + '\u00B0C');
		console.log("Notification added.");
		$$notif = true;
		//consoleToast("Notification added.");
	}
	var loc = window.location.pathname;
	var dir = loc.substring(0, loc.lastIndexOf('/'));
	////consoleToast('Loc:' + loc + ' Dir:' + dir);
	console.log('Loc:' + loc + ' Dir:' + dir);
}

function consoleToast(str){
	// Create bottom toast
	var toastBottom = app.toast.create({
	  text: str,
	  closeTimeout: 2000,
	});
	toastBottom.open();
}

// Initialize Firebase
function fbInit(){
	var config = {
		apiKey: "...", //settings/general/ @Web API Key
		authDomain: "...",
		databaseURL: "...",
		projectId: "...",
		storageBucket: "...",
		messagingSenderId: "..."				//settings/cloudmessaging/ @Sender ID
	};
	firebase.initializeApp(config);
	// Get a reference to the database service
	$$db = firebase.database();
	var $$fbI = true;
	console.log("fbInit");
}

function fbOn(){
	/* obtain data when app is starting or data is updated */
	$$db.ref("/jtd/PengeringPadi/").on("value", function(snapshot) {
		$$data = snapshot.child("data").val();
		document.getElementById('img-moist').src = 'assets/moist.png';
		document.getElementById('img-tempc').src = 'assets/temp.png';
		document.getElementById('img-tempf').src = 'assets/temp.png';
		document.getElementById('soilVal').innerHTML = $$data.Soil.toFixed(2) + '%';
		document.getElementById('tempCVal').innerHTML = $$data.Suhu_C.toFixed(2) + '\u00B0C';
		document.getElementById('tempFVal').innerHTML = $$data.Suhu_F.toFixed(2) + '\u00B0F';
		if(parseInt($$data.RelayPowerWindow) == 1){
			$$('#relayOffPowerWindow').removeClass('button-active');
			$$('#relayOnPowerWindow').addClass('button-active');
		} else {
			$$('#relayOnPowerWindow').removeClass('button-active');
			$$('#relayOffPowerWindow').addClass('button-active');
		}
		
		if(parseInt($$data.RelayKipas) == 1){
			$$('#relayOffKipas').removeClass('button-active');
			$$('#relayOnKipas').addClass('button-active');
		} else {
			$$('#relayOnKipas').removeClass('button-active');
			$$('#relayOffKipas').addClass('button-active');
		}
		
		if(parseInt($$data.RelayPompa) == 1){
			$$('#relayOffPompa').removeClass('button-active');
			$$('#relayOnPompa').addClass('button-active');
		} else {
			$$('#relayOnPompa').removeClass('button-active');
			$$('#relayOffPompa').addClass('button-active');
		}
		console.log("fbOn");
		if(parseFloat($$data.Soil) <= 15.00 || parseInt($$data.Soil) <= 15){
			addNotification();
		} else {
			$$notif = false;
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
			$$db.ref("/jtd/PengeringPadi/").once("value").then(
				function(snapshot) {
					$$data = snapshot.child("data").val();
					document.getElementById('img-moist').src = 'assets/moist.png';
					document.getElementById('img-tempc').src = 'assets/temp.png';
					document.getElementById('img-tempf').src = 'assets/temp.png';
					document.getElementById('soilVal').innerHTML = $$data.Soil.toFixed(2) + '%';
					document.getElementById('tempCVal').innerHTML = $$data.Suhu_C.toFixed(2) + '\u00B0C';
					document.getElementById('tempFVal').innerHTML = $$data.Suhu_F.toFixed(2) + '\u00B0F';
					if(parseInt($$data.RelayPowerWindow) == 1){
						$$('#relayOffPowerWindow').removeClass('button-active');
						$$('#relayOnPowerWindow').addClass('button-active');
					} else {
						$$('#relayOnPowerWindow').removeClass('button-active');
						$$('#relayOffPowerWindow').addClass('button-active');
					}
					
					if(parseInt($$data.RelayKipas) == 1){
						$$('#relayOffKipas').removeClass('button-active');
						$$('#relayOnKipas').addClass('button-active');
					} else {
						$$('#relayOnKipas').removeClass('button-active');
						$$('#relayOffKipas').addClass('button-active');
					}
					
					if(parseInt($$data.RelayPompa) == 1){
						$$('#relayOffPompa').removeClass('button-active');
						$$('#relayOnPompa').addClass('button-active');
					} else {
						$$('#relayOnPompa').removeClass('button-active');
						$$('#relayOffPompa').addClass('button-active');
					}
					console.log("fbOnce");
					if(parseFloat($$data.Soil) <= 15.00 || parseInt($$data.Soil) <= 15){
						addNotification();
					} else {
						$$notif = false;
					}
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

function writeRelayData(relay, modes) {
  var updates = {};
  if(modes == "powerwindow") {
	  updates['/jtd/PengeringPadi/data/RelayPowerWindow'] = relay;
  } else if(modes == "kipas") {
	  updates['/jtd/PengeringPadi/data/RelayKipas'] = relay;
  } else if(modes == "pompa") {
	  updates['/jtd/PengeringPadi/data/RelayPompa'] = relay;
  }

  return firebase.database().ref().update(updates);
}

// Pull to refresh content
var $ptrContent = $$('.ptr-content');
$ptrContent.on('ptr:refresh', function (e) {
  setTimeout(function () {
		$$db.ref("/jtd/PengeringPadi/").once("value").then(
			function(snapshot) {
				$$data = snapshot.child("data").val();
				document.getElementById('img-moist').src = 'assets/moist.png';
				document.getElementById('img-tempc').src = 'assets/temp.png';
				document.getElementById('img-tempf').src = 'assets/temp.png';
				document.getElementById('soilVal').innerHTML = $$data.Soil.toFixed(2) + '%';
				document.getElementById('tempCVal').innerHTML = $$data.Suhu_C.toFixed(2) + '\u00B0C';
				document.getElementById('tempFVal').innerHTML = $$data.Suhu_F.toFixed(2) + '\u00B0F';
				if(parseInt($$data.RelayPowerWindow) == 1){
					$$('#relayOffPowerWindow').removeClass('button-active');
					$$('#relayOnPowerWindow').addClass('button-active');
				} else {
					$$('#relayOnPowerWindow').removeClass('button-active');
					$$('#relayOffPowerWindow').addClass('button-active');
				}
				
				if(parseInt($$data.RelayKipas) == 1){
					$$('#relayOffKipas').removeClass('button-active');
					$$('#relayOnKipas').addClass('button-active');
				} else {
					$$('#relayOnKipas').removeClass('button-active');
					$$('#relayOffKipas').addClass('button-active');
				}
				
				if(parseInt($$data.RelayPompa) == 1){
					$$('#relayOffPompa').removeClass('button-active');
					$$('#relayOnPompa').addClass('button-active');
				} else {
					$$('#relayOnPompa').removeClass('button-active');
					$$('#relayOffPompa').addClass('button-active');
				}
				
				if(parseFloat($$data.Soil) <= 15.00 || parseInt($$data.Soil) <= 15){
					addNotification();
				} else {
					$$notif = false;
				}
			}
		);
		console.log("ptr done...");
		//consoleToast("Updated.");
		app.ptr.done();
  }, 1000);
});