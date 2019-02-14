var audio;
var playlist;
var tracks;
var current;
var title;
var activeEpisode;
var currentTime;
title = document.title;
if (!localStorage.getItem('activeEpisode'+title)) {
    localStorage.setItem('activeEpisode'+title, "1");
    localStorage.setItem('currentTime'+title, 0.0);
}
activeEpisode = localStorage.getItem('activeEpisode'+title);
currentTime = localStorage.getItem('currentTime'+title);
if (document.readyState !== 'loading' ) {
  eventHandler();
} else {
  document.addEventListener( 'DOMContentLoaded', eventHandler);  
}  
function eventHandler(){

init();
function init(){
    SetGridColumn();
    audio = document.getElementById('audio');
    playlist = document.getElementById('playlist');
    tracks = playlist.querySelectorAll('a');
    for (var link of tracks) {
        link.addEventListener('click', function(e){ 
        e.preventDefault();
        var link = this;
        current.classList.remove('active');
        current = link.parentNode;
        current.classList.add('active');
        currentTime = 0.0;
        localStorage.setItem('currentTime'+title, 0.0);
        run(link, audio);
        });
	    if (activeEpisode == link.innerHTML) {
            current = link.parentNode;
            current.classList.add('active');
	        audio.firstElementChild.setAttribute("src", link.href);     
            audio.load();
            audio.volume = .10;
        }	
    }
    audio.addEventListener('ended',function(e){
        current.classList.remove('active');
        current= current.nextElementSibling;
        if(current == null){
            current = playlist.firstElementChild;
        }
        current.classList.add('active');
        link = current.firstElementChild;
        currentTime = 0.0;
        localStorage.setItem('currentTime'+title, 0.0);
        run(link,audio);
    });
    audio.addEventListener('play',function(e){
        if (currentTime > audio.currentTime) {
            audio.currentTime = currentTime;
        }
    });
    audio.addEventListener('pause',function(e){
        localStorage.setItem('currentTime'+title, audio.currentTime);
    });
    document.title = title + ' - ' + activeEpisode;
    audio.play();
    audio.currentTime = currentTime;
}
function run(link, player){
        player.src = link.href;
        localStorage.setItem('activeEpisode'+title, link.innerHTML);
        activeEpisode = link.innerHTML;
        document.title = title + ' - ' + activeEpisode;
        audio.load();
        audio.play();
        audio.currentTime = currentTime;
}
function FillPlaylist() {
    var i;
    for (i=1; i<=radiodrama.episodes; i++) { 	
       var div_ = document.createElement("DIV");
       var a_ = document.createElement("A");
       var drama = radiodrama.program_infix;
       var pad = radiodrama.digit;
       var base = (drama.indexOf("/") == -1) ? "media" : "mp3";
       if (pad == 4) {
           var episode = "abcdefghijklmnopqrstuvwxyz".charAt(i-1);	    
       } else {
           var episode = i.toString();
           if (pad > 0) {
	          episode = episode.padStart(pad, '0');
           }
       }       
       a_.setAttribute("href", "http://rthk9.rthk.hk/radiodrama/" + base + "/"+ drama + episode + ".mp3");
       var i_ = document.createTextNode(i.toString());
       a_.appendChild(i_);
       div_.appendChild(a_);
       if (i.toString() == activeEpisode) {
      div_.setAttribute("class","active");     
      current = div_;
	  audio.firstElementChild.setAttribute("src", a_.attributes[0].value);     
	  audio.load();     
       }	       
       playlist.appendChild(div_);
    }	    
}
function SetGridColumn() {
    var colNum = 10;
    var n = podcast.episodes;	
    switch (n) {
       case 1: case 2: case 3: case 4: case 5: case 6: case 7: case 8: case 9:
          colNum = n;
          break;
       case 11: case 12:
          colNum = 6;
          break;
       case 13: case 14:
       case 21:
          colNUm = 7;
          break;
       case 15: case 16:
       case 22: case 23: case 24:
       case 31: case 32:
          colNum = 8;
          break;
       case 17: case 18:
       case 25: case 26: case 27:
       case 33: case 34: case 35: case 36:
       case 41: case 42: case 43: case 44: case 45:
       case 51: case 52: case 53: case 54:
       case 61: case 62: case 63:
       case 71: case 72:
       case 81: 
          colNum = 9;
          break;
    }
    document.documentElement.style.setProperty("--colNum", colNum);
}
}	
