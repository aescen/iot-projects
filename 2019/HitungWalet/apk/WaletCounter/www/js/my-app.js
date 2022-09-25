// Init framework7
var app = new Framework7({
  // App root element
  root: '#app',
  // App Name
  name: 'Walet Monitoring',
  // App id
  id: 'id.plnm.waletmonitoring',
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
	  name:'about',
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
var $$dataLogHumid;
var $$dataLogTemp;
var $$dataLogTotal;
var $$fbI;
var $$fbO;
var $$ref;
var $$heads = ['Humidity', 'Temperature', 'Total Birds'];
var $$idCoS = ['humid', 'temp', 'total'];
var $$vals = ['null %', 'null \u00B0C', 'null walet'];
var $$ = Dom7;

// Initialize Firebase
function fbInit(){
	console.log("firebase init!")
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
	$$ref = firebase.database().ref();
	$$fbI=true;
}
function fbOn(){
	/* obtain data when app is starting or data is updated */
	console.log("firebase refOn!")
	$$ref.on("value", function(snapshot) {
		$$data = snapshot.child("data").val();
		document.getElementById('humid').innerHTML = $$data.humid + ' %';
		document.getElementById('temp').innerHTML = $$data.temp + ' \u00B0C';
		document.getElementById('total').innerHTML = $$data.total + ' walet';
		$$vals = [$$data.humid + ' %', $$data.temp + ' \u00B0C', $$data.total + ' walet'];
		$$dataLogTemp = snapshot.child("logs/temp").val();
		$$dataLogHumid = snapshot.child("logs/humid").val();
		$$dataLogTotal = snapshot.child("logs/total").val();
		app.preloader.hide();
		$$fbO = true;
	}, function (error) {
		console.log("Error: " + error.code);
	});
}
/* obtain data once */
function refOnce(){
	console.log("firebase refOnce!")
	if(!$$fbI){
		fbInit();
		if(!$$fbO){fbOn();}
	}
	else{
		$$ref.once("value").then(
			function(snapshot) {
				$$data = snapshot.child("data").val();
				$$vals = [$$data.humid + ' %', $$data.temp + ' \u00B0C', $$data.total + ' walet'];
				$$dataLogTemp = snapshot.child("logs/temp").val();
				$$dataLogHumid = snapshot.child("logs/humid").val();
				$$dataLogTotal = snapshot.child("logs/total").val();
			}
		)
	}
};

// Pull to refresh content
var $ptrContent = $$('.ptr-content');
// Add 'refresh' listener on it
$ptrContent.on('ptr:refresh', function (e) {
  // Emulate 2s loading
  console.log("ptr set!");
  setTimeout(function () {
    var head = $$heads[Math.floor(Math.random() * $$heads.length)];
	var idcs = $$idCoS[Math.floor(Math.random() * $$idCoS.length)];
    var val = $$vals[Math.floor(Math.random() * $$vals.length)];
    var itemHTML =
		'<div class="card card-outline">'+
		  '<div class="card-header">'+head+'</div>'+
		  '<div class="card-content"></div>'+
		  '<div class="card-footer" id="'+idcs+'">'+val+'</div>'+
		'</div>';
    // Prepend new list element
    $ptrContent.find('.cardContent').prepend(itemHTML);
    // When loading done, we need to reset it
    app.ptr.done(); // or e.detail();
  }, 2000);
});

function timeConverter(UNIX_timestamp){
  var a = new Date(UNIX_timestamp * 1000);
  var months = ['Jan','Feb','Mar','Apr','Mei','Jun','Jul','Agu','Sep','Okt','Nov','Des'];
  var year = a.getFullYear();
  var month = months[a.getMonth()];
  var date = a.getDate();
  var hour = a.getHours();
  var min = a.getMinutes();
  var sec = a.getSeconds();
  var time = date + ' ' + month + ' ' + year + ' ' + hour + ':' + min + ':' + sec ;
  return time;
}

function updateTables(){
	var tLog = '';
	console.log($$dataLogTemp);
	for(let key in $$dataLogTemp){  //for in loop iterates all properties in an object
		//console.log(key) ;  //print all properties in sequence
		//console.log($$dataLogTemp[key]);//print all properties values
		tLog += '<tr>'+
					'<td class="label-cell">'+ timeConverter(key) +'</td>'+
					'<td class="numeric-cell">'+ $$dataLogTemp[key] +'&deg;C</td>'+
				'</tr>';
	}
	document.getElementById('tempLog').innerHTML = tLog;

	var hLog = '';
	for(let key in $$dataLogHumid){  //for in loop iterates all properties in an object
		//console.log(key) ;  //print all properties in sequence
		//console.log($$dataLogHumid[key]);//print all properties values
		hLog += '<tr>'+
					'<td class="label-cell">'+ timeConverter(key) +'</td>'+
					'<td class="numeric-cell">'+ $$dataLogHumid[key] +'%</td>'+
				'</tr>';
	}
	document.getElementById('humidLog').innerHTML = hLog;

	var ttLog = '';
	for(let key in $$dataLogTotal){  //for in loop iterates all properties in an object
		//console.log(key) ;  //print all properties in sequence
		//console.log($$dataLogTotal[key]);//print all properties values
		ttLog += '<tr>'+
					'<td class="label-cell">'+ timeConverter(key) +'</td>'+
					'<td class="numeric-cell">'+ $$dataLogTotal[key] +'</td>'+
				'</tr>';
	}
	document.getElementById('totalLog').innerHTML = ttLog;
}

window.setInterval(function () {
	//do something
	if($$fbO == true){
		updateTables();
	}
	/*document.getElementById('tempLog').innerHTML = '<tr>'+
			'<td class="label-cell">'+ timeConverter(1515151515) +'</td>'+
			'<td class="numeric-cell">'+ 21 +'&deg;C</td>'+
		'</tr>';
	document.getElementById('humidLog').innerHTML = '<tr>'+
			'<td class="label-cell">'+ timeConverter(1515151515) +'</td>'+
			'<td class="numeric-cell">'+ 82 +'%</td>'+
		'</tr>';
	document.getElementById('totalLog').innerHTML = '<tr>'+
			'<td class="label-cell">'+ timeConverter(1515151515) +'</td>'+
			'<td class="numeric-cell">'+ 8 +'</td>'+
		'</tr>';*/
},1000);