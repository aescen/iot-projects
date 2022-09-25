// Init framework7
var app = new Framework7({
  // App root element
  root: '#app',
  // App Name
  name: 'Monitor Level UV',
  // App id
  id: 'id.ac.plnm.monitoring.uv',
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
var $$serverurl = "http://192.168.202.1/uv/index.php/loaddata.php"; //WiFi
//var $$serverurl = "http://192.168.137.101/uv/index.php/loaddata.php"; //LAN
//var $$serverurl = "http://localhost/uv/index.php/loaddata.php";

function loadJSONNode1() {
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
		  
		  function searchData(idData){
				var searchVal = idData;
				for (var i = 0 ; i < jsonObj.length ; i++){
					if (jsonObj[i].id == searchVal){
						return (jsonObj[i].value);
					}
				}
		  }

		  // jsonObj variable now contains the data structure and can
		  // be accessed as jsonObj.motion
		  
		  //Node 1
		  //fan
		  if(searchData('fan1') == 0){
			  document.getElementById("fan1").innerHTML = "OFF";
			  document.getElementById("imgFan1").innerHTML = '<img src="./img/fan-grey.png" width="44"/>';
		  }
		  else if(searchData('fan1') == 1){
			  document.getElementById("fan1").innerHTML = "ON";
			  document.getElementById("imgFan1").innerHTML = '<img src="./img/fan.png" width="44"/>';
		  }
		  
		  //humidity
		  document.getElementById("humidity1").innerHTML = searchData('humidity1');
		  document.getElementById("imgHumid1").innerHTML = '<img src="./img/humid.png" width="44"/>';
		  
		  //lamp
		  if(searchData('lamp1') == 0){
			  document.getElementById("lamp1").innerHTML = "OFF";
			  document.getElementById("imgLamp1").innerHTML = '<img src="./img/lamp-grey.png" width="44"/>';
		  }
		  else if(searchData('lamp1') == 1){
			  document.getElementById("lamp1").innerHTML = "ON";
			  document.getElementById("imgLamp1").innerHTML = '<img src="./img/lamp.png" width="44"/>';
		  }
		  
		  //temperature
		  document.getElementById("temperature1").innerHTML = searchData('temperature1');
		  document.getElementById("imgTemp1").innerHTML = '<img src="./img/temp.png" width="44"/>';
		  
		  //uvLevel
		  document.getElementById("uvLevel1").innerHTML = searchData('uvLevel1');
		  document.getElementById("imgUV1").innerHTML = '<img src="./img/uv.png" width="44"/>';
		  
		  //uvIntensity
		  document.getElementById("uvIntensity1").innerHTML = searchData('uvIntensity1');
		  document.getElementById("imgUVIntensity1").innerHTML = '<img src="./img/uvintensity.png" width="44"/>';
		  
		  //uvLambda
		  document.getElementById("uvLambda1").innerHTML = searchData('uvLambda1');
		  document.getElementById("imgUVLambda1").innerHTML = '<img src="./img/uvlambda.png" width="44"/>';
		  
		  //Lux
		  document.getElementById("luxLevel1").innerHTML = searchData('lux1');
		  document.getElementById("imgLux1").innerHTML = '<img src="./img/lux.png" width="44"/>';
		 
	   }
	   else{
	      //Node 1
		  document.getElementById("humidity1").innerHTML = "...";
		  document.getElementById("imgHumid1").innerHTML = '<img src="./img/humid-grey.png" width="44"/>';
		  
		  document.getElementById("temperature1").innerHTML = "...";
		  document.getElementById("imgTemp1").innerHTML = '<img src="./img/temp-grey.png" width="44"/>';
		  
		  document.getElementById("uvLevel1").innerHTML = "...";
		  document.getElementById("imgUV1").innerHTML = '<img src="./img/uv-grey.png" width="44"/>';
		  
		  document.getElementById("uvIntensity1").innerHTML = "...";
		  document.getElementById("imgUVIntensity1").innerHTML = '<img src="./img/uvintensity-grey.png" width="44"/>';
		  
		  document.getElementById("uvLambda1").innerHTML = "...";
		  document.getElementById("imgUVLambda1").innerHTML = '<img src="./img/uvlambda-grey.png" width="44"/>';
		  
		  document.getElementById("luxLevel1").innerHTML = "...";
		  document.getElementById("imgLux1").innerHTML = '<img src="./img/lux-grey.png" width="44"/>';
		  
		  document.getElementById("fan1").innerHTML = "...";
		  document.getElementById("imgFan1").innerHTML = '<img src="./img/fan-grey.png" width="44"/>';
		  
		  document.getElementById("lamp1").innerHTML = "...";
		  document.getElementById("imgLamp1").innerHTML = '<img src="./img/lamp-grey.png" width="44"/>';
	   }
	};

	http_request.open("POST", $$serverurl, true);
	http_request.setRequestHeader("X-Requested-With", "XMLHttpRequest");
	http_request.setRequestHeader("Content-type", "application/x-www-form-urlencoded; charset=UTF-8");
	http_request.send("tabel=uv");
	
	app.preloader.hide();
}

function loadJSONNode2() {
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
		  
		  function searchData(idData){
				var searchVal = idData;
				for (var i = 0 ; i < jsonObj.length ; i++){
					if (jsonObj[i].id == searchVal){
						return (jsonObj[i].value);
					}
				}
		  }

		  // jsonObj variable now contains the data structure and can
		  // be accessed as jsonObj.motion
		  
		  //Node 2
		  //fan
		  if(searchData('fan2') == 0){
			  document.getElementById("fan2").innerHTML = "OFF";
			  document.getElementById("imgFan2").innerHTML = '<img src="./img/fan-grey.png" width="44"/>';
		  }
		  else if(searchData('fan2') == 1){
			  document.getElementById("fan2").innerHTML = "ON";
			  document.getElementById("imgFan2").innerHTML = '<img src="./img/fan.png" width="44"/>';
		  }
		  
		  //humidity
		  document.getElementById("humidity2").innerHTML = searchData('humidity2');
		  document.getElementById("imgHumid2").innerHTML = '<img src="./img/humid.png" width="44"/>';
		  
		  //lamp
		  if(searchData('lamp2') == 0){
			  document.getElementById("lamp2").innerHTML = "OFF";
			  document.getElementById("imgLamp2").innerHTML = '<img src="./img/lamp-grey.png" width="44"/>';
		  }
		  else if(searchData('lamp2') == 1){
			  document.getElementById("lamp2").innerHTML = "ON";
			  document.getElementById("imgLamp2").innerHTML = '<img src="./img/lamp.png" width="44"/>';
		  }
		  
		  //temperature
		  document.getElementById("temperature2").innerHTML = searchData('temperature2');
		  document.getElementById("imgTemp2").innerHTML = '<img src="./img/temp.png" width="44"/>';
		  
		  //uvLevel
		  document.getElementById("uvLevel2").innerHTML = searchData('uvLevel2');
		  document.getElementById("imgUV2").innerHTML = '<img src="./img/uv.png" width="44"/>';
		  
		  //uvIntensity
		  document.getElementById("uvIntensity2").innerHTML = searchData('uvIntensity2');
		  document.getElementById("imgUVIntensity2").innerHTML = '<img src="./img/uvintensity.png" width="44"/>';
		  
		  //uvLambda
		  document.getElementById("uvLambda2").innerHTML = searchData('uvLambda2');
		  document.getElementById("imgUVLambda2").innerHTML = '<img src="./img/uvlambda.png" width="44"/>';
		  
		  //Lux
		  document.getElementById("luxLevel2").innerHTML = searchData('lux2');
		  document.getElementById("imgLux2").innerHTML = '<img src="./img/lux.png" width="44"/>';
		  
	   }
	   else{
		  
		  //Node 2
		  document.getElementById("humidity2").innerHTML = "...";
		  document.getElementById("imgHumid2").innerHTML = '<img src="./img/humid-grey.png" width="44"/>';
		  
		  document.getElementById("temperature2").innerHTML = "...";
		  document.getElementById("imgTemp2").innerHTML = '<img src="./img/temp-grey.png" width="44"/>';
		  
		  document.getElementById("uvLevel2").innerHTML = "...";
		  document.getElementById("imgUV2").innerHTML = '<img src="./img/uv-grey.png" width="44"/>';
		  
		  document.getElementById("uvIntensity2").innerHTML = "...";
		  document.getElementById("imgUVIntensity2").innerHTML = '<img src="./img/uvintensity-grey.png" width="44"/>';
		  
		  document.getElementById("uvLambda2").innerHTML = "...";
		  document.getElementById("imgUVLambda2").innerHTML = '<img src="./img/uvlambda-grey.png" width="44"/>';
		  
		  document.getElementById("luxLevel2").innerHTML = "...";
		  document.getElementById("imgLux2").innerHTML = '<img src="./img/lux-grey.png" width="44"/>';
		  
		  document.getElementById("fan2").innerHTML = "...";
		  document.getElementById("imgFan2").innerHTML = '<img src="./img/fan-grey.png" width="44"/>';
		  
		  document.getElementById("lamp2").innerHTML = "...";
		  document.getElementById("imgLamp2").innerHTML = '<img src="./img/lamp-grey.png" width="44"/>';
	   }
	};

	http_request.open("POST", $$serverurl, true);
	http_request.setRequestHeader("X-Requested-With", "XMLHttpRequest");
	http_request.setRequestHeader("Content-type", "application/x-www-form-urlencoded; charset=UTF-8");
	http_request.send("tabel=uv");
	
	app.preloader.hide();
}