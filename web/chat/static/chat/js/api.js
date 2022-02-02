$.fn.scrollBottom = function() {
  return $(document).height() - this.scrollTop() - this.height();
};
let requestedNewPageChat = false;
let requestedNewPageMessage = false;
$('.people-list').scroll(function () {
  if (($(this).prop('scrollHeight') - $(this).height()) <= $(this).scrollTop() + 5 && !requestedNewPage) {
    if ($(this).attr("data-href")) {
      requestedNewPageChat = true;
      getChatList();
    }
  }
});
$('.chat-history').scroll(function () {
  if ($(this).scrollTop() === 0 && !requestedNewPage) {
    if($(this).attr('data')) {
      requestedNewPageMessage = true;
      getMessagesInChat($(this).attr('id'), $(this).attr('href'), $(this).attr('data'));
    }
  }
  if (($(this).scrollTop() + $(this).scrollBottom()) <= 257) {
    //  chat_id, message_id -> consumer
    console.log('checked');
    hasReadMessage(chatId = $(this).attr('id'), messageId = 45);
  }
});
$(function () {
  getChatList();
});

function outgoingMessage(content, date) {
  let message = `
        <div class="outgoing_msg">
        <div class="sent_msg">
            <p>${content}</p>
            <span class="time_date"> ${date}</span> </div>
        </div>
        `;
  return message;
}

function ingoingMessage(image, content, date) {
  let message = `
        <div class="incoming_msg">
        <div class="incoming_msg_img"><img src="${image}" alt="sunil" id="imageId" width="40px" height="40px"></div>
        <div class="received_msg">
          <div class="received_withd_msg">
            <p>${content}</p>
            <span class="time_date"> ${date}</span></div>
        </div>
        </div>
        `;
  return message;
}

function getChatList() {
  $.ajax({
    url: $(".people-list").attr("data-href"),
    type: "GET",
    success: function (data) {
      chatListRender(data);
    },
  })
}

function makeChatActive(e) {
  let block = $(this);
  $(".active_chat").removeClass("active_chat");
  block.addClass("active_chat");
  $('.chat-history').attr('id', block.attr('id'));
  $('.chat-history').empty();
  $('.chat-history').attr('href', block.attr('href'));
  getMessagesInChat(block.attr('id'), block.attr('href'));
  $('.chat-history').scrollTop($('.chat-history').prop('scrollHeight'));
}

function chatListRender(data) {
  let chatList = data.results;
  $(".people-list").attr("data-href", data.next);
  let ulStart = `<ul class="list-unstyled chat-list mt-2 mb-0">`;
  let chats = ``;
  let ulEnd = `</ul>`;
  $.each(chatList, function (i) {
    if (chatList[i].last_message == null) {
      chatList[i].last_message = "no messages";
    }
    if (chatList[i].last_message_date == null) {
      chatList[i].last_message_date = chatList[i].date;
    }
    let chat = `
              <div class="chat_list" id="${chatList[i].id}" href="${chatList[i].user_chats[1].image}">
                <li class="clearfix">
                  <img src="${chatList[i].file}" alt="avatar" width="10" height="40">
                  <div class="about">
                      <div class="name">${chatList[i].name}</div>
                      <div class="status"> ${chatList[i].last_message_date} </div>
                      <div class="status"> ${chatList[i].last_message}
                      <div class="status">
                      <div class="icon-badge-container">
                        <i class="far fa-envelope icon-badge-icon"></i>
                        <div class="icon-badge"></div>
                      </div>
                       <i class="fa fa-circle online"></i> online </div>
                  </div>
                </li>
              </div>
    `;
    chats += chat
  })
  ulStart += chats
  ulStart += ulEnd
  $('.people-list').append(ulStart);
  $(".chat_list").click(makeChatActive)
  requestedNewPage = false;
}

function convertTZ(date, tzString) {
  return new Date((typeof date === "string" ? new Date(date) : date).toLocaleString("en-US", {timeZone: tzString}));
}

function getMessagesInChat(id, image, url = null) {
  let url_web = ""
  if (url == null) {
    url_web = "/message-list/" + id + "/";
  } else {
    url_web = url;
  }
  let currentUser = JSON.parse(localStorage.getItem('userData'));
  $.ajax({
    url: url_web,
    type: "GET",
    success: function (data) {
      let message_list = data.results
      $.each(message_list, function (i) {
        let messageDate = new Date();
        convertTZ(messageDate, "Europe/Kiev");
        let messageDateStringToday = ("0" + messageDate.getDate()).slice(-2) + "-" + ("0" + (messageDate.getMonth() + 1)).slice(-2) + "-" +
          messageDate.getFullYear();
        let messageDateStringYesterday = ("0" + (messageDate.getDate() - 1)).slice(-2) + "-" + ("0" + (messageDate.getMonth() + 1)).slice(-2) + "-" +
          messageDate.getFullYear();
        let intermediateDate = ``;
        if (messageDateStringToday === (message_list[i].date).split(" ")[0]) {
          if (!$('div').hasClass("scroll-date-today")) {
            let date = messageDateStringToday.split("-")[0] + "." + messageDateStringToday.split("-")[1]
            intermediateDate = `<div class="scroll-date-today" align="center"><p>Today ${date}</p></div>`;
          }
        }

        if ((message_list[i].date).split(" ")[0] !== messageDateStringToday && (message_list[i].date).split(" ")[0] !== messageDateStringYesterday) {
          let id = (message_list[i].date).split(" ")[0]
          if (!$('div').hasClass("scroll-date-${id}")) {
            intermediateDate = `<div class="scroll-date-${id}" align="center"><p>${(message_list[i].date).split(" ")[0]}</p></div>`;
          }
        }
        if (messageDateStringYesterday === (message_list[i].date).split(" ")[0]) {
          if (!$('div').hasClass("scroll-date-yesterday")) {
            let date = messageDateStringYesterday.split("-")[0] + "." + messageDateStringYesterday.split("-")[1]
            intermediateDate = `<div class="scroll-date-yesterday" align="center"><p>Yesterday ${date}</p></div>`;
          }
        }
        let message = `<ul class="m-b-0">`;
        $('.chat-history').prepend(intermediateDate);
        if (message_list[i].author_id === currentUser[0]) {
          message += outgoingMessage(message_list[i].content, message_list[i].date);
        } else {
          message += ingoingMessage(image, message_list[i].content, message_list[i].date);
        }
        message += `</ul>`;
        $('.chat-history').prepend(message);

      })
      $('.chat-history').attr('data', data.next);
      $('.chat-history').scrollTop($('.chat-history').prop('scrollHeight'));
    },
  })
}
