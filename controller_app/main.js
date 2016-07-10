$(document).ready(function(){

var received = $('#received');


var socket = new WebSocket("ws://" + window.location.hostname + ":8080/ws");
 
socket.onopen = function(){  
  console.log("connected"); 
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

var sendMessage = function(message) {
  console.log("sending:" + message.data);
  socket.send(message.data);
};

// GUI Stuff

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

$('#clear').click(function(){
  received.empty();
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



});


