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
  if (data.data.content_type === "audio/mpeg") {
      let file_message = `
            <div class="outgoing_msg">
            <div class="sent_msg">
                <p>
                <audio controls>
                <source src="${data.data.file}"" type="${data.data.content_type}">
                </p>
                <span class="time_date"></span> </div>
            </div>
            `;
      $('.chat-history').append(file_message);
      $('.chat-history').scrollTop($('.chat-history').prop('scrollHeight'));
    } else if (data.data.content_type === "application/pdf") {
      let file_message = `
              <div class="outgoing_msg">
              <div class="sent_msg">
                  <p>
                  <object data="${data.data.file}" width="500" height="400" type="${data.data.content_type}">
                  </p>
                  <span class="time_date"></span> </div>
              </div>
              `;
        $('.chat-history').append(file_message);
        $('.chat-history').scrollTop($('.chat-history').prop('scrollHeight'));
  } else  {
      let file_message = `
              <div class="outgoing_msg">
              <div class="sent_msg">
                  <p>
                  <img src="${data.data.file}" width="500" height="400" alt="image">
                  </p>
                  <span class="time_date"></span> </div>
              </div>
              `;
        $('.chat-history').append(file_message);
        $('.chat-history').scrollTop($('.chat-history').prop('scrollHeight'));
  }

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
    console.log(data.chat_id)
    $('.people-list').append(
      $("#chat-ul").append(
      chatListFunc(
        data.chat_id, "", "", "hello", "Today", "lalal", 0,
        "mike",
        "", "offline"))
    );
    $(".chat_list").click(makeChatActive);
  }
  if (data.data.data.command === "new_message") {
    // console.log("Hello!", data);
    $(`#${data.data.chat_id}`).find(".icon-badge").attr('data', data.data.count_unread);
    $(`#${data.data.chat_id}`).find(".icon-badge").text("");
    $(`#${data.data.chat_id}`).find(".icon-badge").text($(`#${data.data.chat_id}`).find(".icon-badge").attr('data'));
    $('#chat-log').append(data.username + ": " + data.message + '\n');
    let currentUser = JSON.parse(localStorage.getItem('userData'));
    let message_list = data.data.data
    let message = '';
    if (message_list.author_id === currentUser[0]) {
      message = outgoingMessage(message_list.content, message_list.date, null);
    } else {
      message = ingoingMessage(image, message_list.content, message_list.date, null);
    }
    $('.chat-history').append(message);
    $('.chat-history').scrollTop($('.chat-history').prop('scrollHeight'));
  }
  if (data.data.data.command === "check_message") {
    let temp = Number($(`#${data.data.chat_id}`).find(".icon-badge").attr('data'));
    if (temp === 0) {
      $(`#${data.data.chat_id}`).find(".icon-badge").attr('data', 0);
      $(`#${data.data.chat_id}`).find(".icon-badge").text("");
      $(`#${data.data.chat_id}`).find(".icon-badge").text($(`#${data.data.chat_id}`).find(".icon-badge").attr('data'));
    } else {
      $(`#${data.data.chat_id}`).find(".icon-badge").attr('data', temp - 1);
      $(`#${data.data.chat_id}`).find(".icon-badge").text("");
      $(`#${data.data.chat_id}`).find(".icon-badge").text($(`#${data.data.chat_id}`).find(".icon-badge").attr('data'));
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
