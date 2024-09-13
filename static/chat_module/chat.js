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

let ws;
const roomName = window.location.pathname.split("/")[2];

function connect() {
    const token = getCookieValue("access_token");
    if (token) {
        ws = new WebSocket(`ws://localhost:8000/ws/${roomName}?token=${token}`);

        ws.onmessage = function(event) {
            const messages = document.getElementById('messages');
            const message = document.createElement('li');
            const content = document.createTextNode(event.data);
            message.appendChild(content);
            messages.appendChild(message);
        };

        ws.onclose = function(event) {
            console.log('Connection closed:', event);
        };

        ws.onerror = function(error) {
            console.error('WebSocket error:', error);
        };
    } else {
        alert("Token not found in cookies.");
    }
}

function sendMessage(event) {
    event.preventDefault();
    const input = document.getElementById("messageText");
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(input.value);
    } else {
        console.error('WebSocket is not open. Cannot send message.');
    }
    input.value = '';
}

function leaveRoom() {
    window.location.href = 'http://localhost:8000/rooms';
}

function leaveAndCloseRoom() {
    const encodedRoomName = encodeURIComponent(roomName);
    console.log(`Отправка запроса на удаление комнаты: ${encodedRoomName}`);

    fetch(`http://localhost:8000/rooms/${encodedRoomName}`, {
        method: 'DELETE',
        headers: {
            'Authorization': `Bearer ${getCookieValue("access_token")}`,
            'Content-Type': 'application/json'
        },
    })
    .then(response => {
        console.log('Статус ответа:', response.status);
        // Проверяем, есть ли ответ в формате JSON
        return response.text().then(text => {
            let data;
            try {
                data = JSON.parse(text);
            } catch (error) {
                data = { detail: text };
            }
            return { status: response.status, data };
        });
    })
    .then(({ status, data }) => {
        console.log('Ответ сервера:', data);
        if (data.detail) {
            console.error('Ошибка:', data.detail);
        }
        if (status === 200) {
            window.location.href = "http://localhost:8000/rooms"; // Успешное удаление
        } else {
            console.error('Ошибка при удалении комнаты:', data);
        }
    })
    .catch(error => {
        console.error('Ошибка сети:', error);
    });
}

function redirectToRegister() {
    window.location.href = "http://localhost:8000/login";
}

connect();

document.getElementById("messageForm").onsubmit = sendMessage;
