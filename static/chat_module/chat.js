let ws;
const roomName = window.location.pathname.split("/")[2];
const roomNameDecode = decodeURIComponent(window.location.pathname.split("/")[2]);

function connect() {
    ws = new WebSocket(`ws://localhost:8000/ws/${roomName}`);
    ws.onmessage = function(event) {
        const messages = document.getElementById('messages');
        const message = document.createElement('li');
        const content = document.createTextNode(event.data);
        message.appendChild(content);
        messages.appendChild(message);
    };
}

function sendMessage(event) {
    event.preventDefault();
    const input = document.getElementById("messageText");
    ws.send(input.value);
    input.value = '';
}

function leaveRoom() {
    window.location.href = 'http://localhost:8000/rooms';
}

function leaveAndCloseRoom() {
    const encodedRoomName = encodeURIComponent(roomName); // используем roomName вместо roomNameDecode
    fetch(`http://localhost:8000/rooms/${roomNameDecode}`, {
        method: 'DELETE',
    })
    .then(response => {
        if (response.ok) {
            // Успешное удаление, перенаправляем на главную страницу
            window.location.href = "http://localhost:8000/rooms";
        } else {
            // Обработка ошибки, если комната не найдена или другая ошибка
            console.error('Ошибка при удалении комнаты:', response.statusText);
        }
    })
    .catch(error => {
        console.error('Ошибка сети:', error);
    });
}

function redirectToRegister() {
    window.location.href = "http://localhost:8000/login";
}

connect();  // Устанавливаем соединение при загрузке страницы