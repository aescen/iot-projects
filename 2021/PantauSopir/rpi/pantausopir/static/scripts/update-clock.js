function updateClock ( ){
    var currentTime = new Date ();

    var currentYear = currentTime.getFullYear();
    var currentMonth = currentTime.getMonth();
    var currentDate = currentTime.getDate();
    var currentHours = currentTime.getHours ( );
    var currentMinutes = currentTime.getMinutes ( );
    var currentSeconds = currentTime.getSeconds ( );

    const monthNames = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun",
                          "Jul", "Agu", "Sep", "Okt", "Nov", "Des"
                        ];

    // Pad the minutes and seconds with leading zeros, if required
    currentMinutes = ( currentMinutes < 10 ? "0" : "" ) + currentMinutes;
    currentSeconds = ( currentSeconds < 10 ? "0" : "" ) + currentSeconds;

    // Choose either "AM" or "PM" as appropriate
    //var timeOfDay = ( currentHours < 12 ) ? "AM" : "PM";

    // Convert the hours component to 12-hour format if needed
    //currentHours = ( currentHours > 12 ) ? currentHours - 12 : currentHours;

    // Convert an hours component of "0" to "12"
    //currentHours = ( currentHours == 0 ) ? 12 : currentHours;

    // Compose the string for display
    //var currentTimeString = currentHours + ":" + currentMinutes + ":" + currentSeconds + " " + timeOfDay;
    var currentTimeString =  currentDate + " " + monthNames[currentMonth] + " "+ currentYear + " " + currentHours + ":" + currentMinutes + ":" + currentSeconds;

    // Update the time display
    document.getElementById("clock").firstChild.nodeValue = currentTimeString;
}
setInterval('updateClock()', 1000 );