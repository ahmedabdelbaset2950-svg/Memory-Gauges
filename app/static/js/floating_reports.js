(() => {
    'use strict';

    const root = document.getElementById('mgms-floating-reports');
    if (!root) return;

    const card = root.querySelector('.mgms-report-card');
    const categoryEl = document.getElementById('mgmsReportCategory');
    const iconEl = document.getElementById('mgmsReportIcon');
    const titleEl = document.getElementById('mgmsReportTitle');
    const messageEl = document.getElementById('mgmsReportMessage');
    const counterEl = document.getElementById('mgmsReportCounter');
    const prevButton = document.getElementById('mgmsReportPrev');
    const nextButton = document.getElementById('mgmsReportNext');
    const closeButton = document.getElementById('mgmsReportClose');

    const notifications = [
        {
            category: 'System Update',
            icon: 'bi-bell-fill',
            title: 'Welcome to MGMS',
            message: 'The Memory Gauge Management System is ready. Important operational updates will appear in this panel.'
        },
        {
            category: 'Jobs Overview',
            icon: 'bi-clipboard2-check-fill',
            title: 'Keep your job records updated',
            message: 'Make sure every completed field operation is recorded in the Jobs module with the correct status and notes.'
        },
        {
            category: 'Equipment Reminder',
            icon: 'bi-cpu-fill',
            title: 'Equipment status reminder',
            message: 'Review equipment availability and maintenance status before assigning gauges or carriers to a new job.'
        }
    ];

    let currentIndex = 0;
    let rotationTimer = null;
    const interval = Math.max(1000, Number(root.dataset.interval) || 6000);

    function renderNotification(index) {
        currentIndex = (index + notifications.length) % notifications.length;
        const item = notifications[currentIndex];

        categoryEl.textContent = item.category;
        iconEl.innerHTML = `<i class="bi ${item.icon}" aria-hidden="true"></i>`;
        titleEl.textContent = item.title;
        messageEl.textContent = item.message;
        counterEl.textContent = `${currentIndex + 1} / ${notifications.length}`;

        card.classList.remove('mgms-report-changing');
        void card.offsetWidth;
        card.classList.add('mgms-report-changing');
    }

    function stopRotation() {
        if (rotationTimer !== null) {
            window.clearInterval(rotationTimer);
            rotationTimer = null;
        }
    }

    function startRotation() {
        stopRotation();
        if (!root.classList.contains('mgms-report-collapsed') && notifications.length > 1) {
            rotationTimer = window.setInterval(() => renderNotification(currentIndex + 1), interval);
        }
    }

    function showNext() {
        renderNotification(currentIndex + 1);
        startRotation();
    }

    function showPrevious() {
        renderNotification(currentIndex - 1);
        startRotation();
    }

    nextButton.addEventListener('click', showNext);
    prevButton.addEventListener('click', showPrevious);

    closeButton.setAttribute('aria-expanded', 'true');
    closeButton.addEventListener('click', () => {
        const collapsed = root.classList.toggle('mgms-report-collapsed');
        closeButton.setAttribute('aria-expanded', String(!collapsed));
        closeButton.setAttribute('aria-label', collapsed ? 'Expand notifications' : 'Collapse notifications');
        closeButton.innerHTML = collapsed
            ? '<i class="bi bi-chevron-up" aria-hidden="true"></i>'
            : '<i class="bi bi-dash-lg" aria-hidden="true"></i>';
        if (collapsed) stopRotation();
        else startRotation();
    });

    root.addEventListener('mouseenter', stopRotation);
    root.addEventListener('mouseleave', startRotation);
    root.addEventListener('focusin', stopRotation);
    root.addEventListener('focusout', event => {
        if (!root.contains(event.relatedTarget)) startRotation();
    });

    renderNotification(0);
    startRotation();
})();
