function getCookieValue(name) {
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        const [cookieName, cookieValue] = cookie.trim().split('=');
        if (cookieName === name) {
            return decodeURIComponent(cookieValue);
        }
    }
    return null;
}

const roomName = window.location.pathname.split("/")[2];
const token = getCookieValue("access_token");

if (token) {
    const ws = new WebSocket(`ws://localhost:8000/ws/${roomName}?token=${token}`);

    ws.onmessage = function(event) {
        const messages = document.getElementById('messages');
        const message = document.createElement('li');
        const content = document.createTextNode(event.data);
        message.appendChild(content);
        messages.appendChild(message);
    };

    function sendMessage(event) {
        event.preventDefault();
        const input = document.getElementById("messageText");
        ws.send(input.value);
        input.value = '';
    }

    function leaveRoom() {
        window.location.href = 'http://localhost:8000/rooms';
    }

    ws.onclose = function(event) {};

    ws.onerror = function(error) {};

} else {
    alert("Token not found in cookies.");
}

document.getElementById("messageForm").onsubmit = sendMessage;
