// Init framework7
var app = new Framework7({
  // App root element
  root: '#app',
  // App Name
  name: 'Monitor Alga',
  // App id
  id: 'id.ac.plnm.monitoring.alga',
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
	$$db.ref("/jtd/alga/").on("value", function(snapshot) {
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
		$$db.ref("/jtd/alga/").once("value").then(
			function(snapshot) {
				$$data = snapshot.child("data").val();
				parseData();
				app.preloader.hide();
			}
		)
	}
};

function parseData(){
	document.getElementById('imgTurbid').innerHTML = '<img src="./img/turbid.png" width="44"/>';
	document.getElementById('imgTemp').innerHTML = '<img src="./img/temp.png" width="44"/>';
	document.getElementById('imgPh').innerHTML = '<img src="./img/ph.png" width="44"/>';
	document.getElementById('turbidity').innerHTML = $$data.turbidity;
	document.getElementById('temperature').innerHTML = $$data.Suhu + ' \u00B0C';
	document.getElementById('phLevel').innerHTML = $$data.ph;
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