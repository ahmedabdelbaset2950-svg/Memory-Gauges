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

const sidebarToggle = document.getElementById("sidebarToggle");
const sidebarBackdrop = document.getElementById("sidebarBackdrop");
const mobileNavigation = window.matchMedia("(max-width: 991.98px)");

function setSidebarOpen(isOpen) {
    document.body.classList.toggle("sidebar-open", isOpen);
    sidebarToggle?.setAttribute("aria-expanded", String(isOpen));
}

sidebarToggle?.addEventListener("click", () => {
    setSidebarOpen(!document.body.classList.contains("sidebar-open"));
});

sidebarBackdrop?.addEventListener("click", () => setSidebarOpen(false));

document.querySelectorAll(".sidebar-link").forEach(link => {
    link.addEventListener("click", () => {
        if (mobileNavigation.matches) setSidebarOpen(false);
    });
});

document.addEventListener("keydown", event => {
    if (event.key === "Escape") setSidebarOpen(false);
});

mobileNavigation.addEventListener("change", event => {
    if (!event.matches) setSidebarOpen(false);
});
