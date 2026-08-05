// ================================
// Show / Hide Password
// ================================

const password = document.getElementById("password");
const togglePassword = document.getElementById("togglePassword");

if (togglePassword && password) {

    togglePassword.addEventListener("click", () => {

        password.type =
            password.type === "password"
            ? "text"
            : "password";

        togglePassword.classList.toggle("bi-eye-fill");
        togglePassword.classList.toggle("bi-eye-slash-fill");

    });

}
const loginWrap = document.querySelector(".login-wrap");

if (loginWrap) {

    loginWrap.classList.remove("show");

    setTimeout(() => {
        document.querySelector(".status-pill").classList.add("show");
    }, 7000);

    setTimeout(() => {
        document.querySelector(".login-header h1").classList.add("show");
    }, 7300);

    setTimeout(() => {
        document.querySelector(".login-header p").classList.add("show");
    }, 7600);

    setTimeout(() => {
        document.querySelector(".panel").classList.add("show");
    }, 7900);

    setTimeout(() => {
        document.querySelectorAll(".form-group")[0].classList.add("show");
    }, 8200);

    setTimeout(() => {
        document.querySelectorAll(".form-group")[1].classList.add("show");
    }, 8500);

    setTimeout(() => {
        document.querySelector(".remember-row").classList.add("show");
    }, 8800);

    setTimeout(() => {
        document.querySelector(".login-btn").classList.add("show");
    }, 9100);

}


const loginVideo = document.getElementById("loginVideo");
const moveVideo = document.getElementById("moveVideo");


loginVideo.addEventListener("ended", () => {

    // إخفاء الفيديو الأول
    loginVideo.style.display = "none";

    // إظهار فيديو الحركة
    moveVideo.style.display = "block";

    // تشغيله
    moveVideo.play();

});

