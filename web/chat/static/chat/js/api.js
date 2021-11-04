$(function () {
  getChatList();
  getMessagesInChat();
});

function getChatList() {
  $.ajax({
    url: $(".inbox_chat").attr("data-href"),
    type: "GET",
    success: function (data) {
      chatListRender(data);
    },
  })
}

function makeChatActive(e) {
  let block = $(this);
  // "chat_list active_chat"
  $(".active_chat").removeClass("active_chat");
  block.addClass("active_chat");
  console.log("Hello world!");
}

function chatListRender(data) {
  // console.log(data);
  let chatList = data.results
  // TODO: сделать кастомные аватарки
  // TODO: сделать норм дату
  $.each(chatList, function (i) {
    let chat = `
    <div class="chat_list" id="${chatList[i].id}">
            <div class="chat_people">
              <div class="chat_img"><img src="{{ file }}" alt="sunil"></div>
              <div class="chat_ib">
                <h5>${chatList[i].name} <span class="chat_date">${chatList[i].date}</span></h5>
                <p>${chatList[i].description}</p>
              </div>
            </div>
          </div>
    `;
    $('.inbox_chat').append(chat);
  })
  $(".chat_list").click(makeChatActive)
}

function getMessagesInChat() {
  let chat_id = $("#chatId").data("id");
  console.log(chat_id);
  let url_web = "/message-list/" + chat_id + "/";
  $.ajax({
    url: url_web,
    type: "GET",
    success: function (data) {
      messagesRender(data);
    },
})
}

function messagesRender(data) {
  console.log(data);
}
