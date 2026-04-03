let submitMessage = document.getElementById("submitMessage");
let form = document.getElementById("listItem");
let input = document.getElementById("noteMSG");
let edit = document.getElementById("edDel");
let listElement = document.createElement("li");
listElement.setAttribute("id", "msgEdit");
let onlineData, editedID, username, thisUser, messID, numUsers;
let currentDMUser = null;
let currentDMUserId = null;
let newMessagesCount = 0;
let userScrolledUp = false;
let dmMessagesCache = {};
let totalUnreadDMs = 0;
let dmModalOpen = false;

const sio = io();

function scrollTobottom() {
  var objDiv = document.getElementById("messageArea");
  if (objDiv) {
    objDiv.scrollTop = objDiv.scrollHeight;
  }
  hideNewMessagesIndicator();
}

function scrollToBottom() {
  scrollTobottom();
}

function scrollBotPage() {
  var sHeight = document.getElementById("chatPage");
  console.log(sHeight.scrollHeight);
}

function showNewMessagesIndicator() {
  var indicator = document.getElementById("newMessagesIndicator");
  if (indicator && userScrolledUp) {
    indicator.style.display = "flex";
    indicator.innerHTML = `<i class="fas fa-arrow-down me-2"></i>${newMessagesCount} new message${newMessagesCount > 1 ? 's' : ''}`;
  }
}

function hideNewMessagesIndicator() {
  var indicator = document.getElementById("newMessagesIndicator");
  if (indicator) {
    indicator.style.display = "none";
  }
  newMessagesCount = 0;
  userScrolledUp = false;
}

function formatTime(date) {
  const d = new Date(date);
  const month = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  let hours = d.getHours();
  const minutes = String(d.getMinutes()).padStart(2, '0');
  const ampm = hours >= 12 ? 'PM' : 'AM';
  hours = hours % 12;
  hours = hours ? hours : 12;
  return `${month}/${day} ${hours}:${minutes} ${ampm}`;
}

function timeAgo(date) {
  const now = new Date();
  const d = new Date(date);
  const seconds = Math.floor((now - d) / 1000);
  
  if (seconds < 60) return 'just now';
  if (seconds < 3600) {
    const mins = Math.floor(seconds / 60);
    return mins + (mins === 1 ? ' min ago' : ' mins ago');
  }
  if (seconds < 86400) {
    const hours = Math.floor(seconds / 3600);
    return hours + (hours === 1 ? ' hr ago' : ' hrs ago');
  }
  if (seconds < 604800) {
    const days = Math.floor(seconds / 86400);
    return days + (days === 1 ? ' day ago' : ' days ago');
  }
  return formatTime(date);
}

function getCurrentUser() {
  sio.emit("getUser");
}

function updateUserList(userSignedUp) {
  var htmlUser = `
    <li id="user${userSignedUp.id}" class="user-item">
      <div class="user-card">
        <div class="user-avatar-sm">
          <i class="fas fa-user"></i>
          <span class="online-indicator">
            <span class="online-dot online"></span>
          </span>
        </div>
        <span class="user-name">${userSignedUp.user_name}</span>
        <span class="user-status">
          <span class="badge bg-success status-badge">Online</span>
        </span>
        <div class="user-actions">
          <button class="user-action-btn" onclick="startDM('${userSignedUp.user_name}', ${userSignedUp.id})" title="Send Message">
            <i class="fas fa-comment-dots"></i>
          </button>
        </div>
      </div>
    </li>`;
  $('#uList').append(htmlUser);
}

function addUser() {
  let uIn = document.getElementById("usersADD").value;
  let len = document.getElementById("broadcast_data").placeholder;
  console.log(len);

  if (uIn && len) {
    document.getElementById("broadcast_data").placeholder += ", " + uIn;
  }
  else if (uIn) {
    document.getElementById("broadcast_data").placeholder = "Message: ";
    document.getElementById("broadcast_data").placeholder += uIn;
  }
  clearTextArea("usersADD");
}

function upsdateUserNumber() {
  numUsers += 1;
}

// DM Functions
function openDModal(userName, userId) {
  currentDMUser = userName;
  currentDMUserId = userId;
  dmModalOpen = true;
  
  document.getElementById("dmModalTitle").textContent = userName;
  document.getElementById("dmMessages").innerHTML = '<div class="text-center text-muted"><i class="fas fa-spinner fa-spin"></i> Loading...</div>';
  
  var modal = new bootstrap.Modal(document.getElementById('dmModal'));
  modal.show();
  
  sio.emit("mark_dm_read", { userId: userId });
  sio.emit("get_dm_history", { userId: userId, userName: userName });
  
  setTimeout(() => {
    document.getElementById("dmMessageInput").focus();
    scrollDMToBottom();
  }, 100);
}

function closeDModal() {
  currentDMUser = null;
  currentDMUserId = null;
  dmModalOpen = false;
  sio.emit("get_total_unread_dms");
  var messagesDiv = document.getElementById("dmMessages");
  if (messagesDiv) {
    messagesDiv.innerHTML = '';
  }
}

function scrollDMToBottom() {
  var container = document.getElementById("dmMessagesContainer");
  if (container) {
    container.scrollTop = container.scrollHeight;
  }
}

function sendDMFromModal() {
  var dmText = document.getElementById("dmMessageInput").value.trim();
  var fileInput = document.getElementById("dmFileInput");
  
  console.log("sendDMFromModal called");
  console.log("Text:", dmText);
  console.log("Has file:", fileInput && fileInput.files.length > 0);
  console.log("currentDMUser:", currentDMUser);
  console.log("currentDMUserId:", currentDMUserId);
  
  if (fileInput && fileInput.files.length > 0) {
    console.log("Calling sendDMWithFile");
    sendDMWithFile();
  } else if (dmText.length > 0 && currentDMUser && currentDMUserId) {
    console.log("Sending text message");
    sio.emit("dm_event", {
      data: dmText,
      toUser: currentDMUser,
      toUserId: currentDMUserId
    });
    document.getElementById("dmMessageInput").value = "";
  } else if (currentDMUser && currentDMUserId) {
    console.log("Sending empty message");
    sio.emit("dm_event", {
      data: "",
      toUser: currentDMUser,
      toUserId: currentDMUserId
    });
  } else {
    console.log("No recipient selected");
  }
}

function sendDMWithFile() {
  var dmText = document.getElementById("dmMessageInput").value.trim();
  var fileInput = document.getElementById("dmFileInput");
  
  console.log("sendDMWithFile called");
  console.log("currentDMUser:", currentDMUser);
  console.log("currentDMUserId:", currentDMUserId);
  
  if (!fileInput || fileInput.files.length === 0) {
    console.log("No file selected");
    return;
  }
  
  if (!currentDMUser || !currentDMUserId) {
    console.log("No recipient selected");
    return;
  }
  
  var file = fileInput.files[0];
  console.log("Uploading file:", file.name);
  
  var formData = new FormData();
  formData.append("dm_file", file);
  formData.append("to_user", currentDMUser);
  formData.append("to_user_id", currentDMUserId);
  formData.append("message_text", dmText);
  
  fetch("/upload-dm-file", {
    method: "POST",
    body: formData
  })
  .then(response => {
    console.log("Response status:", response.status);
    if (!response.ok) {
      throw new Error("HTTP error! status: " + response.status);
    }
    return response.json();
  })
  .then(data => {
    console.log("Response data:", data);
    if (data.success) {
      if (data.dm_data) {
        var listValue = createDMMessageHTML(data.dm_data);
        $('#dmMessages').append(listValue);
        scrollDMToBottom();
      }
      document.getElementById("dmMessageInput").value = "";
      fileInput.value = "";
      updateFilePreview(null);
    } else if (data.error) {
      console.error("Upload error:", data.error);
      alert("Error: " + data.error);
    }
  })
  .catch(error => {
    console.error("Error uploading file:", error);
    alert("Upload failed: " + error.message);
  });
}

function updateFilePreview(file) {
  var preview = document.getElementById("dmFilePreview");
  var previewContainer = document.getElementById("dmFilePreviewContainer");
  
  if (!preview || !previewContainer) return;
  
  if (file) {
    previewContainer.style.display = "flex";
    
    if (file.type.startsWith("image/")) {
      var reader = new FileReader();
      reader.onload = function(e) {
        preview.innerHTML = `<img src="${e.target.result}" alt="Preview" style="max-width: 100px; max-height: 100px; border-radius: 8px;">`;
      };
      reader.readAsDataURL(file);
    } else {
      preview.innerHTML = `<i class="fas fa-file"></i> ${file.name}`;
    }
  } else {
    previewContainer.style.display = "none";
    preview.innerHTML = "";
  }
}

function removeDMFile() {
  var fileInput = document.getElementById("dmFileInput");
  if (fileInput) {
    fileInput.value = "";
  }
  updateFilePreview(null);
}

function detectLinks(text) {
  var urlRegex = /(https?:\/\/[^\s]+)/g;
  return text.replace(urlRegex, '<a href="$1" target="_blank" class="dm-link">$1</a>');
}

function clearTextArea(broadcast) {
  let messageData = document.getElementById(broadcast).value;
  messageData = "";
  document.getElementById(broadcast).value = messageData;
}

function showPass() {
  var x = document.getElementById("password");
  if (x.type === "password") {
    x.type = "text";
  } else {
    x.type = "password";
  }
}

function showPass2() {
  var x = document.getElementById("password1");
  var y = document.getElementById("password2");
  if (x.type === "password") {
    x.type = "text";
    y.type = "text";
  } else {
    x.type = "password";
    y.type = "password";
  }
}

function editNote(noteId) {
  sio.emit("note_id", { id: noteId });
  messID = noteId;
  var nData = document.getElementById("edit" + noteId).innerText;
  document.getElementById("modalEdit").value = nData;
}

function deleteNote(noteId) {
  sio.emit("delete_event", { id: noteId });
}

function removeElement(id) {
  var element = document.getElementById(id);
  if (element) {
    element.parentElement.removeChild(element);
  }
}

// Socket IO Events
sio.on('c_user', function(msg) {
  thisUser = msg.user_name;
});

sio.on('new_user', function(newUserData) {
  updateUserList(newUserData);
});

sio.on("disconnect", () => {
  console.log("disconnected");
});

sio.on('connect', function() {
  console.log("connected!");
});

sio.on('up_user', function(online) {
  var indicator = document.getElementById("onlineIndicator" + online.id);
  var badge = document.getElementById("statusBadge" + online.id);
  
  if (indicator != null) {
    var dot = indicator.querySelector('.online-dot');
    if (dot) {
      dot.className = online.status ? 'online-dot online' : 'online-dot offline';
    }
  }
  
  if (badge != null) {
    badge.className = online.status ? 'badge bg-success status-badge' : 'badge bg-secondary status-badge';
    badge.textContent = online.status ? 'Online' : 'Offline';
  }
});

sio.on('edit_message', function(messId) {
  var messageText = document.getElementById("edit" + messId.noteID);
  if (messageText) {
    messageText.innerText = messId.data;
  }
  
  var messageItem = document.getElementById("chat" + messId.noteID);
  if (messageItem && messId.edited) {
    var editedIndicator = messageItem.querySelector('.message-edited');
    if (!editedIndicator) {
      var timeElement = messageItem.querySelector('.message-time');
      if (timeElement) {
        timeElement.insertAdjacentHTML('afterend', `<span class="message-edited">(edited ${timeAgo(messId.edited_date)})</span>`);
      }
    }
  }
});

sio.on('delete_message', function(messId) {
  removeElement('chat' + messId.id);
});

sio.on('load_page', function() {
  location.reload();
});

sio.on('message_add', function(msg) {
  var listValue = createMessage(msg);
  $('#log').append(listValue);
  
  var messageArea = document.getElementById("messageArea");
  if (messageArea) {
    var isAtBottom = messageArea.scrollHeight - messageArea.scrollTop <= messageArea.clientHeight + 100;
    if (isAtBottom || !userScrolledUp) {
      scrollTobottom();
    } else {
      newMessagesCount++;
      showNewMessagesIndicator();
    }
  }
  return false;
});

// Total Unread DMs Handler
sio.on('total_unread_dms', function(data) {
  totalUnreadDMs = data.count || 0;
  updateDMNotificationBadge();
});

// DM Message Handler - show in modal if conversation is open
sio.on('dm_message', function(msg) {
  console.log("DM received:", msg);
  
  if (msg.sender_id == current_user_id || msg.recipient_id == current_user_id) {
    var otherUserId = msg.sender_id == current_user_id ? msg.recipient_id : msg.sender_id;
    var isFromOtherUser = msg.sender_id != current_user_id;
    
    if (currentDMUserId == otherUserId && dmModalOpen) {
      var listValue = createDMMessageHTML(msg);
      $('#dmMessages').append(listValue);
      scrollDMToBottom();
    } else if (isFromOtherUser) {
      totalUnreadDMs++;
      updateDMNotificationBadge();
      showDMToastNotification(msg.sender_name);
    }
    
    sio.emit("get_dm_conversations");
  }
});

function updateDMNotificationBadge() {
  var badge = document.getElementById("dmNavBadge");
  if (badge) {
    if (totalUnreadDMs > 0) {
      badge.textContent = totalUnreadDMs > 99 ? "99+" : totalUnreadDMs;
      badge.style.display = "block";
      badge.classList.add("active");
    } else {
      badge.style.display = "none";
      badge.classList.remove("active");
    }
  }
}

function showDMToastNotification(senderName) {
  var toast = document.getElementById("dmToast");
  var toastBody = document.getElementById("dmToastBody");
  
  if (toast && toastBody) {
    toastBody.textContent = "New message from " + senderName;
    var bsToast = new bootstrap.Toast(toast);
    bsToast.show();
  }
}

function clearUnreadForConversation(userId) {
  if (currentDMUserId == userId) {
    totalUnreadDMs = 0;
    updateDMNotificationBadge();
  }
}

// DM Deleted Handler
sio.on('dm_deleted', function(data) {
  var msgElement = document.getElementById("dmm" + data.id);
  if (msgElement) {
    var contentElement = msgElement.querySelector('.dm-content');
    var metaElement = msgElement.querySelector('.dm-meta');
    var actionsElement = msgElement.querySelector('.dm-actions');
    
    if (contentElement) {
      contentElement.outerHTML = '<span class="dm-content dm-content-deleted">This message was deleted</span>';
    }
    
    if (actionsElement) {
      actionsElement.remove();
    }
    
    if (metaElement) {
      var timeElement = metaElement.querySelector('.dm-time');
      if (timeElement) {
        var deletedDate = data.deleted_date ? formatTime(data.deleted_date) : '';
        timeElement.insertAdjacentHTML('beforeend', `<span class="dm-deleted">(deleted ${deletedDate})</span>`);
      }
    }
  }
});

// DM Edited Handler
sio.on('dm_edited', function(data) {
  var msgElement = document.getElementById("dmm" + data.id);
  if (msgElement) {
    var contentElement = msgElement.querySelector('.dm-content');
    var timeElement = msgElement.querySelector('.dm-time');
    
    if (contentElement) {
      contentElement.textContent = data.data;
    }
    
    if (timeElement && data.edited) {
      var existingEdited = timeElement.querySelector('.dm-edited');
      if (!existingEdited) {
        var editedDate = data.edited_date ? formatTime(data.edited_date) : '';
        timeElement.insertAdjacentHTML('beforeend', `<span class="dm-edited">(edited ${editedDate})</span>`);
      }
    }
  }
});

// Load DM history for modal
sio.on('dm_history', function(data) {
  console.log("Loading DM history:", data);
  var container = document.getElementById('dmMessages');
  container.innerHTML = '';
  
  if (data.messages && data.messages.length > 0) {
    data.messages.forEach(function(msg) {
      var listValue = createDMMessageHTML(msg);
      $(container).append(listValue);
    });
    scrollDMToBottom();
  } else {
    container.innerHTML = '<div class="text-center text-muted"><i class="fas fa-comment-dots me-2"></i>No messages yet. Start the conversation!</div>';
  }
});

// Handle DM conversations list
sio.on('dm_conversations', function(data) {
  console.log("DM conversations:", data);
  updateDMConversationsList(data.conversations);
});

sio.on('dm_read_receipt', function(data) {
  sio.emit("get_dm_conversations");
  sio.emit("get_total_unread_dms");
});

function updateDMConversationsList(conversations) {
  var container = document.getElementById('dmConversationsList');
  if (!container) return;
  
  if (!conversations || conversations.length === 0) {
    container.innerHTML = '<div class="dm-conversation-empty">No direct messages yet</div>';
    return;
  }
  
  var html = '';
  conversations.forEach(function(conv) {
    var unreadBadge = conv.unread_count > 0 ? `<span class="dm-unread-badge">${conv.unread_count}</span>` : '';
    var preview = conv.last_message.length > 25 ? conv.last_message.substring(0, 25) + '...' : conv.last_message;
    
    html += `
      <div class="dm-conversation-item" onclick="openDModal('${conv.user_name}', ${conv.user_id})">
        <div class="dm-conv-avatar">
          <i class="fas fa-user"></i>
        </div>
        <div class="dm-conv-info">
          <div class="dm-conv-header">
            <span class="dm-conv-name">${conv.user_name}</span>
            <span class="dm-conv-time">${timeAgo(conv.last_date)}</span>
          </div>
          <div class="dm-conv-preview">
            <span class="dm-conv-message">${escapeHtml(preview)}</span>
            ${unreadBadge}
          </div>
        </div>
      </div>
    `;
  });
  
  container.innerHTML = html;
}

function createDMMessageHTML(msg) {
  var messageTime = formatTime(msg.date);
  var isOwn = msg.sender_id == current_user_id;
  
  var editedIndicator = '';
  if (msg.edited && msg.edited_date) {
    editedIndicator = `<span class="dm-edited">(edited ${formatTime(msg.edited_date)})</span>`;
  }
  
  var deletedIndicator = '';
  if (msg.is_deleted && msg.deleted_date) {
    deletedIndicator = `<span class="dm-deleted">(deleted ${formatTime(msg.deleted_date)})</span>`;
  }
  
  var messageContent;
  if (msg.is_deleted) {
    messageContent = '<span class="dm-content dm-content-deleted">This message was deleted</span>';
  } else {
    var textWithLinks = msg.data ? detectLinks(escapeHtml(msg.data)) : '';
    messageContent = textWithLinks ? `<span class="dm-content">${textWithLinks}</span>` : '';
  }
  
  var fileContent = '';
  if (msg.file_url && !msg.is_deleted) {
    if (msg.file_type === 'image') {
      fileContent = `<div class="dm-attachment dm-image"><img src="${msg.file_url}" alt="${msg.file_name || 'Image'}" onclick="openImageModal('${msg.file_url}')"></div>`;
    } else {
      fileContent = `<div class="dm-attachment dm-file">
        <a href="${msg.file_url}" target="_blank" class="dm-file-link">
          <i class="fas fa-file"></i>
          <span>${msg.file_name || 'File'}</span>
        </a>
        <a href="${msg.file_url}" download="${msg.file_name || 'download'}" class="dm-download-btn" title="Download">
          <i class="fas fa-download"></i>
        </a>
      </div>`;
    }
  }
  
  var actions = '';
  if (isOwn && !msg.is_deleted) {
    actions = `<div class="dm-actions">
      <button class="dm-btn dm-btn-edit" onclick="openEditDModal(${msg.id})" title="Edit">
        <i class="fas fa-pen-to-square"></i>
      </button>
      <button class="dm-btn dm-btn-delete" onclick="deleteDM(${msg.id})" title="Delete">
        <i class="fas fa-trash-can"></i>
      </button>
    </div>`;
  }
  
  if (isOwn) {
    return `<div class="dm-message dm-own" id="dmm${msg.id}">
      <div class="dm-bubble">
        <div class="dm-meta">
          <span class="dm-time">${messageTime}${editedIndicator}${deletedIndicator}</span>
          ${actions}
        </div>
        ${messageContent}
        ${fileContent}
      </div>
    </div>`;
  } else {
    return `<div class="dm-message dm-other" id="dmm${msg.id}">
      <div class="dm-bubble dm-bubble-other">
        <div class="dm-meta">
          <span class="dm-time">${messageTime}${editedIndicator}${deletedIndicator}</span>
        </div>
        ${messageContent}
        ${fileContent}
      </div>
    </div>`;
  }
}

function openImageModal(imageUrl) {
  document.getElementById("imageModalImg").src = imageUrl;
  var modal = new bootstrap.Modal(document.getElementById("imageModal"));
  modal.show();
}

function deleteDM(dmId) {
  sio.emit("delete_dm_event", { id: dmId });
}

function openEditDModal(dmId) {
  var msgElement = document.getElementById("dmm" + dmId);
  if (!msgElement) return;
  
  var contentElement = msgElement.querySelector('.dm-content');
  if (!contentElement) return;
  
  var currentText = contentElement.textContent;
  document.getElementById("editDModalInput").value = currentText;
  document.getElementById("editDModalId").value = dmId;
  
  var modal = new bootstrap.Modal(document.getElementById('editDModal'));
  modal.show();
}

function saveEditDM() {
  var dmId = document.getElementById("editDModalId").value;
  var newText = document.getElementById("editDModalInput").value.trim();
  
  if (newText && dmId) {
    sio.emit("edit_dm_event", { id: parseInt(dmId), data: newText });
    bootstrap.Modal.getInstance(document.getElementById('editDModal')).hide();
  }
}

function escapeHtml(text) {
  var div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

function createMessage(msg) {
  var dmPrefix = msg.is_dm ? '<span class="dm-badge"><i class="fas fa-lock"></i></span> ' : '';
  var messageTime = msg.date ? formatTime(msg.date) : formatTime(new Date());
  var editedIndicator = msg.edited ? `<span class="message-edited">(edited ${timeAgo(msg.edited_date)})</span>` : '';
  var editDelete = `<div class="message-actions">
    <button type="button" class="msg-btn msg-btn-edit" data-bs-toggle="modal" data-bs-target="#editModalCenter" onclick="editNote('${msg.noteID}')" title="Edit">
      <i class="fas fa-pen-to-square"></i>
    </button>
    <button type="button" class="msg-btn msg-btn-delete" onclick="deleteNote('${msg.noteID}')" title="Delete">
      <i class="fas fa-trash-can"></i>
    </button>
  </div>`;

  if (msg.user_name === thisUser) {
    return `<li class="message-item message-own" id="chat${msg.noteID}">
      <div class="message-bubble">
        <div class="message-meta">
          <span class="message-sender">You</span>
          <span class="message-time">${messageTime}${editedIndicator}</span>
        </div>
        <div class="message-content-row">
          <span class="message-text" id="edit${msg.noteID}">${dmPrefix}${msg.data}</span>
          ${editDelete}
        </div>
      </div>
    </li>`;
  }
  else {
    return `<li class="message-item" id="chat${msg.noteID}">
      <div class="message-bubble message-other">
        <div class="message-meta">
          <span class="message-sender">${msg.user_name}</span>
          <span class="message-time">${messageTime}${editedIndicator}</span>
        </div>
        <span class="message-text" id="edit${msg.noteID}">${dmPrefix}${msg.data}</span>
      </div>
    </li>`;
  }
}

function createDMMessage(msg) {
  var messageTime = formatTime(msg.date);
  var isOwn = msg.sender_id == current_user_id;
  var recipientName = isOwn ? msg.recipient_name : msg.sender_name;
  
  var editDelete = `<div class="message-actions">
    <button type="button" class="msg-btn msg-btn-delete" onclick="deleteNote('dm_${msg.id}')" title="Delete">
      <i class="fas fa-trash-can"></i>
    </button>
  </div>`;

  if (isOwn) {
    return `<li class="message-item message-own message-dm" id="chatdm${msg.id}">
      <div class="dm-indicator-left">
        <i class="fas fa-lock"></i> DM to ${recipientName}
      </div>
      <div class="message-bubble">
        <div class="message-meta">
          <span class="message-sender">You</span>
          <span class="message-time">${messageTime}</span>
        </div>
        <div class="message-content-wrapper">
          <span class="message-text">${msg.data}</span>
        </div>
        ${editDelete}
      </div>
    </li>`;
  }
  else {
    return `<li class="message-item message-dm" id="chatdm${msg.id}">
      <div class="dm-indicator-left">
        <i class="fas fa-lock"></i> DM from ${msg.sender_name}
      </div>
      <div class="message-bubble message-other">
        <div class="message-meta">
          <span class="message-sender">${msg.sender_name}</span>
          <span class="message-time">${messageTime}</span>
        </div>
        <div class="message-content-wrapper">
          <span class="message-text">${msg.data}</span>
        </div>
      </div>
    </li>`;
  }
}

// Form Submissions - only handle button clicks, not Enter key (handled separately)
$('form#broadcast').submit(function(e) {
  var broadText = $('#broadcast_data').val();
  if (broadText.length > 0) {
    sio.emit('my_broadcast_event', { data: broadText });
    clearTextArea("broadcast_data");
  }
  return false;
});

$('#dmForm').submit(function(e) {
  console.log("DM Form submitted via submit!");
  e.preventDefault();
  sendDMFromModal();
  return false;
});

$('#dmSendBtn').click(function(e) {
  console.log("DM Send button clicked!");
  e.preventDefault();
  sendDMFromModal();
});

$('#dmMessageInput').on('keydown', function(e) {
  if (e.key === 'Enter') {
    if (e.shiftKey) {
      return;
    } else {
      e.preventDefault();
      sendDMFromModal();
    }
  }
});

// Key handling for broadcast input
$('#broadcast_data').on('keydown', function(e) {
  if (e.key === 'Enter') {
    if (e.shiftKey) {
      // Shift+Enter: allow default behavior (new line)
      return;
    } else {
      // Enter without Shift: send message
      e.preventDefault();
      var broadText = $(this).val();
      if (broadText.trim().length > 0) {
        sio.emit('my_broadcast_event', { data: broadText });
        clearTextArea("broadcast_data");
      }
    }
  }
});

// Key handling for DM input
$('#dmMessageInput').on('keydown', function(e) {
  if (e.key === 'Enter') {
    if (e.shiftKey) {
      // Shift+Enter: allow default behavior (new line)
      return;
    } else {
      // Enter without Shift: send message
      e.preventDefault();
      sendDMFromModal();
    }
  }
});

$('form#editForm').submit(function() {
  var editedData = $("#modalEdit").val();
  var editedID = messID;
  sio.emit('edit_event', { id: editedID, data: editedData });
  $("#editModalCenter").modal("hide");
  return false;
});



// Page Load
$(document).ready(function() {
  getCurrentUser();
  sio.emit("load_all_messages");
  sio.emit("get_dm_conversations");
  sio.emit("get_total_unread_dms");
  scrollTobottom();
  
  // Scroll detection for new messages indicator
  var messageArea = document.getElementById("messageArea");
  if (messageArea) {
    messageArea.addEventListener("scroll", function() {
      var isAtBottom = messageArea.scrollHeight - messageArea.scrollTop <= messageArea.clientHeight + 100;
      if (isAtBottom) {
        hideNewMessagesIndicator();
      } else {
        userScrolledUp = true;
      }
    });
  }
});

// Image upload - form submits on file selection
console.log("Image upload JS loaded");
