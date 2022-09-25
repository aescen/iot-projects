var $$ = Dom7;
var $$data;
var $$fbI;
var $$fbO;
var $$db;
var $$err = false;
var $$devReady = false;
var $$nid = 0;
var $$tmp = {
    "burung": -1,
    "tikus": -1,
    "speaker": -1
  };

var app = new Framework7({
  root: '#app', // App root element

  id: 'id.ycmlg.birdy', // App bundle ID
  name: 'Birdy', // App name
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

var mainView = app.views.create('.view-main', {
  url: '/'
});

window.onerror = function (msg, url, line) {
    $$err = true;
    app.preloader.hide();
    let msgs = "Message : " + msg + "<br>Line number : " + line + "<br>Url : " + url ;
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
    if (app.device.cordova) {
        let toastBottom = app.toast.create({
        text: str,
        closeTimeout: 2000,
        });
        toastBottom.open();
    }
}

//notifications
function addNotification(titlestr, textstr) {
    if (app.device.cordova) {
        cordovaApp.addNotification($$nid, titlestr, textstr);
        $$nid++;
        console.log("Notification added.");
        //consoleToast("Notification added.");
    }
    let loc = window.location.pathname;
    let dir = loc.substring(0, loc.lastIndexOf('/'));
    ////consoleToast('Loc:' + loc + ' Dir:' + dir);
    console.log('Loc:' + loc + ' Dir:' + dir);
}

// Initialize Firebase
function fbInit(){
    let config = {
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
    $$db.ref("/Roby/").on("value", function(snapshot) {
        $$data = snapshot.val();
        //console.log($$data);
        document.getElementById('img-burung').src = 'assets/burung.png';
        document.getElementById('img-tikus').src = 'assets/tikus.png';
        document.getElementById('jBurung').innerHTML = $$data.JumlahBurung > 0 ? 'Ada' : 'Tidak Ada';
        document.getElementById('jTikus').innerHTML = $$data.JumlahTikus > 0 ? 'Ada' : 'Tidak Ada';

        let burung = parseInt($$data.JumlahBurung);
        if($$tmp.burung != burung){
            if(burung > 0){
                addNotification("Deteksi Burung", "Ada");
            }
            $$tmp.burung = burung;
        }

        let tikus = parseInt($$data.JumlahTikus);
        if($$tmp.tikus != tikus){
            if(tikus > 0){
                addNotification("Deteksi Tikus", "Ada");
            }
            $$tmp.tikus = tikus;
        }
        
        // if($$tmp.speaker != $$data.MenyalakanSpeaker){
        //     if(parseInt($$data.MenyalakanSpeaker) == 1){
        //         $$('#speakerOff').removeClass('button-active');
        //         $$('#speakerOn').addClass('button-active');
        //     } else {
        //         $$('#speakerOn').removeClass('button-active');
        //         $$('#speakerOff').addClass('button-active');
        //     }
        //     $$tmp.speaker = $$data.MenyalakanSpeaker;
        // }
        
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
            if(!$$fbO){
                fbOn();
            }
        } else {
            $$db.ref("/Roby/").once("value").then(
                function(snapshot) {
                    $$data = snapshot.val();
                    //console.log($$data);
                    document.getElementById('img-burung').src = 'assets/burung.png';
                    document.getElementById('img-tikus').src = 'assets/tikus.png';
                    document.getElementById('jBurung').innerHTML = $$data.JumlahBurung > 0 ? 'Ada' : 'Tidak Ada';
                    document.getElementById('jTikus').innerHTML = $$data.JumlahTikus > 0 ? 'Ada' : 'Tidak Ada';
                    
                    let burung = parseInt($$data.JumlahBurung);
                    if($$tmp.burung != burung){
                        if(burung > 0){
                            addNotification("Deteksi Burung", "Ada");
                        }
                        $$tmp.burung = burung;
                    }

                    let tikus = parseInt($$data.JumlahTikus);
                    if($$tmp.tikus != tikus){
                        if(tikus > 0){
                            addNotification("Deteksi Tikus", "Ada");
                        }
                        $$tmp.tikus = tikus;
                    }
                    
                    // if($$tmp.speaker != $$data.MenyalakanSpeaker){
                    //     if(parseInt($$data.MenyalakanSpeaker) == 1){
                    //         $$('#speakerOff').removeClass('button-active');
                    //         $$('#speakerOn').addClass('button-active');
                    //     } else {
                    //         $$('#speakerOn').removeClass('button-active');
                    //         $$('#speakerOff').addClass('button-active');
                    //     }
                    //     $$tmp.speaker = $$data.MenyalakanSpeaker;
                    // }
                    
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

function writeSpeakerData(speaker) {
  let updates = {};
  updates['/Roby/MenyalakanSpeaker'] = speaker;

  return firebase.database().ref().update(updates);
}

// Pull to refresh content
var $ptrContent = $$('.ptr-content');
$ptrContent.on('ptr:refresh', function (e) {
  setTimeout(function () {
    $$db.ref("/Roby/").once("value").then(
            function(snapshot) {
                $$data = snapshot.val();
                //console.log($$data);
                document.getElementById('img-burung').src = 'assets/burung.png';
                document.getElementById('img-tikus').src = 'assets/tikus.png';
                document.getElementById('jBurung').innerHTML = $$data.JumlahBurung > 0 ? 'Ada' : 'Tidak Ada';
                document.getElementById('jTikus').innerHTML = $$data.JumlahTikus > 0 ? 'Ada' : 'Tidak Ada';
                
                let burung = parseInt($$data.JumlahBurung);
                if($$tmp.burung != burung){
                    if(burung > 0){
                        addNotification("Deteksi Burung", "Ada");
                    }
                    $$tmp.burung = burung;
                }

                let tikus = parseInt($$data.JumlahTikus);
                if($$tmp.tikus != tikus){
                    if(tikus > 0){
                        addNotification("Deteksi Tikus", "Ada");
                    }
                    $$tmp.tikus = tikus;
                }
                
                // if($$tmp.speaker != $$data.MenyalakanSpeaker){
                //     if(parseInt($$data.MenyalakanSpeaker) == 1){
                //         $$('#speakerOff').removeClass('button-active');
                //         $$('#speakerOn').addClass('button-active');
                //     } else {
                //         $$('#speakerOn').removeClass('button-active');
                //         $$('#speakerOff').addClass('button-active');
                //     }
                //     $$tmp.speaker = $$data.MenyalakanSpeaker;
                // }
                
            }
        );
        console.log("ptr done...");
        consoleToast("Updated.");
        app.ptr.done();
  }, 2000);
});