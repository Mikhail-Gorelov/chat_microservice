$(function () {
  getChatList();
});
$.fn.scrollBottom = function () {
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
    if ($(this).attr('data')) {
      requestedNewPageMessage = true;
      getMessagesInChat($(this).attr('id'), $(this).attr('href'), $(this).attr('data'));
    }
  }
  if (($(this).scrollTop() + $(this).scrollBottom()) <= 257) {
    //  chat_id, message_id -> consumer
    console.log('checked');
    hasReadMessage(chatId = $(this).attr('id'), messageId = 89);
  }
});

function outgoingMessage(content, date, message_file) {
  if (message_file === null) {
    let message = `
        <div class="outgoing_msg">
        <div class="sent_msg">
            <p>${content}</p>
            <span class="time_date"> ${date}</span> </div>
        </div>
        `;
    return message;
  } else {
    console.log(message_file);
    if (message_file.content_type === "audio/mpeg") {
      let file_message = `
            <div class="outgoing_msg">
            <div class="sent_msg">
                <p>
                <audio controls style="width: 250px;">
                <source src="${message_file.file}" type="${message_file.content_type}">
                </p>
                <span class="time_date"></span> </div>
            </div>
            `;
      return file_message;
    } else if (message_file.content_type === "application/pdf") {
      let file_message = `
              <div class="outgoing_msg">
              <div class="sent_msg">
                  <p>
                  <object data="${message_file.file}" width="250" height="200" type="${message_file.content_type}">
                  </p>
                  <span class="time_date"></span> </div>
              </div>
              `;
      return file_message;
    } else {
      let file_message = `
              <div class="outgoing_msg">
              <div class="sent_msg">
                  <p>
                  <img src="${message_file.file}" width="250" height="200" alt="image">
                  </p>
                  <span class="time_date"></span> </div>
              </div>
              `;
      return file_message;
    }
  }
}

function ingoingMessage(image, content, date, message_file) {
  if (message_file === null) {
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
  } else {
    if (message_file.content_type === "audio/mpeg") {
      let file_message = `
            <div class="incoming_msg">
            <div class="incoming_msg_img"><img src="${image}" alt="sunil" id="imageId" width="40px" height="40px"></div>
            <div class="received_msg">
                  <div class="received_withd_msg">
                  <p>
                  <audio controls style="width: 250px;">
                  <source src="${message_file.file}" type="${message_file.content_type}">
                  </p>
                  <span class="time_date"></span> </div>
            </div>
            `;
      return file_message;
    } else if (message_file.content_type === "application/pdf") {
      let file_message = `
            <div class="incoming_msg">
            <div class="incoming_msg_img"><img src="${image}" alt="sunil" id="imageId" width="40px" height="40px"></div>
            <div class="received_msg">
                  <div class="received_withd_msg">
                  <p>
                  <object data="${message_file.file}" width="250" height="200" type="${message_file.content_type}">
                  </p>
                  <span class="time_date"></span> </div>
            </div>
            </div>
              `;
      return file_message;
    } else {
      let file_message = `
          <div class="incoming_msg">
          <div class="incoming_msg_img"><img src="${image}" alt="sunil" id="imageId" width="40px" height="40px"></div>
          <div class="received_msg">
              <div class="received_withd_msg">
                <p>
                <img src="${message_file.file}" width="250" height="200" alt="image">
                </p>
                <span class="time_date"></span> </div>
          </div>
          </div>
              `;
      return file_message;
    }
  }
}

function chatListFunc(id, imageHref, imageSrc, title, lastMessageDate, lastMessage, countUnread, interlocutorsName,
                      profile, interlocutorOnline) {
  if (interlocutorOnline.status === "online") {
    let chat = `
                <div class="chat_list" id="${id}" href="${imageHref}" data="${interlocutorsName}" data-href="${profile}" data-status="${interlocutorOnline.status}" data-last-seen="${interlocutorOnline.last_seen}">
                  <li class="clearfix">
                    <img src="${imageSrc}" alt="avtr" width="10" height="40">
                    <div class="about">
                        <div class="name">${title}</div>
                        <div class="status"> ${lastMessageDate} </div>
                        <div class="status"> ${lastMessage}
                        <div class="status">
                        <div class="icon-badge-container">
                          <i class="far fa-envelope icon-badge-icon"></i>
                          <div class="icon-badge" data="${countUnread}">${countUnread}</div>
                        </div>
                         <i class="fa fa-circle online"></i> online </div>
                    </div>
                  </li>
                </div>
      `;
    return chat;
  } else {
    let chat = `
                <div class="chat_list" id="${id}" href="${imageHref}" data="${interlocutorsName}" data-href="${profile}" data-status="${interlocutorOnline.status}" data-last-seen="${interlocutorOnline.last_seen}">
                  <li class="clearfix">
                    <img src="${imageSrc}" alt="avtr" width="10" height="40">
                    <div class="about">
                        <div class="name">${title}</div>
                        <div class="status"> ${lastMessageDate} </div>
                        <div class="status"> ${lastMessage}
                        <div class="status">
                        <div class="icon-badge-container">
                          <i class="far fa-envelope icon-badge-icon"></i>
                          <div class="icon-badge" data="${countUnread}">${countUnread}</div>
                        </div>
                         <i class="fa fa-circle offline"></i> offline </div>
                    </div>
                  </li>
                </div>
      `;
    return chat;
  }
}

function uploadImage() {
  let fd = new FormData();
  let button = $(this);
  let files = button[0].files;

  // Check file selected or not
  if (files.length > 0) {
    fd.append('image', files[0]);
  }

  $.ajax({
    url: button.data("href"),
    type: "POST",
    contentType: false,
    processData: false,
    data: fd,
    success: function (data) {
      console.log(data);
      $('#userAvatar').attr("src", data.image);
    },
    error: function (data) {
      console.log("error");
    },
  })
}

function chatAbout(image, name, profile, status, lastSeen) {
  let buttons = `
  <div class="col-lg-6 hidden-sm text-right">
    <a href="javascript:void(0);" class="btn btn-outline-secondary"><i class="fa fa-camera"></i></a>
    <i class="fa fa-image"><input id="uploadFile" class="btn btn-outline-primary" type="file"></i>
    <a href="javascript:void(0);" class="btn btn-outline-info"><i class="fa fa-cogs"></i></a>
    <a href="javascript:void(0);" class="btn btn-outline-warning"><i class="fa fa-question"></i></a>
  </div>
  `;
  let wrapperTop = `
   <div class="row">
  `;
  let wrapperBottom = `
  </div>
  `;
  if (status === "undefined" && lastSeen === "undefined") {
    let header = `
          <div class="col-lg-6">
              <a href="${profile}" target="_blank">
                  <img src="${image}" alt="avtr">
              </a>
              <div class="chat-about">
                  <h6 class="m-b-0">${name}</h6>
                  <i class="fa fa-circle offline"></i>
                  <small>Last seen: never</small>
              </div>
          </div>
  `;
    return wrapperTop + header + buttons + wrapperBottom
  }
  if (status === "online") {
    let header = `
          <div class="col-lg-6">
              <a href="${profile}" target="_blank">
                  <img src="${image}" alt="avtr">
              </a>
              <div class="chat-about">
                  <h6 class="m-b-0">${name}</h6>
                  <i class="fa fa-circle online"></i> Online
              </div>
          </div>
  `;
    return wrapperTop + header + buttons + wrapperBottom
  }
  if (status === "offline") {
    let header = `
          <div class="col-lg-6">
              <a href="${profile}" target="_blank">
                  <img src="${image}" alt="avtr">
              </a>
              <div class="chat-about">
                  <h6 class="m-b-0">${name}</h6>
                  <i class="fa fa-circle offline"></i>
                  <small>Last seen: ${lastSeen}</small>
              </div>
          </div>
  `;
    return wrapperTop + header + buttons + wrapperBottom
  }
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
  getChatAbout(
    block.attr('href'), block.attr('data'), block.attr('data-href'), block.attr('data-status'), block.attr('data-last-seen'));
  getMessagesInChat(block.attr('id'), block.attr('href'));
  $('.chat-history').scrollTop($('.chat-history').prop('scrollHeight'));
}

function chatListRender(data) {
  let chatList = data.results;
  $(".people-list").attr("data-href", data.next);
  let ulStart = `<ul id="chat-ul" class="list-unstyled chat-list mt-2 mb-0">`;
  let chats = ``;
  let ulEnd = `</ul>`;
  $.each(chatList, function (i) {
    if (chatList[i].last_message == null) {
      chatList[i].last_message = "no messages";
    }
    if (chatList[i].last_message_date == null) {
      chatList[i].last_message_date = chatList[i].date;
    }
    chats += chatListFunc(
      chatList[i].id, chatList[i].user_chats[1].image, chatList[i].file, chatList[i].name, chatList[i].last_message_date,
      chatList[i].last_message, chatList[i].count_unread, chatList[i].user_chats[1].full_name,
      chatList[i].user_chats[1].profile, chatList[i].interlocutor_online);
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

function getChatAbout(image, name, profile, status, lastSeen) {
  $('#header').empty();
  $('#header').prepend(chatAbout(image, name, profile, status, lastSeen));
  $('#uploadFile').change(uploadImage);
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
      console.log(message_list);
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
          message += outgoingMessage(message_list[i].content, message_list[i].date, message_list[i].message_file);
        } else {
          message += ingoingMessage(image, message_list[i].content, message_list[i].date, message_list[i].message_file);
        }
        message += `</ul>`;
        $('.chat-history').prepend(message);

      })
      $('.chat-history').attr('data', data.next);
      $('.chat-history').scrollTop($('.chat-history').prop('scrollHeight'));
    },
  })
}
