// Init framework7
var app = new Framework7({
  // App root element
  root: '#app',
  // App Name
  name: 'Monitor Fermentasi',
  // App id
  id: 'id.ac.plnm.monitoring.fermentasi',
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
var $$data2;
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
	$$db.ref("/jtd/Fermentasi/").once("value").then(
		function(snapshot) {
			$$data = snapshot.child("data").val();
			$$db.ref("/jtd/Fermentasi2/").once("value").then(
				function(snapshot) {
					$$data2 = snapshot.child("data").val();
					parseData();
					app.preloader.hide();
				}
			)
		}
	)
	$$fbO = true;
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
		$$db.ref("/jtd/Fermentasi/").once("value").then(
			function(snapshot) {
				$$data = snapshot.child("data").val();
				$$db.ref("/jtd/Fermentasi2/").once("value").then(
					function(snapshot) {
						$$data2 = snapshot.child("data").val();
						parseData();
						app.preloader.hide();
					}
				)
			}
		)
	}
};

function parseData(){
	document.getElementById('imgAirCondition1').innerHTML = '<img src="./img/air-condition.png" width="44"/>';
	document.getElementById('imgAirCondition2').innerHTML = '<img src="./img/air-condition.png" width="44"/>';
	document.getElementById('imgTemp1').innerHTML = '<img src="./img/temp.png" width="44"/>';
	document.getElementById('imgTemp2').innerHTML = '<img src="./img/temp.png" width="44"/>';
	document.getElementById('imgMoist1').innerHTML = '<img src="./img/moist.png" width="44"/>';
	document.getElementById('imgMoist2').innerHTML = '<img src="./img/moist.png" width="44"/>';
	if(parseFloat($$data.Moist) <= 0.090){
		document.getElementById('imgStatus1').innerHTML = '<img src="./img/status-green.png" width="44"/>';
	}else if (parseFloat($$data.Moist) > 0.090){
		document.getElementById('imgStatus1').innerHTML = '<img src="./img/status-red.png" width="44"/>';
	}
	if(parseFloat($$data2.Moist) <= 0.090){
		document.getElementById('imgStatus2').innerHTML = '<img src="./img/status-green.png" width="44"/>';
	}else if (parseFloat($$data2.Moist) > 0.090){
		document.getElementById('imgStatus2').innerHTML = '<img src="./img/status-red.png" width="44"/>';
	}
	
	document.getElementById('airCondition1').innerHTML = $$data.KondisiUdara + '%';
	document.getElementById('airCondition2').innerHTML = $$data2.KondisiUdara + '%';
	document.getElementById('temperature1').innerHTML = $$data.Suhu + '\u00B0C';
	document.getElementById('temperature2').innerHTML = $$data2.Suhu + '\u00B0C';
	document.getElementById('moisture1').innerHTML = $$data.Moist;
	document.getElementById('moisture2').innerHTML = $$data2.Moist;
	if(parseFloat($$data.Moist) <= 0.090){
		document.getElementById('status1').innerHTML = 'Process done.';
	}else if (parseFloat($$data.Moist) > 0.090){
		document.getElementById('status1').innerHTML = 'In Process...';
	}
	if(parseFloat($$data2.Moist) <= 0.090){
		document.getElementById('status2').innerHTML = 'Process done.';
	}else if (parseFloat($$data2.Moist) > 0.090){
		document.getElementById('status2').innerHTML = 'In Process...';
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

window.setInterval(function () {
	refOnce();
}, 1000);