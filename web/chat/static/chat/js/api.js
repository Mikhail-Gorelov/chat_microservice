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
  let chatList = data.results
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
  $.ajax({
    url: url_web,
    type: "GET",
    success: function (data) {
      let message_list = data.results
      $.each(message_list, function (i) {
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
      // got current date, need to compare with messages and add date in list of messages
      let currentDate = new Date();
      convertTZ(currentDate, "Europe/Kiev");

      if (data.next !=null) {
        return getMessagesInChat(id, image, data.next);
      }
      if (data.next == null) {
        $('.msg_history').scrollTop($('.msg_history').prop('scrollHeight'));
      }
    },
})
}
