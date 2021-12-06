$(function () {
  $('#room-name-submit').click(enterRoom);
  $('#chat-message-submit').click(sendMessage);
  getLastMessages();

  console.log("Initialized chat");
});
let chat = null;

function enterRoom() {
  if (chat) {
    console.log("chat.close()")
    chat.close()
  }
  let roomName = $('#room-name-input').val();
  console.log(roomName);
  chat = new ReconnectingWebSocket(
    'ws://'
    + window.location.host
    + '/ws/chat/'
    + roomName
    + '/'
  );
  chat.onclose = closeChat;
  chat.onmessage = messageInChat;

}

function messageInChat(e) {
  const data = JSON.parse(e.data);
  if (data.type == "user.connect") {
    $("#usernameList").append(data.data.username + " ");
  }
  if (data.command == "new_message") {
    $('#chat-log').append(data.username + ": " + data.message + '\n');
  }
}

function closeChat(e) {
  console.error('Chat socket closed unexpectedly');
}

function sendMessage() {
  const message = $('#chat-message-input').val();
  console.log(message)
  chat.send(JSON.stringify({
    'command': 'new_message',
    'message': message,
    'username': 1,
  }));
  message.value = '';
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

function messageRender(data) {
  $.each(data, function (i) {
    let message = `${data[i].author_id} says: ${data[i].content} at ${data[i].date}\n`;
    $('#chat-log').append(message);
  })
}
