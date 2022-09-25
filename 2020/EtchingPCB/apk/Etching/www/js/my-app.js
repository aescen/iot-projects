// Init framework7
var app = new Framework7({
  // App root element
  root: '#app',
  // App Name
  name: 'Bisindo',
  // App id
  id: 'id.ac.plnm.monitoring.etching',
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
const $$urlmain = "127.0.0.1";
const $$urlRelayLampuOn = "http://" + $$urlmain + "/etching/index.php/onrelaylampu.php";
const $$urlRelayLampuOff = "http://" + $$urlmain + "/etching/index.php/offrelaylampu.php";
const $$urlRelayGoyangOn = "http://" + $$urlmain + "/etching/index.php/onrelaygoyang.php";
const $$urlRelayGoyangOff = "http://" + $$urlmain + "/etching/index.php/offrelaygoyang.php";
const $$urlLoadData = "http://" + $$urlmain + "/etching/index.php/loaddata.php";

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

function offRelayGoyang(){
	var http_request = new XMLHttpRequest();
	try{
	   // Opera 8.0+, Firefox, Chrome, Safari
	   http_request = new XMLHttpRequest();
	}catch (e) {
	   // Internet Explorer Browsers
	   try{
		  http_request = new ActiveXObject("Msxml2.XMLHTTP");
			
	   }catch (e) {
		
		  try{
			 http_request = new ActiveXObject("Microsoft.XMLHTTP");
		  }catch (e) {
			 // Something went wrong
			 alert("Your browser broke!");
			 return false;
		  }
			
	   }
	}
	
	http_request.onreadystatechange = function() {
		if (http_request.readyState == 4  ) {
		  var jsonObj = JSON.parse(http_request.responseText);
		  //console.log(jsonObj)
		  
		  //relay goyang
		  if(parseInt(jsonObj[0].relaygoyang) == 0){
			  document.getElementById("buttongoyang").innerHTML = "<button class='button' onclick='onRelayGoyang();'>On</button>" +
															   "<button class='button button-active' onclick='offRelayGoyang();'>Off</button>";
		  } else if(parseInt(jsonObj[0].relaygoyang) == 1){
			  document.getElementById("buttongoyang").innerHTML = "<button class='button button-active' onclick='onRelayGoyang();'>On</button>" +
															   "<button class='button' onclick='offRelayGoyang();'>Off</button>";
		  }
		  
	   }
	   else{
		  document.getElementById("buttongoyang").innerHTML = "<button class='button' onclick='onRelayGoyang();'>On</button>" +
															   "<button class='button' onclick='offRelayGoyang();'>Off</button>";
	   }
	}
	http_request.open("POST", $$urlRelayGoyangOff, true);
	http_request.setRequestHeader("X-Requested-With", "XMLHttpRequest");
	http_request.setRequestHeader("Content-type", "application/x-www-form-urlencoded; charset=UTF-8");
	http_request.send("id=1");
	
}

function onRelayGoyang(){
	var http_request = new XMLHttpRequest();
	try{
	   // Opera 8.0+, Firefox, Chrome, Safari
	   http_request = new XMLHttpRequest();
	}catch (e) {
	   // Internet Explorer Browsers
	   try{
		  http_request = new ActiveXObject("Msxml2.XMLHTTP");
			
	   }catch (e) {
		
		  try{
			 http_request = new ActiveXObject("Microsoft.XMLHTTP");
		  }catch (e) {
			 // Something went wrong
			 alert("Your browser broke!");
			 return false;
		  }
			
	   }
	}
	
	http_request.onreadystatechange = function() {
		if (http_request.readyState == 4  ) {
		  var jsonObj = JSON.parse(http_request.responseText);
		  //console.log(jsonObj)
		  
		  //relay goyang
		  if(parseInt(jsonObj[0].relaygoyang) == 0){
			  document.getElementById("buttongoyang").innerHTML = "<button class='button' onclick='onRelayGoyang();'>On</button>" +
															   "<button class='button button-active' onclick='offRelayGoyang()'>Off</button>";
		  } else if(parseInt(jsonObj[0].relaygoyang) == 1){
			  document.getElementById("buttongoyang").innerHTML = "<button class='button button-active' onclick='onRelayGoyang();'>On</button>" +
															   "<button class='button' onclick='offRelayGoyang()'>Off</button>";
		  }
		  
	   }
	   else{
		  document.getElementById("buttongoyang").innerHTML = "<button class='button' onclick='onRelayGoyang();'>On</button>" +
															   "<button class='button' onclick='offRelayGoyang();'>Off</button>";
	   }
	}
	http_request.open("POST", $$urlRelayGoyangOn, true);
	http_request.setRequestHeader("X-Requested-With", "XMLHttpRequest");
	http_request.setRequestHeader("Content-type", "application/x-www-form-urlencoded; charset=UTF-8");
	http_request.send("id=1");
}

function offRelayLampu(){
	var http_request = new XMLHttpRequest();
	try{
	   // Opera 8.0+, Firefox, Chrome, Safari
	   http_request = new XMLHttpRequest();
	}catch (e) {
	   // Internet Explorer Browsers
	   try{
		  http_request = new ActiveXObject("Msxml2.XMLHTTP");
			
	   }catch (e) {
		
		  try{
			 http_request = new ActiveXObject("Microsoft.XMLHTTP");
		  }catch (e) {
			 // Something went wrong
			 alert("Your browser broke!");
			 return false;
		  }
			
	   }
	}
	
	http_request.onreadystatechange = function() {
		if (http_request.readyState == 4  ) {
		  var jsonObj = JSON.parse(http_request.responseText);
		  //console.log(jsonObj)
		  
		  //relay lampu
		  if(parseInt(jsonObj[0].relaylampu) == 0){
			  document.getElementById("buttonlampu").innerHTML = "<button class='button' onclick='onRelayLampu();'>On</button>" +
															   "<button class='button button-active' onclick='offRelayLampu();'>Off</button>";
		  } else if(parseInt(jsonObj[0].relaylampu) == 1){
			  document.getElementById("buttonlampu").innerHTML = "<button class='button button-active' onclick='onRelayLampu();'>On</button>" +
															   "<button class='button' onclick='offRelayLampu();'>Off</button>";
		  }
		  
	   }
	   else{
		  document.getElementById("buttonlampu").innerHTML = "<button class='button' onclick='onRelayLampu();'>On</button>" +
															   "<button class='button' onclick='offRelayLampu();'>Off</button>";
	   }
	}
	http_request.open("POST", $$urlRelayLampuOff, true);
	http_request.setRequestHeader("X-Requested-With", "XMLHttpRequest");
	http_request.setRequestHeader("Content-type", "application/x-www-form-urlencoded; charset=UTF-8");
	http_request.send("id=1");
	
}

function onRelayLampu(){
	var http_request = new XMLHttpRequest();
	try{
	   // Opera 8.0+, Firefox, Chrome, Safari
	   http_request = new XMLHttpRequest();
	}catch (e) {
	   // Internet Explorer Browsers
	   try{
		  http_request = new ActiveXObject("Msxml2.XMLHTTP");
			
	   }catch (e) {
		
		  try{
			 http_request = new ActiveXObject("Microsoft.XMLHTTP");
		  }catch (e) {
			 // Something went wrong
			 alert("Your browser broke!");
			 return false;
		  }
			
	   }
	}
	
	http_request.onreadystatechange = function() {
		if (http_request.readyState == 4  ) {
		  var jsonObj = JSON.parse(http_request.responseText);
		  //console.log(jsonObj)
		  
		  //relay lampu
		  if(parseInt(jsonObj[0].relaylampu) == 0){
			  document.getElementById("buttonlampu").innerHTML = "<button class='button' onclick='onRelayLampu();'>On</button>" +
															   "<button class='button button-active' onclick='offRelayLampu()'>Off</button>";
		  } else if(parseInt(jsonObj[0].relaylampu) == 1){
			  document.getElementById("buttonlampu").innerHTML = "<button class='button button-active' onclick='onRelayLampu();'>On</button>" +
															   "<button class='button' onclick='offRelayLampu()'>Off</button>";
		  }
		  
	   }
	   else{
		  document.getElementById("buttonlampu").innerHTML = "<button class='button' onclick='onRelayLampu();'>On</button>" +
															   "<button class='button' onclick='offRelayLampu();'>Off</button>";
	   }
	}
	http_request.open("POST", $$urlRelayLampuOn, true);
	http_request.setRequestHeader("X-Requested-With", "XMLHttpRequest");
	http_request.setRequestHeader("Content-type", "application/x-www-form-urlencoded; charset=UTF-8");
	http_request.send("id=1");
}

function loadJSON() {
	var http_request = new XMLHttpRequest();
	try{
	   // Opera 8.0+, Firefox, Chrome, Safari
	   http_request = new XMLHttpRequest();
	}catch (e) {
	   // Internet Explorer Browsers
	   try{
		  http_request = new ActiveXObject("Msxml2.XMLHTTP");
			
	   }catch (e) {
		
		  try{
			 http_request = new ActiveXObject("Microsoft.XMLHTTP");
		  }catch (e) {
			 // Something went wrong
			 alert("Your browser broke!");
			 return false;
		  }
			
	   }
	}
	
	http_request.onreadystatechange = function() {

	   if (http_request.readyState == 4  ) {
		  // Javascript function JSON.parse to parse JSON data
		  var jsonObj = JSON.parse(http_request.responseText);
		  //console.log(jsonObj)

		  // jsonObj variable now contains the data structure and can
		  // be accessed as jsonObj.motion
		  
		  //etching
		  document.getElementById("etching").innerHTML = jsonObj[0].etching;
		  
	   }
	   else{
		  document.getElementById("etching").innerHTML = "...";
	   }
	};

	http_request.open("POST", $$urlLoadData, true);
	http_request.setRequestHeader("X-Requested-With", "XMLHttpRequest");
	http_request.setRequestHeader("Content-type", "application/x-www-form-urlencoded; charset=UTF-8");
	http_request.send("tabel=etching");
	
	app.preloader.hide();
}

function loadJSONOnce() {
	var http_request = new XMLHttpRequest();
	try{
	   // Opera 8.0+, Firefox, Chrome, Safari
	   http_request = new XMLHttpRequest();
	}catch (e) {
	   // Internet Explorer Browsers
	   try{
		  http_request = new ActiveXObject("Msxml2.XMLHTTP");
			
	   }catch (e) {
		
		  try{
			 http_request = new ActiveXObject("Microsoft.XMLHTTP");
		  }catch (e) {
			 // Something went wrong
			 alert("Your browser broke!");
			 return false;
		  }
			
	   }
	}
	
	http_request.onreadystatechange = function() {

	   if (http_request.readyState == 4  ) {
		  // Javascript function JSON.parse to parse JSON data
		  var jsonObj = JSON.parse(http_request.responseText);
		  //console.log(jsonObj)

		  // jsonObj variable now contains the data structure and can
		  // be accessed as jsonObj.motion
		  
		  //etching
		  document.getElementById("etching").innerHTML = jsonObj[0].etching;		  
		  
		  //relay goyang
		  if(parseInt(jsonObj[0].relaygoyang) == 0){
			  document.getElementById("buttongoyang").innerHTML = "<button class='button' onclick='onRelayGoyang();'>On</button>" +
															   "<button class='button button-active' onclick='offRelayGoyang();'>Off</button>";
		  } else if(parseInt(jsonObj[0].relaygoyang) == 1){
			  document.getElementById("buttongoyang").innerHTML = "<button class='button button-active' onclick='onRelayGoyang();'>On</button>" +
															   "<button class='button' onclick='offRelayGoyang();'>Off</button>";
		  }
		  
		  
		  
		  //relay lampu
		  if(parseInt(jsonObj[0].relaylampu) == 0){
			  document.getElementById("buttonlampu").innerHTML = "<button class='button' onclick='onRelayLampu();'>On</button>" +
															   "<button class='button button-active' onclick='offRelayLampu();'>Off</button>";
		  } else if(parseInt(jsonObj[0].relaylampu) == 1){
			  document.getElementById("buttonlampu").innerHTML = "<button class='button button-active' onclick='onRelayLampu();'>On</button>" +
															   "<button class='button' onclick='offRelayLampu();'>Off</button>";
		  }
		  
	   }
	   else{
			document.getElementById("etching").innerHTML = "...";
			document.getElementById("buttongoyang").innerHTML = "<button class='button' onclick='onRelayGoyang();'>On</button>" +
															    "<button class='button' onclick='offRelayGoyang();'>Off</button>";
			document.getElementById("buttonlampu").innerHTML = "<button class='button' onclick='onRelayLampu();'>On</button>" +
															    "<button class='button' onclick='offRelayLampu();'>Off</button>";
	   }
	};

	http_request.open("POST", $$urlLoadData, true);
	http_request.setRequestHeader("X-Requested-With", "XMLHttpRequest");
	http_request.setRequestHeader("Content-type", "application/x-www-form-urlencoded; charset=UTF-8");
	http_request.send("tabel=etching");
	
	app.preloader.hide();
}