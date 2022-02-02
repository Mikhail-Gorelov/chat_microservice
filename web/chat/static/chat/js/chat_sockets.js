$(function () {
  // TODO: типо стандартная инициализация, нужно иначе вероятно её делать
  $(".msg_send_btn").click(sendMessage);
});

const ws_scheme = window.location.protocol === "https:" ? "wss://" : "ws://";

chat = new ReconnectingWebSocket(
  ws_scheme
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
            <li class="clearfix">
                  <img src="" alt="avatar" width="10" height="40">
                  <div class="about">
                      <div class="name"></div>
                      <div class="status"></div>
                      <div class="status"></div>
                  </div>
                </li>
          </div>
    `;
    $('.people-list').append(chat);
    $(".people-list").click(makeChatActive);
  }
  if (data.command == "new_message") {
    $(`#${data.chat_id}`).find(".icon-badge").attr('data', data.count_unread);
    $(`#${data.chat_id}`).find(".icon-badge").text("");
    $(`#${data.chat_id}`).find(".icon-badge").text($(`#${data.chat_id}`).find(".icon-badge").attr('data'));
    $('#chat-log').append(data.username + ": " + data.message + '\n');
    let currentUser = JSON.parse(localStorage.getItem('userData'));
    let message_list = data
    let message = '';
    if (message_list.author_id === currentUser[0]) {
      message = outgoingMessage(message_list.content, message_list.date);
    } else {
      message = ingoingMessage(image, message_list.content, message_list.date);
    }
    $('.chat-history').append(message);
    $('.chat-history').scrollTop($('.chat-history').prop('scrollHeight'));
  }
  if (data.type == "check_message") {
    // TODO: проблема в том, что у каждого чата есть id, т.е нам надо коннектится к другому диву
    let temp = Number($('.icon-badge').attr('data'));
    console.log($('.icon-badge').attr('data'))
    $('.icon-badge').attr('data', temp + 1);
    $('.icon-badge').text("");
    $('.icon-badge').text($('.icon-badge').attr('data'));
  }
}

function sendMessage() {
  let message = $('.write_msg').val();
  chat.send(JSON.stringify({
    'command': 'new_message',
    'message': message,
    'chat_id': $('.chat-history').attr('id'),
  }));
  $('.write_msg').val("");
}

function hasReadMessage(chatId, messageId) {
  chat.send(JSON.stringify({
    'command': 'check_message',
    'chat_id': chatId,
    'message_id': messageId,
  }));
}
