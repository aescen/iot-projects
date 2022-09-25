function LoadAlarm(){
  this.audioAlarm = new Audio('./static/sounds/alarm-buzzer-short.mp3');
  this.play = function() {
    this.audioAlarm.setAttribute('src', './static/sounds/alarm-buzzer-short.mp3');
    this.audioAlarm.autoplay = true;
    this.audioAlarm.loop = true;
    this.audioAlarm.play;
    console.log("Playing");
  }
  this.stop = function(){
    this.audioAlarm.setAttribute('src', './static/sounds/alarm-buzzer-short.mp3');
    this.audioAlarm.autoplay = false;
    this.audioAlarm.loop = false;
    this.audioAlarm.pause;
    this.audioAlarm.currentTime = 0;
    console.log("Stopped");
  }

  this.sound =  new Howl({
    src: ['./static/sounds/alarm-buzzer-short.mp3'],
    loop: true,
    volume: 1,
    preload: true,
  });
};