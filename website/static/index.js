var submit = document.getElementById("submitMessage").value;
var form = document.getElementById("listItem");
var input = document.getElementById("noteMSG");
var edit = document.getElementById("edDel");
var editedID;

var listElement = document.createElement("li");
listElement.setAttribute("id", "msgEdit");

console.log(edit);

var username,thisUser;
const sio = io();

function scrollTobottom(){
  var objDiv = document.getElementById("messageArea");
  objDiv.scrollTop = objDiv.scrollHeight;
}

function scrollBotPage(){
  window.scrollTo(0,document.querySelector(".scrollingContainer").scrollHeight);
}

//Gets the currentUser that is logged in
function getCurrentUser(){
  sio.emit("getUser");
}

$(document).ready(function() {

  // disconnect automatically sends from the server when the user disconnects
  sio.on("disconnect", () => {
    onlineData = 0;
    console.log("disconnected");
  });

  // Connect automatically sends from the server when the user disconnects
  sio.on('connect', function() {
    onlineData = 1;
    console.log("connected!")
  });
  
  //getCurrentUser function used here to get the current user
  getCurrentUser();
  scrollTobottom();

  //reads the current user to this function
  sio.on('c_user', function(msg) {
    username = msg.data;
  });

  //reloads the page
  sio.on('load_page',function(){
    location.reload();
  })

  // displays all of the messages to the submitted messages area
  sio.emit("load_all_messages");

  //message receiving message add from socketio server emit message_add
  sio.on('message_add', function(msg) {
      if(msg.id == username){
        $('#log').append("<li class='list-group-item' id = 'chatStuff'>You : "+ msg.data +"&nbsp;"+msg.edit +"</li>");
      }
      else{
        listElement = msg.user_name + " : " +  msg.data;
        $('#log').append(listElement);
      } 
      scrollTobottom()
    });

  // Interval function that tests message latency by sending a "ping" message. The server then responds with a "pong" message and the round trip time is measured.
  var ping_pong_times = [];
  var start_time;
  window.setInterval(function() {
      start_time = (new Date).getTime();
      $('#transport').text(sio.io.engine.transport.name);
      sio.emit('my_ping');
  }, 1000);

  // Handler for the "pong" message. When the pong is received, the time from the ping is stored, and the average of the last 30 samples is average and displayed.
  sio.on('my_pong', function() {
      var latency = (new Date).getTime() - start_time;
      ping_pong_times.push(latency);
      ping_pong_times = ping_pong_times.slice(-30); // keep last 30 samples
      var sum = 0;
      for (var i = 0; i < ping_pong_times.length; i++)
          sum += ping_pong_times[i];
      $('#ping-pong').text(Math.round(10 * sum / ping_pong_times.length) / 10);
  });

  // Handlers for the different forms in the page. These accept data from the user and send it to the server in a variety of ways

  $('form#broadcast').submit(function(event) {
    sio.emit('my_broadcast_event', {data: $('#broadcast_data').val()});
    clearTextArea("broadcast_data");
    window.location.href = "/";
    return false;
  });

  $('form#editForm').submit(function(event) {
    sio.emit('edit_event', {id:editedID, data: $("#modalEdit").val()});
    window.location.href = "/";
    return false;
  });

});

function addUser(){
  var uIn = document.getElementById("usersADD").value;
  var len = document.getElementById("broadcast_data").placeholder;
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
  var messageData = document.getElementById(broadcast).value;
  console.log(messageData);
  messageData = "";
  document.getElementById(broadcast).value = messageData;
}

function deleteNote(noteId) {
  sio.emit("delete_event", {id: noteId});
  /*
  fetch("/delete-note", {
    method: "POST",
    body: JSON.stringify({ noteId: noteId }),
  }).then((_res) => {
    window.location.href = "/";
  });
  */
}

function editNote(noteId,noteData){
  console.log('message ID: ', noteId);
  console.log('message data: ', noteData);
  var editText = document.getElementById("modalEdit");
  editText.value = noteData;
  editedID = noteId;
  /*
  fetch("/edit-note", {
    method: "POST",
    body: JSON.stringify({ noteId: noteId, note_data: n_data}),
  }).then((_res) => {
    window.location.href = "/";
  });*/
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

// using enter with messages as well as clicking submit
/*
input.addEventListener("keyup", function(event) {
    var input = document.getElementById("noteMSG").value;
    console.log(input);
    if (event.key === "Enter" && input){
        event.preventDefault();
        submit.click();
    }
}); */