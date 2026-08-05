// ========================================
// MGMS Main JS
// ========================================

function updateDateTime() {

    const dateElement = document.getElementById("liveDate");
    const timeElement = document.getElementById("liveTime");

    if (!dateElement || !timeElement) return;

    const now = new Date();

    dateElement.textContent = now.toLocaleDateString("en-GB", {
        day: "2-digit",
        month: "short",
        year: "numeric"
    });

    timeElement.textContent = now.toLocaleTimeString("en-GB");
}

updateDateTime();
setInterval(updateDateTime, 1000);

console.log("Main JS Loaded");