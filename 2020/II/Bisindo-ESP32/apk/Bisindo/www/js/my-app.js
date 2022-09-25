// Init framework7
var app = new Framework7({
  // App root element
  root: '#app',
  // App Name
  name: 'Bisindo',
  // App id
  id: 'id.ycmlg.bisindo',
  // Enable swipe panel
  panel: {
    swipe: 'left',
  },
  //pushState
  pushState: true,
  // Add default routes
  routes: [
	{
	  name:'main',
      path: '/',
	  url: './index.html',
    },
	{
      name: 'about',
      path: '/about/',
      url: './pages/about.html',
    },
	{
      path: '(.*)',
      url: './pages/404.html',
    },
  ],
  // Status bar
  statusbar: {
    androidOverlaysWebView: true,
  },
  //Card
  card: {
    hideNavbarOnOpen:false,
	hideToolbarOnOpen:false,
	swipeToClose:false,
	backrop:false,
	closeByBackdropClick:false,
  },
});
var mainView = app.views.create('.view-main', {
  url: '/'
});
// global vars
var $$ = Dom7;
var $$data;
var $$fbI;
var $$fbO;
var $$db;
var $$ttsState = false;
var $$err = false;
var $$devReady = true;

function onLoad(){
	document.addEventListener("deviceready", function(){
		$$devReady = true;
		console.log("Device ready.");
		refOnce();
	}, false);
}

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
	$$fbI=true;
}

function fbOn(){
	/* obtain data when app is starting or data is updated */
	$$db.ref("/jtd/bisindo/").on("value", function(snapshot) {
		$$data = snapshot.child("data").val();
		checkSymbol();
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
			$$db.ref("/jtd/bisindo/").once("value").then(
				function(snapshot) {
					$$data = snapshot.child("data").val();
					checkSymbol();
					app.preloader.hide();
				}
			)
		}
	} else {
		console.log("Device not ready.");
		app.preloader.hide();
	}
};

function checkSymbol(){
	$$temp = document.getElementById('status').value;
	if(typeof $$data.left !== 'undefined' > 0 && typeof $$data.right !== 'undefined'){
		if(parseInt($$data.right) == 1 && parseInt($$data.left) == 2){
			document.getElementById('status').innerHTML = "A";
			if(!$$ttsState){
				//speakText("A");
			}
		} else if(parseInt($$data.right) == 3 && parseInt($$data.left) == 4){
			document.getElementById('status').innerHTML = "B";
			if(!$$ttsState){
				//speakText("B");
			}
		} else if(parseInt($$data.right) == 5 && parseInt($$data.left) == 6){
			document.getElementById('status').innerHTML = "C";
			if(!$$ttsState){
				//speakText("C");
			}
		} else if(parseInt($$data.right) == 7 && parseInt($$data.left) == 8){
			document.getElementById('status').innerHTML = "D";
			if(!$$ttsState){
				//speakText("D");
			}
		} else if(parseInt($$data.right) == 9 && parseInt($$data.left) == 10){
			document.getElementById('status').innerHTML = "E";
			if(!$$ttsState){
				//speakText("E");
			}
		} else if(parseInt($$data.right) == 11 && parseInt($$data.left) == 12){
			document.getElementById('status').innerHTML = "F";
			if(!$$ttsState){
				//speakText("F");
			}
		} else if(parseInt($$data.right) == 13 && parseInt($$data.left) == 14){
			document.getElementById('status').innerHTML = "G";
			if(!$$ttsState){
				//speakText("G");
			}
		} else if(parseInt($$data.right) == 15 && parseInt($$data.left) == 16){
			document.getElementById('status').innerHTML = "H";
			if(!$$ttsState){
				//speakText("H");
			}
		} else if(parseInt($$data.right) == 17 && parseInt($$data.left) == 18){
			document.getElementById('status').innerHTML = "I";
			if(!$$ttsState){
				//speakText("I");
			}
		} else if(parseInt($$data.right) == 19 && parseInt($$data.left) == 20){
			document.getElementById('status').innerHTML = "J";
			if(!$$ttsState){
				//speakText("J");
			}
		} else if(parseInt($$data.right) == 21 && parseInt($$data.left) == 22){
			document.getElementById('status').innerHTML = "K";
			if(!$$ttsState){
				//speakText("K");
			}
		} else if(parseInt($$data.right) == 23 && parseInt($$data.left) == 24){
			document.getElementById('status').innerHTML = "L";
			if(!$$ttsState){
				//speakText("L");
			}
		} else if(parseInt($$data.right) == 25 && parseInt($$data.left) == 26){
			document.getElementById('status').innerHTML = "M";
			if(!$$ttsState){
				//speakText("M");
			}
		} else if(parseInt($$data.right) == 27 && parseInt($$data.left) == 28){
			document.getElementById('status').innerHTML = "N";
			if(!$$ttsState){
				//speakText("N");
			}
		} else if(parseInt($$data.right) == 29 && parseInt($$data.left) == 30){
			document.getElementById('status').innerHTML = "O";
			if(!$$ttsState){
				//speakText("O");
			}
		} else if(parseInt($$data.right) == 31 && parseInt($$data.left) == 32){
			document.getElementById('status').innerHTML = "P";
			if(!$$ttsState){
				//speakText("P");
			}
		} else if(parseInt($$data.right) == 33 && parseInt($$data.left) == 34){
			document.getElementById('status').innerHTML = "Q";
			if(!$$ttsState){
				//speakText("Q");
			}
		} else if(parseInt($$data.right) == 35 && parseInt($$data.left) == 36){
			document.getElementById('status').innerHTML = "R";
			if(!$$ttsState){
				//speakText("R");
			}
		} else if(parseInt($$data.right) == 37 && parseInt($$data.left) == 38){
			document.getElementById('status').innerHTML = "S";
			if(!$$ttsState){
				//speakText("S");
			}
		} else if(parseInt($$data.right) == 39 && parseInt($$data.left) == 40){
			document.getElementById('status').innerHTML = "T";
			if(!$$ttsState){
				//speakText("T");
			}
		} else if(parseInt($$data.right) == 41 && parseInt($$data.left) == 42){
			document.getElementById('status').innerHTML = "U";
			if(!$$ttsState){
				//speakText("U");
			}
		} else if(parseInt($$data.right) == 43 && parseInt($$data.left) == 44){
			document.getElementById('status').innerHTML = "V";
			if(!$$ttsState){
				//speakText("V");
			}
		} else if(parseInt($$data.right) == 45 && parseInt($$data.left) == 46){
			document.getElementById('status').innerHTML = "W";
			if(!$$ttsState){
				//speakText("W");
			}
		} else if(parseInt($$data.right) == 47 && parseInt($$data.left) == 48){
			document.getElementById('status').innerHTML = "X";
			if(!$$ttsState){
				//speakText("X");
			}
		} else if(parseInt($$data.right) == 49 && parseInt($$data.left) == 50){
			document.getElementById('status').innerHTML = "Y";
			if(!$$ttsState){
				//speakText("Y");
			}
		} else if(parseInt($$data.right) == 51 && parseInt($$data.left) == 52){
			document.getElementById('status').innerHTML = "Z";
			if(!$$ttsState){
				//speakText("Z");
			}
		} else if(parseInt($$data.right) == 53 && parseInt($$data.left) == 54){
			document.getElementById('status').innerHTML = "Assalamu'alaikum";
			if(!$$ttsState){
				//speakText("Assalamu'alaikum");
			}
		} else if(parseInt($$data.right) == 55 && parseInt($$data.left) == 56){
			document.getElementById('status').innerHTML = "Halo";
			if(!$$ttsState){
				//speakText("Halo");
			}
		} else if(parseInt($$data.right) == 57 && parseInt($$data.left) == 58){
			document.getElementById('status').innerHTML = "Dosen";
			if(!$$ttsState){
				//speakText("Dosen");
			}
		} else if(parseInt($$data.right) == 59 && parseInt($$data.left) == 60){
			document.getElementById('status').innerHTML = "Terimakasih";
			if(!$$ttsState){
				//speakText("Terimakasih");
			}
		} else if(parseInt($$data.right) == 61 && parseInt($$data.left) == 62){
			document.getElementById('status').innerHTML = "Selamat Jalan";
			if(!$$ttsState){
				//speakText("Selamat Jalan");
			}
		} else if(parseInt($$data.right) == 63 && parseInt($$data.left) == 64){
			document.getElementById('status').innerHTML = "Wa'alaikumsalam";
			if(!$$ttsState){
				//speakText("Wa'alaikumsalam");
			}
		} else if(parseInt($$data.right) == 999 && parseInt($$data.left) == 1000){
			document.getElementById('status').innerHTML = "0";
			if(!$$ttsState){
				//speakText("0");
			}
		} else if(parseInt($$data.right) == 1001 && parseInt($$data.left) == 1002){
			document.getElementById('status').innerHTML = "1";
			if(!$$ttsState){
				//speakText("1");
			}
		} else if(parseInt($$data.right) == 1003 && parseInt($$data.left) == 1004){
			document.getElementById('status').innerHTML = "2";
			if(!$$ttsState){
				//speakText("2");
			}
		} else if(parseInt($$data.right) == 1005 && parseInt($$data.left) == 1006){
			document.getElementById('status').innerHTML = "3";
			if(!$$ttsState){
				//speakText("3");
			}
		} else if(parseInt($$data.right) == 1007 && parseInt($$data.left) == 1008){
			document.getElementById('status').innerHTML = "4";
			if(!$$ttsState){
				//speakText("4");
			}
		} else if(parseInt($$data.right) == 1009 && parseInt($$data.left) == 1010){
			document.getElementById('status').innerHTML = "5";
			if(!$$ttsState){
				//speakText("5");
			}
		} else if(parseInt($$data.right) == 1011 && parseInt($$data.left) == 1012){
			document.getElementById('status').innerHTML = "6";
			if(!$$ttsState){
				//speakText("6");
			}
		} else if(parseInt($$data.right) == 1013 && parseInt($$data.left) == 1014){
			document.getElementById('status').innerHTML = "7";
			if(!$$ttsState){
				//speakText("7");
			}
		} else if(parseInt($$data.right) == 1015 && parseInt($$data.left) == 1016){
			document.getElementById('status').innerHTML = "8";
			if(!$$ttsState){
				//speakText("8");
			}
		} else if(parseInt($$data.right) == 1017 && parseInt($$data.left) == 1018){
			document.getElementById('status').innerHTML = "9";
			if(!$$ttsState){
				//speakText(9");
			}
		} else {
			document.getElementById('status').innerHTML = "N/A";
			if(!$$ttsState){
				//speakText("Simbol tidak diketahui");
			}
		}
	} else {
			document.getElementById('status').innerHTML = "-";
			if(!$$ttsState){
				//speakText("Data belum siap");
			}
	}	
}


// Pull to refresh content
var $ptrContent = $$('.ptr-content');
// Add 'refresh' listener on it
$ptrContent.on('ptr:refresh', function (e) {
  // Emulate 2s loading
  setTimeout(function () {
    refOnce();
    app.ptr.done(); // or e.detail();
  }, 2000);
});