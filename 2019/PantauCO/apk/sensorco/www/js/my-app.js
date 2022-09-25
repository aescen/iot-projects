// Init framework7
var app = new Framework7({
  // App root element
  root: '#app',
  // App Name
  name: 'Sensor CO',
  // App id
  id: 'id.plnm.sensorco',
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
    hideNavbarOnOpe:false,
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
var $$data;
var $$fbI;
var $$fbO;
var $$db;
var $$valKipas;
//var $$kipas = [0];
var $$sensors = ['Sensor 1', 'Sensor 2', 'Kadar PPM', 'Kipas 1'];
var $$idCoS = ['coSensor1', 'coSensor2', 'coPPM', 'relayKipas1'];
var $$levelVal = ['undefined', 'undefined', 'undefined', 'undefined'];
var $$ = Dom7;

// Initialize Firebase
function fbInit(){
	var config = {
		apiKey: "...",
		authDomain: "...",
		databaseURL: "...",
		projectId: "...",
		storageBucket: "...",
		messagingSenderId: "..."
	};
	firebase.initializeApp(config);
	// Get a reference to the database service
	$$db = firebase.database();
	/*$$db.ref('relays').update({
		relayKipas1: 0
	});*/
	$$fbI=true;
}
//check level
function checkLevel(x){
	if (x == 1){
		return "Baik";
	}
	else if (x == 0){
		return "Buruk";
	}
	else {return "null";}
}
// check value
function checkVal(x){
	if (x == 1 || x == 0){
		if (x == 1){
			return "Hidup";
		}
		else if (x == 0){
			return "Mati";
		}
	}
	else {return "n/a";}
}
/* obtain data when app is starting or data is updated */
function fbOn(){
	$$db.ref().on("value", function(snapshot) {
		$$data = snapshot.child("sensors").val();
		$$valKipas = snapshot.child("relays").val();
		$$kipas = [$$valKipas.relayKipas1];
		var a1 = checkLevel($$data.coSensor1); var a2 = checkLevel($$data.coSensor2);
		var k1 = checkVal($$valKipas.relayKipas1);
		var ppm = $$data.coPPM + " ppm";
		document.getElementById('coSensor1').innerHTML = a1;
		document.getElementById('coSensor2').innerHTML = a2;
		document.getElementById('coPPM').innerHTML = ppm;
		document.getElementById('relayKipas1').innerHTML = k1;
		$$levelVal = [a1, a2, ppm, k1];
		//$$kipas = [k1];
		app.preloader.hide();
		$$fbO = true;
		}, function (error) {
	});
}
/* obtain data once */
function refOnce(){
	if(!$$fbI){
		fbInit();
		if(!$$fbO){fbOn();}
	}
	else{
		$$db.ref().once("value").then(
			function(snapshot) {
				$$data = snapshot.child("sensors").val();
				$$valKipas = snapshot.child("relays").val();
				$$kipas = [$$valKipas.relayKipas1];
				var a1 = checkLevel($$data.coSensor1);
				var a2 = checkLevel($$data.coSensor2);
				var ppm = $$data.coPPM + " ppm";
				var k1 = checkLevel($$data.relayKipas1);
				$$levelVal = [a1, a2, ppm, k1];
				//$$kipas = [k1];
				app.preloader.hide();
			}
		)
	}
};

// Pull to refresh content
var $ptrContent = $$('.ptr-content');
// Add 'refresh' listener on it
$ptrContent.on('ptr:refresh', function (e) {
  // Emulate 2s loading
  refOnce();
  setTimeout(function () {
    var sensor = $$sensors[Math.floor(Math.random() * $$sensors.length)];
	var idcs = $$idCoS[Math.floor(Math.random() * $$idCoS.length)];
    var level = $$levelVal[Math.floor(Math.random() * $$levelVal.length)];
    var itemHTML =
		'<div class="card card-outline">'+
		  '<div class="card-header">'+sensor+'</div>'+
		  '<div class="card-content"></div>'+
		  '<div class="card-footer" id="'+idcs+'">'+level+'</div>'+
		'</div>';
    // Prepend new list element
    $ptrContent.find('.cardContent').prepend(itemHTML);
    // When loading done, we need to reset it
    app.ptr.done(); // or e.detail();
  }, 2000);
});