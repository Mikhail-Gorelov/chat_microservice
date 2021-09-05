$(function () {
  $('#chat-message-submit').click(sendMessage);
  getLastMessages();
  getOnlineUsers();
});

const username = localStorage.getItem("username");

const chatSocket = new WebSocket(
  'ws://'
  + window.location.host
  + '/ws/chat/?username='
  + username
);

chatSocket.onmessage = function (e) {
  const data = JSON.parse(e.data);
  console.log(data);
  if (data.type == "user.connect") {
    $("#usernameList").append(data.data.username + " ");
  }
  if (data.type == "fetch.messages") {
    $('#chat-log').append(data.author + ' says:  ' + data.content + ' at ' + data.date + '\n');
  }
  if (data.command == "new_message") {
    $('#chat-log').append(data.username + ": " + data.message + '\n');
  }
};

chatSocket.onclose = function (e) {
  console.error('Chat socket closed unexpectedly');
};

$('#chat-message-input').focus();
$('#chat-message-input').onkeyup = function (e) {
  if (e.keyCode === 13) {  // enter, return
    $('#chat-message-submit').click();
  }
};

function sendMessage() {
  const messageInputDom = $('#chat-message-input')[0];
  const message = messageInputDom.value;
  chatSocket.send(JSON.stringify({
    'command': 'new_message',
    'message': message,
    'username': username,
  }));
  messageInputDom.value = '';
}

function getLastMessages() {
  $.ajax({
    url: 'last-messages/',
    type: "GET",
    success: function (data) {
      messageRender(data);
    },
  })
}
function getOnlineUsers() {
  $.ajax({
    url: 'author-status/',
    type: "GET",
    success: function (data) {
      userRender(data);
    },
  })
}
function messageRender(data) {
  $.each(data, function (i) {
    let message = `${data[i].author} says: ${data[i].content} at ${data[i].date}\n`;
    $('#chat-log').append(message);
  })
}
function userRender(data) {
  $.each(data, function (i) {
    // let user = `${data[i].id=id={{ user.id }}>{{ username }}: online`;
    // let user = `<p id=${data[i].id}> ${data[i].username}</p>`
    let user = `${data[i].username} `;
    $("#usernameList").append(user);
  })
}
