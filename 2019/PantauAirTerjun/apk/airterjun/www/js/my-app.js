// Init framework7
var app = new Framework7({
  // App root element
  root: '#app',
  // App Name
  name: 'Monitor Air Terjun',
  // App id
  id: 'id.plnm.airterjun.monitor',
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
var $$data;
var $$fbI;
var $$fbO;
var $$db;
var $$s;
var $$status = [0, 0, 0, 0];
var $$sensors = ['Suhu air', 'Kekeruahn air', 'Kadar pH air', 'Aliran air'];
var $$idCoS = ['temp', 'turbidity', 'pH', 'flow'];
var $$levelVal = ['undefined', 'undefined', 'undefined', 'undefined'];
var $$ = Dom7;

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
	$$db.ref().on("value", function(snapshot) {
		$$data = snapshot.child("sensors").val();
		document.getElementById('temp').innerHTML = $$data.temp + ' \u00B0C';
		document.getElementById('turbidity').innerHTML = $$data.turbidity + ' %';
		document.getElementById('pH').innerHTML = $$data.ph;
		document.getElementById('flow').innerHTML = $$data.flow + ' ml';
		app.preloader.hide();
		$$fbO = true;
		}, function (error) {
	});
}
/* obtain data once */
function refOnce(){
	if(!$$fbI){
		fbInit();
		if(!$$fbO){fbOn();status();}
	}
	else{
		$$db.ref().once("value").then(
			function(snapshot) {
				$$data = snapshot.child("sensors").val();
				$$levelVal = [$$data.temp + ' \u00B0C', $$data.turbidity + ' %', $$data.ph, $$data.flow + ' ml'];
				status();
				app.preloader.hide();
			}
		)
	}
};

function status(){
	$$db.ref().once("value").then(
		function(snapshot) {
			$$data = snapshot.child("sensors").val();
			$$levelVal = [$$data.temp + ' \u00B0C', $$data.turbidity + ' %', $$data.ph, $$data.flow + ' ml'];
			if($$data.temp < 10){
				$$status[0] = 1;
			}else{
				$$status[0] = 0;
			}
			if($$data.ph < 6){
				$$status[1] = 1;
			}else{
				$$status[1] = 0;
			}
			if($$data.turbidity > 40){
				$$status[2] = 1;
			}else{
				$$status[2] = 0;
			}
			if($$data.flow > 140){
				$$status[3] = 1;
			}else{
				$$status[3] = 0;
			}
			$$s = 0;
			for(i = 0; i < 4; i++){
				$$s += $$status[i];
			}
			if($$s <= 1){
				document.getElementById("status").className = "bg-color-green";
				document.getElementById("status").classList.add('text-color-white');
				document.getElementById("status").classList.add('display-block');
				document.getElementById('status').innerHTML = '<h2 class="no-margin no-padding"></br><strong>AMAN<strong></h2>';
			}else if($$s == 2){
				document.getElementById("status").className = "bg-color-orange";
				document.getElementById("status").classList.add('text-color-white');
				document.getElementById("status").classList.add('display-block');
				document.getElementById("status").classList.add('no-padding');
				document.getElementById("status").classList.add('no-margin');
				document.getElementById('status').innerHTML = '<h2 class="no-margin no-padding"></br><strong>PERINGATAN<strong></h2>';
			}else if($$s >= 3){
				document.getElementById("status").className = "bg-color-red";
				document.getElementById("status").classList.add('text-color-white');
				document.getElementById("status").classList.add('display-block');
				document.getElementById("status").classList.add('no-padding');
				document.getElementById("status").classList.add('no-margin');
				document.getElementById('status').innerHTML = '<h2 class="no-margin no-padding"></br><strong>BAHAYA<strong></h2>';
			}			
		}
	)
}

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

window.setInterval(function () {
  //do something
  status();
},1000);