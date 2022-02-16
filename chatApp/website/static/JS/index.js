let submitMessage = document.getElementById("submitMessage");
let form = document.getElementById("listItem");
let input = document.getElementById("noteMSG");
let edit = document.getElementById("edDel");
let listElement = document.createElement("li");
listElement.setAttribute("id", "msgEdit");
let onlineData, editedID, username, thisUser;

const sio = io();

function scrollTobottom(){
  var objDiv = document.getElementById("messageArea");
  objDiv.scrollTop = objDiv.scrollHeight;
}

function scrollBotPage(){
  var scrollingheight = (document.body.scrollHeight);
  console.log(scrollingheight);
  return scrollingheight; 
}

//Gets the currentUser that is logged in
function getCurrentUser(){
  sio.emit("getUser");
}

function editNote(noteId,noteData){
  var nData = document.getElementById("modalEdit");
  nData.value = noteData;
  editedID = noteId;
}

function deleteNote(noteId) {
  sio.emit("delete_event", {id: noteId});
}

function addUser(){
  let uIn = document.getElementById("usersADD").value;
  let len = document.getElementById("broadcast_data").placeholder;
  console.log(len);

  if(uIn && len){
    document.getElementById("broadcast_data").placeholder += ", " + uIn;
  }
  else if(uIn){
    document.getElementById("broadcast_data").placeholder = "Message: ";
    document.getElementById("broadcast_data").placeholder += uIn;
  }
  clearTextArea("usersADD");
}

function clearTextArea(broadcast){
  let messageData = document.getElementById(broadcast).value;
  console.log(messageData);
  messageData = "";
  document.getElementById(broadcast).value = messageData;
}

function showPass(){
  var x = document.getElementById("password");

  if (x.type === "password") {
    x.type = "text";
  } else {
    x.type = "password";
  }
}

function showPass2(){
  var x = document.getElementById("password1");
  var y = document.getElementById("password2");
  if (x.type === "password") {
    x.type = "text";
  } else {
    x.type = "password";
  }
  if(y.type === "password"){
    y.type = "text";
  }
  else{
    y.type = "password";
  }
}

//-------------------------------------------------------
//Functions for changing bubble color for online/offline
//-------------------------------------------------------

function userOnlineBubble(){
  data = "<span class=\"position-absolute top-0 start-100 translate-middle p-1 bg-success rounded-circle\" id = \"bubble\">"
  data += "<span class=\"visually-hidden\">Online</span>"
  data += "</span>\";"
  $("#myBubble").val = data;
}

function userOfflineBubble(){
  data = "<span class=\"position-absolute top-0 start-100 translate-middle p-1 bg-danger rounded-circle\" id = \"bubble\">"
  data += "<span class=\"visually-hidden\">Online</span>"
  data += "</span>\";"
  $("#myBubble").val = data;
}


//-----------------------------------------
//SocketIO Messages received by the server
//-----------------------------------------

//reads the current user to this function
sio.on('c_user',function(msg) {
  username = msg.data;
});
// disconnect automatically sends from the server when the user disconnects
sio.on("disconnect", () => {
  console.log("disconnected");
})

// Connect automatically sends from the server when the user disconnects
sio.on('connect',function() {
  console.log("connected!");
})

//reloads the page

sio.on('load_page',function(){
  location.reload();
})

//message receiving message add from socketio server emit message_add
sio.on('message_add',function(msg) {
  edit = "<div id = \"edDel\">";
  edit += "<div type = \"button\" class = \"btn\" data-bs-toggle=\"modal\" data-bs-target=\"#editModalCenter\" id =\"editB\">";
  edit += "<img src=\"./static/images/edit.png\" id=\"editImage\" onclick = \"editNote("+msg.id+","+msg.data+")\">";
  edit += "</div>";
  edit += "<button type=\"button\" class=\"btn-close\" id =\"closeX\" aria-label=\"Close\" onclick=\"deleteNote({{"+msg.id+"}})\">";
  edit += "</button>";
  edit += "</div>";

  if(msg.id == username){
    $('#log').append("<li class='list-group-item' id = 'chatStuff'>You: "+ msg.data + edit +"</li>");
  }
  else{
    listElement = msg.user_name +" : " +  msg.data;
    $('#log').append(listElement);
  }
  scrollTobottom();
  return(msg);
})

/*
sio.on("saved_messages",function(myResults)
{
  $('#log').val()
  for(res in myResults){
    console.log(res.data);
  }
})

function message_clear(){
  logs = document.getElementById('#log');
  $('#log').empty();
  sio.emit("load_all_messages");
}*/

//-----------------------------------------
//Submit functions for Forms used
//-----------------------------------------

$('form#broadcast').submit(function() {
  broadText = $('#broadcast_data').val();
  console.log(broadText);
  if(broadText.length > 0){
    sio.emit('my_broadcast_event', {data: broadText});
    clearTextArea("broadcast_data");
    sio.emit('load_all_messages');
  }
  return false;
});

$('form#editForm').submit(function(){
  editedData = $("#modalEdit").val();
  $("#editModalCenter").modal("hide");
  console.log(editedID,editedData);
  sio.emit('edit_event', {id:editedID, data: editedData});
  return false;
});


window.onbeforeunload = function () {
  window.scrollTo(0, scrollBotPage());
}

//Functions to use when the page loads
$(document).ready(function() {
  //getCurrentUser function used here to get the current user
  getCurrentUser();
 // displays all of the messages to the submitted messages area
  sio.emit("load_all_messages");
  scrollTobottom();
  //scrollBotPage();
});

//-----------------------------------------
//Commented Code to Possibly Add back later
//-----------------------------------------

  //Below is commented out and will only be used for making sure code works. Final version will not have this
  /*
  // Interval function that tests message latency by sending a "ping" message. The server then responds with a "pong" message and the round trip time is measured.
  var ping_pong_times = [];
  var start_time;
  window.setInterval(function() {
      start_time = (new Date).getTime();
      $('#transport').text(sio.io.engine.transport.name);
      sio.emit('my_ping');
  }, 1000);

  // Handler for the "pong" message. When the pong is received, the time from the ping is stored, and the average of the last 30 samples is average and displayed.
  sio.on('my_pong',function() {
      var latency = (new Date).getTime() - start_time;
      ping_pong_times.push(latency);
      ping_pong_times = ping_pong_times.slice(-30); // keep last 30 samples
      var sum = 0;
      for (var i = 0; i < ping_pong_times.length; i++)
          sum += ping_pong_times[i];
      $('#ping-pong').text(Math.round(10 * sum / ping_pong_times.length) / 10);
  });
  
*/
  // Handlers for the different forms in the page. These accept data from the user and send it to the server in a variety of ways


// using enter with messages as well as clicking submit
/*
input.addEventListener("keyup", function(event) {
    var input = document.getElementById("noteMSG").value;
    console.log(input);
    if (event.key === "Enter" && input){
        event.preventDefault();
        submit.click();
    }
    */
//});