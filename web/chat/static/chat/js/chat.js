$(function () {
    $('#chatButton').click(connectToChat);
});

function connectToChat(){
  let button = $(this);
  let input = $('#username');
  console.log(input.val());
  console.log("click");
  window.location.pathname = button.attr("href");
  localStorage.setItem("username", input.val());
  console.log(window.location.pathname);
}
