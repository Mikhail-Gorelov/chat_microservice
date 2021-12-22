$(function () {
    initChat();
});

function initChat() {
  const urlSearchParams = new URLSearchParams(window.location.search);
  const params = Object.fromEntries(urlSearchParams.entries());
  $.ajax({
    url: "/init/",
    type: "POST",
    data: params,
    success: function (data) {
      console.log("success", data);
      localStorage.setItem('userData', JSON.stringify(data));
      window.location.href = '/'
    },
    error: function (data) {
      console.log("error", data);
    },
  })
}
