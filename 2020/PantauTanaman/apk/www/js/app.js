var $$ = Dom7;
var $$data;
var $$fbI;
var $$fbO;
var $$db;
var $$err = false;
var $$devReady = false;

var app = new Framework7({
  root: '#app', // App root element

  id: 'id.ycmlg.tanaman', // App bundle ID
  name: 'Tanaman', // App name
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
    iosOverlaysWebView: false,
    androidOverlaysWebView: true,
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
		apiKey: "...",
		authDomain: "...",
		databaseURL: "...",
		projectId: "...",
		storageBucket: "...",
		messagingSenderId: "...",
		appId: "...",
		measurementId: "..."
	};
	// Initialize Firebase
	firebase.initializeApp(config);
	//firebase.analytics();
	
	$$db = firebase.database();
	$$fbI = true;
	console.log("fbInit");
	
}

function fbOn(){
	/* obtain data when app is starting or data is updated */
	$$db.ref("/JUNPA/").on("value", function(snapshot) {
		$$data = snapshot.val();
		//console.log($$data);
		if ( $$data.Kelembapan1 !== undefined || $$data.Tinggi1 !== undefined) {
			document.getElementById('img-tanaman1').src = 'assets/tanaman.png';
			document.getElementById('kelembapan1').innerHTML = $$data.Kelembapan1;
			document.getElementById('tinggi1').innerHTML = $$data.Tinggi1;
		} else if ( $$data.Kelembapan1 === undefined && $$data.Tinggi1 === undefined) {
			document.getElementById('img-tanaman1').src = 'assets/tanaman-grey.png';
			document.getElementById('kelembapan1').innerHTML = $$data.Kelembapan1;
			document.getElementById('tinggi1').innerHTML = $$data.Tinggi1;
		}
		
		if ( $$data.Kelembapan2 !== undefined || $$data.Tinggi2 !== undefined) {
			document.getElementById('img-tanaman2').src = 'assets/tanaman.png';
			document.getElementById('kelembapan2').innerHTML = $$data.Kelembapan2;
			document.getElementById('tinggi2').innerHTML = $$data.Tinggi2;
		} else if ( $$data.Kelembapan2 === undefined && $$data.Tinggi2 === undefined) {
			document.getElementById('img-tanaman2').src = 'assets/tanaman-grey.png';
			document.getElementById('kelembapan2').innerHTML = $$data.Kelembapan2;
			document.getElementById('tinggi2').innerHTML = $$data.Tinggi2;
		}
		
		if ( $$data.Kelembapan3 !== undefined || $$data.Tinggi3 !== undefined) {
			document.getElementById('img-tanaman3').src = 'assets/tanaman.png';
			document.getElementById('kelembapan3').innerHTML = $$data.Kelembapan3;
			document.getElementById('tinggi3').innerHTML = $$data.Tinggi3;
		} else if ( $$data.Kelembapan3 === undefined && $$data.Tinggi3 === undefined) {
			document.getElementById('img-tanaman3').src = 'assets/tanaman-grey.png';
			document.getElementById('kelembapan3').innerHTML = $$data.Kelembapan3;
			document.getElementById('tinggi3').innerHTML = $$data.Tinggi3;
		}
		
		if ( $$data.Kelembapan4 !== undefined || $$data.Tinggi4 !== undefined) {
			document.getElementById('img-tanaman4').src = 'assets/tanaman.png';
			document.getElementById('kelembapan4').innerHTML = $$data.Kelembapan4;
			document.getElementById('tinggi4').innerHTML = $$data.Tinggi4;
		} else if ( $$data.Kelembapan4 === undefined && $$data.Tinggi4 === undefined) {
			document.getElementById('img-tanaman4').src = 'assets/tanaman-grey.png';
			document.getElementById('kelembapan4').innerHTML = $$data.Kelembapan4;
			document.getElementById('tinggi4').innerHTML = $$data.Tinggi4;
		}
		
		if ( $$data.Kelembapan5 !== undefined || $$data.Tinggi5 !== undefined) {
			document.getElementById('img-tanaman5').src = 'assets/tanaman.png';
			document.getElementById('kelembapan5').innerHTML = $$data.Kelembapan5;
			document.getElementById('tinggi5').innerHTML = $$data.Tinggi5;
		} else if ( $$data.Kelembapan5 === undefined && $$data.Tinggi5 === undefined) {
			document.getElementById('img-tanaman5').src = 'assets/tanaman-grey.png';
			document.getElementById('kelembapan5').innerHTML = $$data.Kelembapan5;
			document.getElementById('tinggi5').innerHTML = $$data.Tinggi5;
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
			$$db.ref("/JUNPA/").once("value").then(
				function(snapshot) {
					$$data = snapshot.val();
					//console.log($$data);
					if ( $$data.Kelembapan1 !== undefined || $$data.Tinggi1 !== undefined) {
						document.getElementById('img-tanaman1').src = 'assets/tanaman.png';
						document.getElementById('kelembapan1').innerHTML = $$data.Kelembapan1;
						document.getElementById('tinggi1').innerHTML = $$data.Tinggi1;
					} else if ( $$data.Kelembapan1 === undefined && $$data.Tinggi1 === undefined) {
						document.getElementById('img-tanaman1').src = 'assets/tanaman-grey.png';
						document.getElementById('kelembapan1').innerHTML = $$data.Kelembapan1;
						document.getElementById('tinggi1').innerHTML = $$data.Tinggi1;
					}
					
					if ( $$data.Kelembapan2 !== undefined || $$data.Tinggi2 !== undefined) {
						document.getElementById('img-tanaman2').src = 'assets/tanaman.png';
						document.getElementById('kelembapan2').innerHTML = $$data.Kelembapan2;
						document.getElementById('tinggi2').innerHTML = $$data.Tinggi2;
					} else if ( $$data.Kelembapan2 === undefined && $$data.Tinggi2 === undefined) {
						document.getElementById('img-tanaman2').src = 'assets/tanaman-grey.png';
						document.getElementById('kelembapan2').innerHTML = $$data.Kelembapan2;
						document.getElementById('tinggi2').innerHTML = $$data.Tinggi2;
					}
					
					if ( $$data.Kelembapan3 !== undefined || $$data.Tinggi3 !== undefined) {
						document.getElementById('img-tanaman3').src = 'assets/tanaman.png';
						document.getElementById('kelembapan3').innerHTML = $$data.Kelembapan3;
						document.getElementById('tinggi3').innerHTML = $$data.Tinggi3;
					} else if ( $$data.Kelembapan3 === undefined && $$data.Tinggi3 === undefined) {
						document.getElementById('img-tanaman3').src = 'assets/tanaman-grey.png';
						document.getElementById('kelembapan3').innerHTML = $$data.Kelembapan3;
						document.getElementById('tinggi3').innerHTML = $$data.Tinggi3;
					}
					
					if ( $$data.Kelembapan4 !== undefined || $$data.Tinggi4 !== undefined) {
						document.getElementById('img-tanaman4').src = 'assets/tanaman.png';
						document.getElementById('kelembapan4').innerHTML = $$data.Kelembapan4;
						document.getElementById('tinggi4').innerHTML = $$data.Tinggi4;
					} else if ( $$data.Kelembapan4 === undefined && $$data.Tinggi4 === undefined) {
						document.getElementById('img-tanaman4').src = 'assets/tanaman-grey.png';
						document.getElementById('kelembapan4').innerHTML = $$data.Kelembapan4;
						document.getElementById('tinggi4').innerHTML = $$data.Tinggi4;
					}
					
					if ( $$data.Kelembapan5 !== undefined || $$data.Tinggi5 !== undefined) {
						document.getElementById('img-tanaman5').src = 'assets/tanaman.png';
						document.getElementById('kelembapan5').innerHTML = $$data.Kelembapan5;
						document.getElementById('tinggi5').innerHTML = $$data.Tinggi5;
					} else if ( $$data.Kelembapan5 === undefined && $$data.Tinggi5 === undefined) {
						document.getElementById('img-tanaman5').src = 'assets/tanaman-grey.png';
						document.getElementById('kelembapan5').innerHTML = $$data.Kelembapan5;
						document.getElementById('tinggi5').innerHTML = $$data.Tinggi5;
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

function writeMusikData(musik) {
  var updates = {};
  updates['/JUNPA/MenyalakanMusik'] = musik;

  return firebase.database().ref().update(updates);
}

// Pull to refresh content
var $ptrContent = $$('.ptr-content');
$ptrContent.on('ptr:refresh', function (e) {
  setTimeout(function () {
		$$db.ref("/JUNPA/").once("value").then(
			function(snapshot) {
				$$data = snapshot.val();
				//console.log($$data);
				if ( $$data.Kelembapan1 !== undefined || $$data.Tinggi1 !== undefined) {
					document.getElementById('img-tanaman1').src = 'assets/tanaman.png';
					document.getElementById('kelembapan1').innerHTML = $$data.Kelembapan1;
					document.getElementById('tinggi1').innerHTML = $$data.Tinggi1;
				} else if ( $$data.Kelembapan1 === undefined && $$data.Tinggi1 === undefined) {
					document.getElementById('img-tanaman1').src = 'assets/tanaman-grey.png';
					document.getElementById('kelembapan1').innerHTML = $$data.Kelembapan1;
					document.getElementById('tinggi1').innerHTML = $$data.Tinggi1;
				}
				
				if ( $$data.Kelembapan2 !== undefined || $$data.Tinggi2 !== undefined) {
					document.getElementById('img-tanaman2').src = 'assets/tanaman.png';
					document.getElementById('kelembapan2').innerHTML = $$data.Kelembapan2;
					document.getElementById('tinggi2').innerHTML = $$data.Tinggi2;
				} else if ( $$data.Kelembapan2 === undefined && $$data.Tinggi2 === undefined) {
					document.getElementById('img-tanaman2').src = 'assets/tanaman-grey.png';
					document.getElementById('kelembapan2').innerHTML = $$data.Kelembapan2;
					document.getElementById('tinggi2').innerHTML = $$data.Tinggi2;
				}
				
				if ( $$data.Kelembapan3 !== undefined || $$data.Tinggi3 !== undefined) {
					document.getElementById('img-tanaman3').src = 'assets/tanaman.png';
					document.getElementById('kelembapan3').innerHTML = $$data.Kelembapan3;
					document.getElementById('tinggi3').innerHTML = $$data.Tinggi3;
				} else if ( $$data.Kelembapan3 === undefined && $$data.Tinggi3 === undefined) {
					document.getElementById('img-tanaman3').src = 'assets/tanaman-grey.png';
					document.getElementById('kelembapan3').innerHTML = $$data.Kelembapan3;
					document.getElementById('tinggi3').innerHTML = $$data.Tinggi3;
				}
				
				if ( $$data.Kelembapan4 !== undefined || $$data.Tinggi4 !== undefined) {
					document.getElementById('img-tanaman4').src = 'assets/tanaman.png';
					document.getElementById('kelembapan4').innerHTML = $$data.Kelembapan4;
					document.getElementById('tinggi4').innerHTML = $$data.Tinggi4;
				} else if ( $$data.Kelembapan4 === undefined && $$data.Tinggi4 === undefined) {
					document.getElementById('img-tanaman4').src = 'assets/tanaman-grey.png';
					document.getElementById('kelembapan4').innerHTML = $$data.Kelembapan4;
					document.getElementById('tinggi4').innerHTML = $$data.Tinggi4;
				}
				
				if ( $$data.Kelembapan5 !== undefined || $$data.Tinggi5 !== undefined) {
					document.getElementById('img-tanaman5').src = 'assets/tanaman.png';
					document.getElementById('kelembapan5').innerHTML = $$data.Kelembapan5;
					document.getElementById('tinggi5').innerHTML = $$data.Tinggi5;
				} else if ( $$data.Kelembapan5 === undefined && $$data.Tinggi5 === undefined) {
					document.getElementById('img-tanaman5').src = 'assets/tanaman-grey.png';
					document.getElementById('kelembapan5').innerHTML = $$data.Kelembapan5;
					document.getElementById('tinggi5').innerHTML = $$data.Tinggi5;
				}
			}
		);
		console.log("ptr done...");
		//consoleToast("Updated.");
		app.ptr.done();
  }, 1000);
});