$(document).ready(function(){

var received = $('#received');

var socket;

//open websocket
openSocket();

function openSocket(){
    // Ensures only one connection is open at a time
    if(socket !== undefined && socket.readyState !== socket.CLOSED){
        console.log("WebSocket is already opened.");
        received.append("socket connected");
        received.append($('<br/>'));
        return;
    }

    // Create a new instance of the websocket
    socket = new WebSocket("ws://" + window.location.hostname + ":8080/ws");

    /**
    * Binds functions to the listeners for the websocket.
    */ 
    socket.onopen = function(){  
      console.log("connected"); 
    }; 

    socket.onerror = function (error) {
      console.log('error: ' + error);
    };

    socket.onmessage = function (message) {
      console.log("receiving: " + message.data);
      received.append("RECV: " + message.data);
      received.append($('<br/>'));
      received.scrollTop(received[0].scrollHeight);
    };

    socket.onclose = function(){
      console.log("disconnected"); 
    };
}

var sendMessage = function(message) {
  console.log("sending:" + message.data);
  socket.send(message.data);
};


// jQuery no-double-tap-zoom plugin

// Triple-licensed: Public Domain, MIT and WTFPL license - share and enjoy!

(function($) {
  var IS_IOS = /iphone|ipad/i.test(navigator.userAgent);
  $.fn.nodoubletapzoom = function() {
    if (IS_IOS)
      $(this).bind('touchstart', function preventZoom(e) {
        var t2 = e.timeStamp
          , t1 = $(this).data('lastTouch') || t2
          , dt = t2 - t1
          , fingers = e.originalEvent.touches.length;
        $(this).data('lastTouch', t2);
        if (!dt || dt > 500 || fingers > 1) return; // not double-tap

        e.preventDefault(); // double tap - prevent the zoom
        // also synthesize click events we just swallowed up
        $(this).trigger('click').trigger('click');
      });
  };
})(jQuery);

// GUI Stuff

$('#bleft,#bright,#bforward,#bback').nodoubletapzoom();

$(document).keypress(function(e) {

        //function to receive control from keyboard keys
        KeyCheck();
        function KeyCheck()
			{
				var KeyID = e.keyCode;
				var serCMD;
				
				switch(KeyID)
				{
                    //case 16:
                    //socket.send("b;");
                    //break; 
                    //case 17:
                    //socket.send("b;");
                    //break;
                    case 37:
                    serCMD = "l;";      //left key - l(left) on serial
                    break;
                    case 38:
                    serCMD = "a;";      //up key - a(accelerate) on serial
                    break;
                    case 39:
                    serCMD = "r;";      //right key - r(right) on serial
                    break;
                    case 40:
                    serCMD = "b;";      //down key - b(back) on serial
                    break;
				}
				
				socket.send(serCMD);
				console.log("sending:" + serCMD);
				received.append("SEND: " + serCMD);
                received.append($('<br/>'));
			}
});


$('#bleft').click(function() {
    serCMD = "l;";
    socket.send(serCMD);
	console.log("sending:" + serCMD);
	received.append("SEND: " + serCMD);
    received.append($('<br/>'));    
});

$('#bright').click(function() {
    serCMD = "r;";
    socket.send(serCMD);
	console.log("sending:" + serCMD);
	received.append("SEND: " + serCMD);
    received.append($('<br/>'));    
});

$('#bforward').click(function() {
    serCMD = "a;";
    socket.send(serCMD);
	console.log("sending:" + serCMD);
	received.append("SEND: " + serCMD);
    received.append($('<br/>'));    
});

$('#bback').click(function() {
    serCMD = "b;";
    socket.send(serCMD);
	console.log("sending:" + serCMD);
	received.append("SEND: " + serCMD);
    received.append($('<br/>'));    
});

$("#webcam_container").mouseover(function() {
    //var $this = $(this);
    $(".keycontrol_overlay").removeClass("hidden").addClass("visible");
});

$("#webcam_container").mouseout(function() {
    var $this = $(this);
    $(".keycontrol_overlay").removeClass("visible").addClass("hidden");

});

$("#keycontrol_overlay").addClass("hidden");

// send a command to the serial port
$("#cmd_send").click(function(ev){
  ev.preventDefault();
  var cmd = $('#cmd_value').val();
  sendMessage({ 'data' : cmd});
  $('#cmd_value').val("");
});

$('.console_output').addClass("hidden");

$('.console_output').click(function() {
    var $this = $(this);

    if ($this.hasClass("hidden")) {
        $(this).removeClass("hidden").addClass("visible");

    } else {
        $(this).removeClass("visible").addClass("hidden");
    }
});        

$('#clear').click(function(){
  received.empty();
});
$('#reconnect').click(function(){
  openSocket();
});

});


