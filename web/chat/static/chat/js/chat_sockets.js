$(function () {
  $(".msg_send_btn").click(sendMessage);
});

chat = new ReconnectingWebSocket(
  'ws://'
  + window.location.host
  + '/ws/chat/'
);
chat.onclose = closeChat;
chat.onmessage = messageInChat;

function closeChat(e) {
  console.error('Chat socket closed unexpectedly');
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

function sendMessage() {
  const message = $('.write_msg').val();
  console.log(message);
  chat.send(JSON.stringify({
    'command': 'new_message',
    'message': message,
    'chat_id': $('.msg_history').attr('id'),
    'username': 1,
  }));
  message.value = '';
}


