var $$ = Dom7;
var $$data;
var $$fbI;
var $$fbO;
var $$db;
var $$err = false;
var $$devReady = false;
var $$timerx = null;
var $$mode = 0;

var app = new Framework7({
  root: '#app', // App root element

  id: 'id.ycmlg.mesinvacuumfrying', // App bundle ID
  name: 'Mesin Frying', // App name
  theme: 'md', // Automatic theme detection
  autoDarkTheme : true,
  // App root data
  data() {
    return {
      foo: 'bar'
    };
  },
  // App root methods
  methods: {
    doSomething() {
      // ...
    }
  },

  navbar: {
    hideOnPageScroll: false,
    mdCenterTitle: false,
  },


  // App routes
  routes: routes,


  // Input settings
  input: {
    scrollIntoViewOnFocus: Framework7.device.cordova && !Framework7.device.electron,
    scrollIntoViewCentered: Framework7.device.cordova && !Framework7.device.electron,
  },
  // Cordova Statusbar settings
  statusbar: {
    iosOverlaysWebView: false,
    androidOverlaysWebView: true,
  },
  on: {
    init: function () {
      var f7 = this;
      if (f7.device.cordova) {
        // Init cordova APIs (see cordova-app.js)
        cordovaApp.init(f7);
      }
    },
    pageInit: function () {
      console.log('Page initialized');
      $$devReady = true;
      refOnce();
    },
  },
});

var $$mainView = app.views.create('.view-main', {
    url: '/'
});


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

function consoleToast(str){
    // Create bottom toast
    var toastBottom = app.toast.create({
      text: str,
      closeTimeout: 2000,
    });
    toastBottom.open();
}


// Initialize Firebase
function fbInit(){
    var config = {
        apiKey: "...",
        authDomain: "...",
        databaseURL: "...",
        projectId: "...",
        storageBucket: "...",
        messagingSenderId: "...",
        appId: "...",
        measurementId: "..."
    };
    // Initialize Firebase
    firebase.initializeApp(config);
    //firebase.analytics();

    $$db = firebase.database();
    $$fbI = true;
    console.log("fbInit");

}

function fbOn(){
    /* obtain data when app is starting or data is updated */
    $$db.ref("/Berlin/").on("value", function(snapshot) {
        $$data = snapshot.val();
        //console.log($$data);
        if ( $$data.Thermal1 !== undefined) {
            document.getElementById('img-thermal1').src = 'assets/thermal.png';
            document.getElementById('thermal1').innerHTML = $$data.Thermal1 + ' \u00B0C';
        } else {
            document.getElementById('img-thermal1').src = 'assets/thermal-grey.png';
            document.getElementById('thermal1').innerHTML = $$data.Thermal1 + ' \u00B0C';
        }

        // if ( $$data.Thermal2 !== undefined) {
        // 	document.getElementById('img-thermal2').src = 'assets/thermal.png';
        // 	document.getElementById('thermal2').innerHTML = $$data.Thermal2 + ' \u00B0C';
        // } else {
        // 	document.getElementById('img-thermal2').src = 'assets/thermal-grey.png';
        // 	document.getElementById('thermal2').innerHTML = $$data.Thermal2 + ' \u00B0C';
        // }

        if ( $$data.TekananUdara !== undefined) {
            document.getElementById('img-tekananudara').src = 'assets/thermal.png';
            document.getElementById('tekananudara').innerHTML = $$data.TekananUdara + ' cmHg';
        } else {
            document.getElementById('img-tekananudara').src = 'assets/thermal-grey.png';
            document.getElementById('tekananudara').innerHTML = $$data.TekananUdara + ' cmHg';
        }

        if($$data.Mode !== undefined){
          $$mode = parseInt($$data.Mode);
        } else {
          $$mode = 1;
          setMode(1);
        }

        if($$mode == 1){
          $$('#modePisang').addClass('button-active');
          $$('#modeNangka').removeClass('button-active');
          $$('#modeApel').removeClass('button-active');
          document.getElementById("mesinOn").disabled = false;
          document.getElementById("mesinOff").disabled = false;
        } else if($$mode == 2){
          $$('#modePisang').removeClass('button-active');
          $$('#modeNangka').addClass('button-active');
          $$('#modeApel').removeClass('button-active');
          document.getElementById("mesinOn").disabled = false;
          document.getElementById("mesinOff").disabled = false;
        } else if($$mode == 3){
          $$('#modePisang').removeClass('button-active');
          $$('#modeNangka').removeClass('button-active');
          $$('#modeApel').addClass('button-active');
          document.getElementById("mesinOn").disabled = false;
          document.getElementById("mesinOff").disabled = false;
        } else{
          $$('#modePisang').removeClass('button-active');
          $$('#modeNangka').removeClass('button-active');
          $$('#modeApel').removeClass('button-active');
          $$('#onoffmesin').addClass('color-gray');
          document.getElementById("mesinOn").setAttribute("disabled", true);
          document.getElementById("mesinOff").setAttribute("disabled", true);
        }

        if(parseInt($$data.MenyalakanMesin) == 1 && $$mode != 0){
          document.getElementById("modePisang").setAttribute("disabled", true);
          document.getElementById("modeNangka").setAttribute("disabled", true);
          document.getElementById("modeApel").setAttribute("disabled", true);
          $$('#modemesin').addClass('color-gray');
          $$('#mesinOff').removeClass('button-active');
          $$('#mesinOn').addClass('button-active');
          startTimer();
        } else if(parseInt($$data.MenyalakanMesin) == 0){
            document.getElementById("modePisang").disabled = false;
            document.getElementById("modeNangka").disabled = false;
            document.getElementById("modeApel").disabled = false;
            $$('#modemesin').removeClass('color-gray');
            $$('#mesinOn').removeClass('button-active');
            $$('#mesinOff').addClass('button-active');
            stopTimer();
        }

        console.log("fbOn");

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
            //writeMesinData(0);
            if(!$$fbO){
                fbOn();
            }
        } else {
            $$db.ref("/Berlin/").once("value").then(
                function(snapshot) {
                    $$data = snapshot.val();
                    //console.log($$data);
                    if ( $$data.Thermal1 !== undefined) {
                        document.getElementById('img-thermal1').src = 'assets/thermal.png';
                        document.getElementById('thermal1').innerHTML = $$data.Thermal1 + ' \u00B0C';
                    } else {
                        document.getElementById('img-thermal1').src = 'assets/thermal-grey.png';
                        document.getElementById('thermal1').innerHTML = $$data.Thermal1 + ' \u00B0C';
                    }

                    // if ( $$data.Thermal2 !== undefined) {
                    // 	document.getElementById('img-thermal2').src = 'assets/thermal.png';
                    // 	document.getElementById('thermal2').innerHTML = $$data.Thermal2 + ' \u00B0C';
                    // } else {
                    // 	document.getElementById('img-thermal2').src = 'assets/thermal-grey.png';
                    // 	document.getElementById('thermal2').innerHTML = $$data.Thermal2 + ' \u00B0C';
                    // }

                    if ( $$data.TekananUdara !== undefined) {
                        document.getElementById('img-tekananudara').src = 'assets/thermal.png';
                        document.getElementById('tekananudara').innerHTML = $$data.TekananUdara + ' cmHg';
                    } else {
                        document.getElementById('img-tekananudara').src = 'assets/thermal-grey.png';
                        document.getElementById('tekananudara').innerHTML = $$data.TekananUdara + ' cmHg';
                    }

                    if($$data.Mode !== undefined){
                      $$mode = parseInt($$data.Mode);
                    } else {
                      $$mode = 1;
                      setMode(1);
                    }
    
                    if($$mode == 1){
                      $$('#modePisang').addClass('button-active');
                      $$('#modeNangka').removeClass('button-active');
                      $$('#modeApel').removeClass('button-active');
                      document.getElementById("mesinOn").disabled = false;
                      document.getElementById("mesinOff").disabled = false;
                    } else if($$mode == 2){
                      $$('#modePisang').removeClass('button-active');
                      $$('#modeNangka').addClass('button-active');
                      $$('#modeApel').removeClass('button-active');
                      document.getElementById("mesinOn").disabled = false;
                      document.getElementById("mesinOff").disabled = false;
                    } else if($$mode == 3){
                      $$('#modePisang').removeClass('button-active');
                      $$('#modeNangka').removeClass('button-active');
                      $$('#modeApel').addClass('button-active');
                      document.getElementById("mesinOn").disabled = false;
                      document.getElementById("mesinOff").disabled = false;
                    } else{
                      $$('#modePisang').removeClass('button-active');
                      $$('#modeNangka').removeClass('button-active');
                      $$('#modeApel').removeClass('button-active');
                      $$('#onoffmesin').addClass('color-gray');
                      document.getElementById("mesinOn").setAttribute("disabled", true);
                      document.getElementById("mesinOff").setAttribute("disabled", true);
                    }
    
                    if(parseInt($$data.MenyalakanMesin) == 1 && $$mode != 0){
                      document.getElementById("modePisang").setAttribute("disabled", true);
                      document.getElementById("modeNangka").setAttribute("disabled", true);
                      document.getElementById("modeApel").setAttribute("disabled", true);
                      $$('#modemesin').addClass('color-gray');
                      $$('#mesinOff').removeClass('button-active');
                      $$('#mesinOn').addClass('button-active');
                      startTimer();
                    } else if(parseInt($$data.MenyalakanMesin) == 0){
                        document.getElementById("modePisang").disabled = false;
                        document.getElementById("modeNangka").disabled = false;
                        document.getElementById("modeApel").disabled = false;
                        $$('#modemesin').removeClass('color-gray');
                        $$('#mesinOn').removeClass('button-active');
                        $$('#mesinOff').addClass('button-active');
                        stopTimer();
                    }

                    console.log("fbOnce");
                    app.preloader.hide();
                }
            )
        }
    } else {
        console.log("Error/device not ready.");
        //consoleToast("Error/device not ready.");
        app.preloader.hide();
    }
};

// Pull to refresh content
var $ptrContent = $$('.ptr-content');
$ptrContent.on('ptr:refresh', function (e) {
  setTimeout(function () {
        $$db.ref("/Berlin/").once("value").then(
            function(snapshot) {
                $$data = snapshot.val();
                //console.log($$data);
                if ( $$data.Thermal1 !== undefined) {
                    document.getElementById('img-thermal1').src = 'assets/thermal.png';
                    document.getElementById('thermal1').innerHTML = $$data.Thermal1 + ' \u00B0C';
                } else {
                    document.getElementById('img-thermal1').src = 'assets/thermal-grey.png';
                    document.getElementById('thermal1').innerHTML = $$data.Thermal1 + ' \u00B0C';
                }

                // if ( $$data.Thermal2 !== undefined) {
                // 	document.getElementById('img-thermal2').src = 'assets/thermal.png';
                // 	document.getElementById('thermal2').innerHTML = $$data.Thermal2 + ' \u00B0C';
                // } else {
                // 	document.getElementById('img-thermal2').src = 'assets/thermal-grey.png';
                // 	document.getElementById('thermal2').innerHTML = $$data.Thermal2 + ' \u00B0C';
                // }

                if ( $$data.TekananUdara !== undefined) {
                    document.getElementById('img-tekananudara').src = 'assets/thermal.png';
                    document.getElementById('tekananudara').innerHTML = $$data.TekananUdara + ' cmHg';
                } else {
                    document.getElementById('img-tekananudara').src = 'assets/thermal-grey.png';
                    document.getElementById('tekananudara').innerHTML = $$data.TekananUdara + ' cmHg';
                }

                if($$data.Mode !== undefined){
                  $$mode = parseInt($$data.Mode);
                } else {
                  $$mode = 1;
                  setMode(1);
                }

                if($$mode == 1){
                  $$('#modePisang').addClass('button-active');
                  $$('#modeNangka').removeClass('button-active');
                  $$('#modeApel').removeClass('button-active');
                  document.getElementById("mesinOn").disabled = false;
                  document.getElementById("mesinOff").disabled = false;
                } else if($$mode == 2){
                  $$('#modePisang').removeClass('button-active');
                  $$('#modeNangka').addClass('button-active');
                  $$('#modeApel').removeClass('button-active');
                  document.getElementById("mesinOn").disabled = false;
                  document.getElementById("mesinOff").disabled = false;
                } else if($$mode == 3){
                  $$('#modePisang').removeClass('button-active');
                  $$('#modeNangka').removeClass('button-active');
                  $$('#modeApel').addClass('button-active');
                  document.getElementById("mesinOn").disabled = false;
                  document.getElementById("mesinOff").disabled = false;
                } else{
                  $$('#modePisang').removeClass('button-active');
                  $$('#modeNangka').removeClass('button-active');
                  $$('#modeApel').removeClass('button-active');
                  $$('#onoffmesin').addClass('color-gray');
                  document.getElementById("mesinOn").setAttribute("disabled", true);
                  document.getElementById("mesinOff").setAttribute("disabled", true);
                }

                if(parseInt($$data.MenyalakanMesin) == 1 && $$mode != 0){
                    document.getElementById("modePisang").setAttribute("disabled", true);
                    document.getElementById("modeNangka").setAttribute("disabled", true);
                    document.getElementById("modeApel").setAttribute("disabled", true);
                    $$('#modemesin').addClass('color-gray');
                    $$('#mesinOff').removeClass('button-active');
                    $$('#mesinOn').addClass('button-active');
                    startTimer();
                } else if(parseInt($$data.MenyalakanMesin) == 0){
                    document.getElementById("modePisang").disabled = false;
                    document.getElementById("modeNangka").disabled = false;
                    document.getElementById("modeApel").disabled = false;
                    $$('#modemesin').removeClass('color-gray');
                    $$('#mesinOn').removeClass('button-active');
                    $$('#mesinOff').addClass('button-active');
                    stopTimer();
                }
            }
        );
        console.log("ptr done...");
        //consoleToast("Updated.");
        app.ptr.done();
  }, 1000);
});

function setMode(m){
    var updates = {};
    updates['/Berlin/Mode'] = Number(m);
    return firebase.database().ref().update(updates);
}

function writeMesinData(mesin) {
    var updates = {};
    updates['/Berlin/MenyalakanMesin'] = mesin;
    return firebase.database().ref().update(updates);
}

function startTimer(){
  if($$timerx == null){
    var timer = app.gauge.get('.my-timer');
        var timerMode = 0;
        if($$mode == 1){
            timerMode = 1000 * 60 * 45; //45m
        } else if($$mode == 2){
            timerMode = 1000 * 60 * 50; //50m
        } else if($$mode == 3){
            timerMode = 1000 * 60 * 60; //60m
        } else{
            consoleToast("Unknown timer mode. Skipping...");
            $$('#mesinOn').removeClass('button-active');
            $$('#mesinOff').addClass('button-active');
            stopTimer();
            return;
        }
        const milli = new Date().getTime();
        const toMilli = milli + timerMode; //90m = 5400000
        const countDownTo = new Date().setTime(toMilli);
        document.getElementById('mytimer').style.display = 'inline';

        $$timerx = setInterval(function() {
            var now = new Date().getTime();
            var distance = countDownTo - now;
            //let days = Math.floor(distance / (1000 * 60 * 60 * 24));
            var hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
            var seconds = Math.floor((distance % (1000 * 60)) / 1000);
            var val = remap(seconds, 0, 59, 1, 0);
            if(seconds > 0){
                timer.update({
                    value: val,
                    valueText: seconds,
                    labelText: hours + ":" + minutes
                });
            } else {
                timer.update({
                    value: val,
                    valueText: 60,
                    labelText: hours + ":" + minutes
                });
            }

            if (distance < 0) {
                if(parseInt($$data.MenyalakanMesin) == 1){
                    timer.update({
                        value: 100,
                        valueText: "...",
                        labelText: "EXPIRED"
                    });
                } else {
                    clearInterval($$timerx);
                    $$timerx = null;
                    document.getElementById('mytimer').style.display = 'none';

                }
            }
        }, 1000);
    }
}

function stopTimer(){
    clearInterval($$timerx);
    $$timerx = null;
    $$mode = 0;
    document.getElementById('mytimer').style.display = 'none';
}

function remap(x, in_min, in_max, out_min, out_max){
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min;
}