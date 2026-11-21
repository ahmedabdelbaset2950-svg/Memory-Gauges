const password = document.getElementById("password");
const togglePassword = document.getElementById("togglePassword");

if (togglePassword && password) {
    togglePassword.addEventListener("click", () => {
        password.type = password.type === "password" ? "text" : "password";
        togglePassword.classList.toggle("bi-eye-fill");
        togglePassword.classList.toggle("bi-eye-slash-fill");
    });
}

const loginVideo = document.getElementById("loginVideo");
const moveVideo = document.getElementById("moveVideo");

if (loginVideo && moveVideo) {
    loginVideo.addEventListener("ended", () => {
        loginVideo.style.display = "none";
        moveVideo.style.display = "block";
        moveVideo.play();
    });
}
