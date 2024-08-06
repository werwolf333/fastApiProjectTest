function showForm() {
    var form = document.getElementById("newRoomForm");
    if (form.style.display === "none") {
        form.style.display = "block";
    } else {
        form.style.display = "none";
    }
}

function redirectToRegister() {
    window.location.href = "http://localhost:8000/login";
}