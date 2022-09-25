// Init framework7
var app = new Framework7({
  // App root element
  root: '#app',
  // App Name
  name: 'Monitor Jamur',
  // App id
  id: 'id.ac.plnm.monitoring.jamur',
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
// global vars
var $$ = Dom7;
var $$data;
var $$fbI;
var $$fbO;
var $$db

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
	$$db.ref("/jtd/RakagayuhJamur/").on("value", function(snapshot) {
		$$data = snapshot.child("data").val();
		parseData();
		app.preloader.hide();
		$$fbO = true;
		}, function (error) {
	});
}
/* obtain data once */
function refOnce(){
	if(!$$fbI){
		fbInit();
		if(!$$fbO){
			fbOn();
		}
	}
	else{
		$$db.ref("/jtd/RakagayuhJamur/").once("value").then(
			function(snapshot) {
				$$data = snapshot.child("data").val();
				parseData();
				app.preloader.hide();
			}
		)
	}
};

function parseData(){
	document.getElementById('imgHumid').innerHTML = '<img src="./img/humid.png" width="44"/>';
	document.getElementById('imgTemp').innerHTML = '<img src="./img/temp.png" width="44"/>';
	document.getElementById('imgWaterPh').innerHTML = '<img src="./img/water-ph.png" width="44"/>';
	document.getElementById('imgSoilPh').innerHTML = '<img src="./img/soil-ph.png" width="44"/>';
	document.getElementById('imgDensity').innerHTML = '<img src="./img/density.png" width="44"/>';
	
	document.getElementById('humidity').innerHTML = $$data.Kelembaban;
	document.getElementById('temperature').innerHTML = $$data.Suhu + ' \u00B0C';
	document.getElementById('waterPhLevel').innerHTML = $$data.pHAir;
	document.getElementById('soilPhLevel').innerHTML = $$data.pHTanah;
	document.getElementById('density').innerHTML = $$data.Kerapatan;
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

window.setInterval(function () {
	refOnce();
}, 1000);