let submitMessage = document.getElementById("submitMessage");
let form = document.getElementById("listItem");
let input = document.getElementById("noteMSG");
let edit = document.getElementById("edDel");
let listElement = document.createElement("li");
listElement.setAttribute("id", "msgEdit");
let onlineData, editedID, username,thisUser,messID,numUsers;

const sio = io();

//---------------------------------------------------------------
//Functions that have to do with scrolling
//---------------------------------------------------------------

function scrollTobottom(){
  var objDiv = document.getElementById("messageArea");
  objDiv.scrollTop = objDiv.scrollHeight;
}

function scrollBotPage(){
  var sHeight = document.getElementById("chatPage");
  console.log(sHeight.scrollHeight);
}

//---------------------------------------------------------------
//Functions that have to do with the Users
//---------------------------------------------------------------

function getCurrentUser(){
  sio.emit("getUser");
}

function updateUserList(userSignedUp){
  var htmlUser = `
    <li id = \"user`+userSignedUp.id+`\">
      <div type=\"button\" class=\"btn btn-primary position-relative\" id = \"userLink\" data-bs-placement=\"left\">`+userSignedUp.user_name+`
        <div id = \"myBubble`+userSignedUp.id+`\">
            <span class=\"position-absolute top-0 start-100 translate-middle p-1 bg-success rounded-circle\" id = \"bubble\"></span>
        </div>
      </div>
    </li>`;

  $('#uList').append(htmlUser);
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

function upsdateUserNumber(){
  numUsers+=1;
}

//---------------------------------------------------------------
//Functions for Direct Messaging
//---------------------------------------------------------------




//---------------------------------------------------------------
//Functions for clearing the message area
//---------------------------------------------------------------

function clearTextArea(broadcast){
  let messageData = document.getElementById(broadcast).value;
  console.log(messageData);
  messageData = "";
  document.getElementById(broadcast).value = messageData;
}

//---------------------------------------------------------------
//Functions for showing passwords on the login and sign-up pages
//---------------------------------------------------------------

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

//---------------------------------------------------------------
//Functions for creating, editing and deleting messages
//---------------------------------------------------------------
function createMessage(msg){

  let edit = `<div id = \"edDel\">
    <div type = \"button\" class = \"btn\" data-bs-toggle=\"modal\" data-bs-target=\"#editModalCenter\" id =\"editB\" onclick =\"editNote('`+msg.noteID+"','"+msg.data+`')\">
    <img src=\"./static/images/edit.png\" id=\"editImage\">
    </div>
    <button type=\"button\" class=\"btn-close\" id =\"closeX\" aria-label=\"Close\" onclick=\"deleteNote('`+msg.noteID+`')\">
    </button>
  </div>`;

  if(msg.user_name == thisUser){
    var listValue = "<li class=\"list-group-item chatStuff\" id =\"chat"+msg.noteID+"\"><div> You : &nbsp; <span id=\"edit"+msg.noteID+"\">"+ msg.data +"&nbsp;"+edit+"</span></div></li>";
  }
  else{
    var listValue= "<li class=\"list-group-item chatStuff\" id =\"chat"+msg.noteID+"\"><div>"+msg.user_name +" : &nbsp; <span id=\"edit"+msg.noteID+"\">"+msg.data +"</span></div></li>";
  }
  return listValue;
}

function editNote(noteId){
  sio.emit("note_id",{id:noteId});
  messID = noteId;
  var nData = document.getElementById("edit"+noteId).innerText;
  document.getElementById("modalEdit").value = nData;  
}

function deleteNote(noteId) {
  sio.emit("delete_event", {id: noteId});
}

//Used from Stack Overflow
function removeElement(id) {
  var element = document.getElementById(id);
  element.parentElement.removeChild(element);
}

//-------------------------------------------------------
//Functions for changing bubble color for online/offline
//-------------------------------------------------------

/*
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
}*/

//-----------------------------------------
//SocketIO Messages received by the server
//-----------------------------------------

/*
Socket IO Functions for Users
-----------------------------------------------------
*/
sio.on('c_user',function(msg) {
  thisUser = msg.user_name;
});

sio.on('new_user',function(newUserData) {
   updateUserList(newUserData);
   return false
});

/*
Socket IO Functions for Connect and Disconnect
-----------------------------------------------------
*/

sio.on("disconnect", () => {
  console.log("disconnected");
})

sio.on('connect',function() {
  console.log("connected!");
})

sio.on('up_user',function(online) {
  var user = document.getElementById("myBubble"+online.id);
  if (user!= null){
    if(online.status == true)
    {
      user.innerHTML = "<span class=\"position-absolute top-0 start-100 translate-middle p-1 bg-success rounded-circle\" id = \"bubble\"></span>";
    }
    else{
      user.innerHTML = "<span class=\"position-absolute top-0 start-100 translate-middle p-1 bg-danger rounded-circle\" id = \"bubble\"></span>";
    }
  }
})

sio.on('edit_message',function(messId){
  var editDelete = `<div id = \"edDel\">
  <div type = \"button\" class = \"btn\" data-bs-toggle=\"modal\" data-bs-target=\"#editModalCenter\" id =\"editB\" onclick =\"editNote('`+messId.noteID+"','"+messId.data+`')\">
  <img src=\"./static/images/edit.png\" id=\"editImage\">
  </div>
  <button type=\"button\" class=\"btn-close\" id =\"closeX\" aria-label=\"Close\" onclick=\"deleteNote('`+messId.noteID+`')\">
  </button>
  </div>`;
  
  if (thisUser == messId.user_name){
    document.getElementById("edit"+messId.noteID).innerHTML = messId.data +"&nbsp"+editDelete;
  }
  else{
    document.getElementById("edit"+messId.noteID).innerText = messId.data;
  }
})

sio.on('delete_message',function(messId){
  //message = document.getElementById('chat'+messId).innerHTML;
  removeElement('chat'+messId.id);
})

//reloads the page
sio.on('load_page',function(){
  location.reload();
})

//message receiving message add from socketio server emit message_add
sio.on('message_add',function(msg) {
  listValue = createMessage(msg);
  console.log(listValue);
  $('#log').append(listValue);
  scrollTobottom();
  return false;
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
  var broadText = $('#broadcast_data').val();
  if(broadText.length > 0){
    sio.emit('my_broadcast_event', {data: broadText});
    clearTextArea("broadcast_data");
  }
  return false;
})


$('form#editForm').submit(function(){
  var editedData = $("#modalEdit").val();
  var editedID = messID;
  sio.emit('edit_event', {id:editedID, data: editedData});
  $("#editModalCenter").modal("hide");  
  return false;
})


//Functions to use when the page loads
$(document).ready(function() {
  //getCurrentUser function used here to get the current user
  getCurrentUser();
 // displays all of the messages to the submitted messages area
  sio.emit("load_all_messages");
  scrollTobottom();
  //scrollBotPage();
})

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