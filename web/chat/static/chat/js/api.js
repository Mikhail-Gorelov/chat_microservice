let requestedNewPage = false;
$('.inbox_chat').scroll(function () {
  if (($(this).prop('scrollHeight') - $(this).height()) <= $(this).scrollTop()+5&& !requestedNewPage) {
    if ($(this).attr("data-href")) {
      console.log("Hello world!");
      requestedNewPage = true;
      getChatList();
    }
  }
});
$(function () {
  getChatList();
});

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
  getMessagesInChat(block.attr('id'), block.attr('href'));
}

function chatListRender(data) {
  let chatList = data.results;
  console.log(data.next);
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
  // let cookie_value = $.cookie("jwt-auth");
  // console.log(cookie_value);
  console.log($(document).height());
  console.log($('.msg_history').height());
  console.log($('.msg_history').scrollTop());
  // if ($(this).height() - $('.msg_history').height() == $('.msg_history').scrollTop()) {
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
        $('.msg_history').append(intermediateDate);
        if (message_list[i].author_id == currentUser.id) {
          let message = `
            <div class="outgoing_msg">
            <div class="sent_msg">
                <p>${message_list[i].content}</p>
                <span class="time_date"> ${message_list[i].date}</span> </div>
            </div>
            `;
          $('.msg_history').append(message);
        } else {
          let message = `
            <div class="incoming_msg">
            <div class="incoming_msg_img"><img src="${image}" alt="sunil" id="imageId"></div>
            <div class="received_msg">
              <div class="received_withd_msg">
                <p>${message_list[i].content}</p>
                <span class="time_date"> ${message_list[i].date}</span></div>
            </div>
            </div>
            `;
          $('.msg_history').append(message);
        }

      })

      if (data.next !=null) {
        return getMessagesInChat(id, image, data.next);
      }
      if (data.next == null) {
        $('.msg_history').scrollTop($('.msg_history').prop('scrollHeight'));
      }
    },
})
// }
}
