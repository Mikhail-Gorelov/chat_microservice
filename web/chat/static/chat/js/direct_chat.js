const username = localStorage.getItem("username");;
const chatSocket = new WebSocket(
            'ws://'
            + window.location.host
            + '/ws/chat/?username='
            + username
);

chatSocket.onmessage = function(e) {
            const data = JSON.parse(e.data);
            console.log(data)
            if (data.type == "user.connect") {
              console.log(data.data.username);
              $("#usernameList").append("<p> " + data.data.username + "</p>")
            }
            if (data.type == "fetch.messages") {
              $('#chat-log').append(data.author_id + ' says:  ' + data.content + ' at ' + data.date + '\n');
            }
            if (data.command == "new_message") {
              $('#chat-log').append("I am saying: " + data.message + '\n');
            }
};

chatSocket.onclose = function(e) {
            console.error('Chat socket closed unexpectedly');
};

$('#chat-message-input').focus();
$('#chat-message-input').onkeyup = function(e) {
            if (e.keyCode === 13) {  // enter, return
                $('#chat-message-submit').click();
            }
};

document.querySelector('#chat-message-submit').onclick = function(e) {
            const messageInputDom = document.querySelector('#chat-message-input');
            const message = messageInputDom.value;
            chatSocket.send(JSON.stringify({
                'command': 'new_message',
                'message': message
            }));
            messageInputDom.value = '';
};
