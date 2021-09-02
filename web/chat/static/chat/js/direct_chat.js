const username = localStorage.getItem("username");;
const chatSocket = new WebSocket(
            'ws://'
            + window.location.host
            + '/ws/chat/?username='
            + username
);

chatSocket.onmessage = function(e) {
            // console.log(e.data);
            const data = JSON.parse(e.data);
            console.log(data)
            if (data.type == "user.connect") {
              console.log(data.data.username);
              $("#usernameList").append("<p> " + data.data.username + "</p>")
            }
            if (data.type == "fetch.message") {
              document.querySelector('#chat-log').value += (data.content + '\n');
            }
            document.querySelector('#chat-log').value += (data.content + '\n');
};

chatSocket.onclose = function(e) {
            console.error('Chat socket closed unexpectedly');
};

document.querySelector('#chat-message-input').focus();
document.querySelector('#chat-message-input').onkeyup = function(e) {
            if (e.keyCode === 13) {  // enter, return
                document.querySelector('#chat-message-submit').click();
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
