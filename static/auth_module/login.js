document.getElementById('loginForm').addEventListener('submit', async function(event) {
    event.preventDefault(); // Отменяем стандартное поведение формы

    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    const response = await fetch('/token', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
            username: username,
            password: password
        })
    });

    if (response.redirected) {
        // Если сервер перенаправляет на /rooms, выполняем переход
        window.location.href = response.url;
    } else if (!response.ok) {
        // Обработка ошибки
        const errorData = await response.json();
        alert(errorData.detail || 'An error occurred');
    }
});