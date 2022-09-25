// Init framework7
var app = new Framework7({
  // App root element
  root: '#app',
  // App Name
  name: 'Monitor Kubis',
  // App id
  id: 'id.ac.plnm.monitoring.kubis',
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
	$$db.ref("/jtd/tcs/").on("value", function(snapshot) {
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
		$$db.ref("/jtd/tcs/").once("value").then(
			function(snapshot) {
				$$data = snapshot.child("data").val();
				parseData();
				app.preloader.hide();
			}
		)
	}
};

function parseData(){
	document.getElementById('tdR').innerHTML = parseFloat($$data.rgb[0]).toFixed(4);
	document.getElementById('tdG').innerHTML = parseFloat($$data.rgb[1]).toFixed(4);
	document.getElementById('tdB').innerHTML = parseFloat($$data.rgb[2]).toFixed(4);
	document.getElementById('tdColor').innerHTML = $$data.color;
	document.getElementById('tdQuality').innerHTML = $$data.quality;
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