$(function () {
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

function messageFile(data) {
  console.log(data);
  let file_message = `
        <div class="outgoing_msg">
        <div class="sent_msg">
            <p>
            <audio controls>
            <source src="${data.data.file}"" type="audio/mpeg">
            <source src="${data.data.file}"" type="audio/ogg">
            </p>
            <span class="time_date"></span> </div>
        </div>
        `;
  $('.chat-history').append(file_message);
  $('.chat-history').scrollTop($('.chat-history').prop('scrollHeight'));
}

function messageInChat(e) {
  const data = JSON.parse(e.data);
  let image = $('.active_chat').attr('href');
  if (data.type === "user.connect") {
    $("#usernameList").append(data.data.username + " ");
  }
  if (data.type === "file.message") {
    messageFile(data);
  }
  if (data.command === "add_chat") {
    console.log("added chat");
    console.log(data);
    console.log(data.chat_id)
    let chat = `
    <div class="chat_list" id="${data.chat_id}">
                  <li class="clearfix">
                    <img src="" alt="avtr" width="10" height="40">
                    <div class="about">
                        <div class="name">Title</div>
                        <div class="status"> Last Message Date </div>
                        <div class="status"> Last Message
                        <div class="status">
                        <div class="icon-badge-container">
                          <i class="far fa-envelope icon-badge-icon"></i>
                          <div class="icon-badge" data="0">0</div>
                        </div>
                         <i class="fa fa-circle online"></i> online </div>
                    </div>
                  </li>
                </div>
    `;
    let ulStart = `<ul class="list-unstyled chat-list mt-2 mb-0">`;
    let ulEnd = `</ul>`;
    ulStart += chat
    ulStart += ulEnd
    // TODO: добавляю в существующий ul
    $('.people-list').append(ulStart);
    $(".people-list").click(makeChatActive);
  }
  if (data.data.command === "new_message") {
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
  if (data.data.command === "check_message") {
    let temp = Number($(`#${data.chat_id}`).find(".icon-badge").attr('data'));
    if (temp === 0) {
      $(`#${data.chat_id}`).find(".icon-badge").attr('data', 0);
      $(`#${data.chat_id}`).find(".icon-badge").text("");
      $(`#${data.chat_id}`).find(".icon-badge").text($(`#${data.chat_id}`).find(".icon-badge").attr('data'));
    } else {
      $(`#${data.chat_id}`).find(".icon-badge").attr('data', temp - 1);
      $(`#${data.chat_id}`).find(".icon-badge").text("");
      $(`#${data.chat_id}`).find(".icon-badge").text($(`#${data.chat_id}`).find(".icon-badge").attr('data'));
    }
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
