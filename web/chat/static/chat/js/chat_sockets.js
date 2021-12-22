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
  let image = $('.active_chat').attr('href');
  if (data.type == "user.connect") {
    $("#usernameList").append(data.data.username + " ");
  }
  if (data.command == "add_chat") {
    console.log("added chat");
    console.log(data);
    console.log(data.chat_id)
    let chat = `
    <div class="chat_list" id="${data.chat_id}">
            <div class="chat_people">
              <div class="chat_img"><img src="" alt="sunil"></div>
              <div class="chat_ib">
              </div>
            </div>
          </div>
    `;
    $('.inbox_chat').append(chat);
    $(".chat_list").click(makeChatActive);
  }
  if (data.command == "new_message") {
    $('#chat-log').append(data.username + ": " + data.message + '\n');
    let currentUser = JSON.parse(localStorage.getItem('userData'));
    let message_list = data
    if (message_list.author_id === currentUser[0]) {
      outgoingMessage(message_list.content, message_list.date);
    } else {
      ingoingMessage(image, message_list.content, message_list.date);
    }
    $('.msg_history').scrollTop($('.msg_history').prop('scrollHeight'));
  }
}

function sendMessage() {
  let message = $('.write_msg').val();
  chat.send(JSON.stringify({
    'command': 'new_message',
    'message': message,
    'chat_id': $('.msg_history').attr('id'),
  }));
  $('.write_msg').val("");
}


