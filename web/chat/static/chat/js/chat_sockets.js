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
  if (data.command == "new_message") {
    $('#chat-log').append(data.username + ": " + data.message + '\n');
    let currentUser = JSON.parse(localStorage.getItem('userData'));
    let message_list = data
    if (message_list.author_id == currentUser.id) {
      let message = `
        <div class="outgoing_msg">
        <div class="sent_msg">
            <p>${message_list.content}</p>
            <span class="time_date"> ${message_list.date}</span> </div>
        </div>
        `;
      $('.msg_history').append(message);
    } else {
      let message = `
        <div class="incoming_msg">
        <div class="incoming_msg_img"><img src="${image}" alt="sunil" id="imageId"></div>
        <div class="received_msg">
          <div class="received_withd_msg">
            <p>${message_list.content}</p>
            <span class="time_date"> ${message_list.date}</span></div>
        </div>
        </div>
        `;
      $('.msg_history').append(message);
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


