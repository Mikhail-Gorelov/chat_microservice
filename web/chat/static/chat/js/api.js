let requestedNewPageChat = false;
let requestedNewPageMessage = false;
$('.inbox_chat').scroll(function () {
  if (($(this).prop('scrollHeight') - $(this).height()) <= $(this).scrollTop()+5&& !requestedNewPage) {
    if ($(this).attr("data-href")) {
      console.log("Hello world!");
      requestedNewPageChat = true;
      getChatList();
    }
  }
});
$('.msg_history').scroll(function () {
  console.log($(this).prop('scrollHeight'), $(this).height(), $(this).scrollTop());
  if ($(this).scrollTop() === 0 && !requestedNewPage) {
    console.log("Hello world!", $(this).attr('id'), $(this).attr('href'), $(this).attr('data'));
    if($(this).attr('data')) {
      requestedNewPageMessage = true;
      getMessagesInChat($(this).attr('id'), $(this).attr('href'), $(this).attr('data'));
    }
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
        <div class="incoming_msg_img"><img src="${image}" alt="sunil" id="imageId"></div>
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
    url: $(".inbox_chat").attr("data-href"),
    type: "GET",
    success: function (data) {
      console.log(data);
      chatListRender(data);
    },
  })
}

function makeChatActive(e) {
  let block = $(this);
  $(".active_chat").removeClass("active_chat");
  block.addClass("active_chat");
  $('.msg_history').attr('id', block.attr('id'));
  $('.msg_history').empty();
  $('.msg_history').attr('href', block.attr('href'));
  getMessagesInChat(block.attr('id'), block.attr('href'));
  $('.msg_history').scrollTop($('.msg_history').prop('scrollHeight'));
}

function chatListRender(data) {
  let chatList = data.results;
  $(".inbox_chat").attr("data-href", data.next);
  $.each(chatList, function (i) {
    if (chatList[i].last_message == null) {
         chatList[i].last_message = "no messages";
    }
    if (chatList[i].last_message_date == null) {
      chatList[i].last_message_date = chatList[i].date;
    }
    let chat = `
    <div class="chat_list" id="${chatList[i].id}" href="${chatList[i].user_chats[1].image}">
            <div class="chat_people">
              <div class="chat_img"><img src="${chatList[i].file}" alt="sunil"></div>
              <div class="chat_ib">
                <h5>${chatList[i].name} <span class="chat_date">${chatList[i].last_message_date}</span></h5>
                <p>${chatList[i].last_message}</p>
              </div>
            </div>
          </div>
    `;
    $('.inbox_chat').append(chat);
  })
  $(".chat_list").click(makeChatActive)
  requestedNewPage = false;
}

function convertTZ(date, tzString) {
    return new Date((typeof date === "string" ? new Date(date) : date).toLocaleString("en-US", {timeZone: tzString}));
}

function getMessagesInChat(id, image, url=null) {
  let url_web = ""
  if (url==null) {
    url_web = "/message-list/" + id + "/";
  }
  else {
    url_web = url;
  }
  let currentUser = JSON.parse(localStorage.getItem('userData'));
  console.log($(document).height());
  console.log($('.msg_history').height());
  console.log($('.msg_history').scrollTop());
    $.ajax({
    url: url_web,
    type: "GET",
    success: function (data) {
      let message_list = data.results
      $.each(message_list, function (i) {
        let messageDate = new Date();
        convertTZ(messageDate, "Europe/Kiev");
        let messageDateStringToday = ("0" + messageDate.getDate()).slice(-2) + "-" + ("0"+(messageDate.getMonth()+1)).slice(-2) + "-" +
    messageDate.getFullYear();
        let messageDateStringYesterday = ("0" + (messageDate.getDate()-1)).slice(-2) + "-" + ("0"+(messageDate.getMonth()+1)).slice(-2) + "-" +
    messageDate.getFullYear();
        let intermediateDate = ``;
        if (messageDateStringToday === (message_list[i].date).split(" ")[0]) {
          if (!$('div').hasClass("scroll-date-today")) {
            console.log("Today!");
            let date = messageDateStringToday.split("-")[0] + "." + messageDateStringToday.split("-")[1]
            intermediateDate = `<div class="scroll-date-today" align="center"><p>Today ${date}</p></div>`;
          }
        }

        if ((message_list[i].date).split(" ")[0] !== messageDateStringToday && (message_list[i].date).split(" ")[0] !== messageDateStringYesterday) {
          let id = (message_list[i].date).split(" ")[0]
          if (!$('div').hasClass("scroll-date-${id}")) {
            // console.log($('div').hasClass("scroll-date-${id}"))
            console.log("Date!");
            intermediateDate = `<div class="scroll-date-${id}" align="center"><p>${(message_list[i].date).split(" ")[0]}</p></div>`;
          }
        }
        if (messageDateStringYesterday === (message_list[i].date).split(" ")[0]) {
          if (!$('div').hasClass("scroll-date-yesterday")) {
            console.log("Yesterday!");
            let date = messageDateStringYesterday.split("-")[0] + "." + messageDateStringYesterday.split("-")[1]
            intermediateDate = `<div class="scroll-date-yesterday" align="center"><p>Yesterday ${date}</p></div>`;
          }
        }
        console.log(intermediateDate);
        let message = '';
        $('.msg_history').prepend(intermediateDate);
        if (message_list[i].author_id === currentUser[0]) {
          message = outgoingMessage(message_list[i].content, message_list[i].date);
        } else {
          message = ingoingMessage(image, message_list[i].content, message_list[i].date);
        }
        $('.msg_history').prepend(message);

      })
      $('.msg_history').attr('data', data.next);
      $('.msg_history').scrollTop($('.msg_history').prop('scrollHeight'));
    },
})
}
