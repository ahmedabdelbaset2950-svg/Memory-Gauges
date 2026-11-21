document.body.classList.add('dashboard-page');

function updateDateTime() {
    const dateElement = document.getElementById('liveDate');
    const timeElement = document.getElementById('liveTime');
    if (!dateElement || !timeElement) return;

    const now = new Date();
    dateElement.textContent = now.toLocaleDateString('en-GB', {
        day: '2-digit', month: 'short', year: 'numeric'
    });
    timeElement.textContent = now.toLocaleTimeString('en-GB', { hour12: true });
}

updateDateTime();
window.setInterval(updateDateTime, 1000);

const dashboardData = window.MGMS_DASHBOARD_DATA || {};
const palette = ['#38BDF8', '#3B82F6', '#2DD4BF', '#34D399', '#FBBF24', '#A78BFA', '#FB7185'];

if (window.Chart) {
    Chart.defaults.font.family = 'Inter, Segoe UI, Arial, sans-serif';
    Chart.defaults.font.size = 10;
    Chart.defaults.color = '#91a4b8';
    Chart.defaults.borderColor = 'rgba(148,176,203,.10)';

    const tooltip = {
        backgroundColor: 'rgba(7, 19, 33, .96)',
        titleColor: '#edf4fb',
        bodyColor: '#c8d8e7',
        borderColor: 'rgba(56, 189, 248, .26)',
        borderWidth: 1,
        padding: 10,
        cornerRadius: 8,
        displayColors: true,
        boxPadding: 4
    };

    const scales = {
        x: {
            grid: { display: false },
            border: { display: false },
            ticks: { color: '#879db2', maxRotation: 0, autoSkip: true }
        },
        y: {
            beginAtZero: true,
            grid: { color: 'rgba(148,176,203,.09)', drawBorder: false },
            border: { display: false },
            ticks: { precision: 0, color: '#879db2', padding: 6 }
        }
    };

    function dataPairs(key) {
        return (dashboardData[key] || []).map(row => [String(row[0]), Number(row[1]) || 0]);
    }

    function barGradient(context, color) {
        const chart = context.chart;
        const area = chart.chartArea;
        if (!area) return color;
        const gradient = chart.ctx.createLinearGradient(0, area.bottom, 0, area.top);
        gradient.addColorStop(0, `${color}99`);
        gradient.addColorStop(1, color);
        return gradient;
    }

    function createBarChart(canvasId, key, label, colorIndex) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return;
        const pairs = dataPairs(key);
        new Chart(canvas, {
            type: 'bar',
            data: {
                labels: pairs.map(pair => pair[0]),
                datasets: [{
                    label,
                    data: pairs.map(pair => pair[1]),
                    backgroundColor: context => barGradient(context, palette[colorIndex]),
                    borderColor: palette[colorIndex],
                    borderWidth: 1,
                    borderRadius: 7,
                    borderSkipped: false,
                    barPercentage: .68,
                    categoryPercentage: .72
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: { duration: 850, easing: 'easeOutQuart' },
                interaction: { mode: 'index', intersect: false },
                plugins: {
                    legend: { display: false },
                    tooltip
                },
                scales
            }
        });
    }

    function createLineChart(canvasId, key, label, colorIndex) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return;
        const pairs = dataPairs(key);
        new Chart(canvas, {
            type: 'line',
            data: {
                labels: pairs.map(pair => pair[0]),
                datasets: [{
                    label,
                    data: pairs.map(pair => pair[1]),
                    borderColor: palette[colorIndex],
                    backgroundColor: context => {
                        const chart = context.chart;
                        const area = chart.chartArea;
                        if (!area) return `${palette[colorIndex]}24`;
                        const gradient = chart.ctx.createLinearGradient(0, area.top, 0, area.bottom);
                        gradient.addColorStop(0, `${palette[colorIndex]}55`);
                        gradient.addColorStop(1, `${palette[colorIndex]}05`);
                        return gradient;
                    },
                    fill: true,
                    borderWidth: 2,
                    tension: .38,
                    pointRadius: 3,
                    pointHoverRadius: 5,
                    pointBackgroundColor: '#0d1d30',
                    pointBorderColor: palette[colorIndex],
                    pointBorderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: { duration: 900, easing: 'easeOutQuart' },
                interaction: { mode: 'index', intersect: false },
                plugins: { legend: { display: false }, tooltip },
                scales
            }
        });
    }

    createBarChart('gaugeYearChart', 'gaugeUsedYear', 'Gauge Used', 0);
    createBarChart('gaugeMonthChart', 'gaugeUsedMonth', 'Gauge Used', 2);
    createLineChart('changedGaugeYearChart', 'changedGaugeYear', 'Changed Gauge', 5);
    createLineChart('changedGaugeMonthChart', 'changedGaugeMonth', 'Changed Gauge', 6);
}

const counters = document.querySelectorAll('.stat-number');
counters.forEach(counter => {
    const target = Number(counter.textContent.trim()) || 0;
    if (target === 0) return;
    counter.textContent = '0';
    const duration = 700;
    const start = performance.now();

    function animate(now) {
        const progress = Math.min((now - start) / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3);
        counter.textContent = String(Math.round(target * eased));
        if (progress < 1) window.requestAnimationFrame(animate);
    }
    window.requestAnimationFrame(animate);
});

function reloadDashboard() {
    const year = document.getElementById('yearFilter')?.value;
    const month = document.getElementById('monthFilter')?.value;
    if (!year || !month) return;
    window.location.href = `/dashboard?year=${encodeURIComponent(year)}&month=${encodeURIComponent(month)}`;
}

['yearFilter', 'monthFilter', 'yearFilter2', 'monthFilter2'].forEach(id => {
    document.getElementById(id)?.addEventListener('change', reloadDashboard);
});

(function initDashboardClock() {
    const heroDate = document.getElementById('mgmsHeroDate');
    const heroTime = document.getElementById('mgmsHeroTime');
    const welcomeTitle = document.getElementById('mgmsWelcomeTitle');

    const firstName = welcomeTitle
        ? welcomeTitle.textContent.trim().replace(/^Welcome back,\s*/i, '').replace(/^Good (morning|afternoon|evening),\s*/i, '')
        : 'Engineer';

    function updateHeroClock() {
        const now = new Date();
        if (heroDate) {
            heroDate.textContent = new Intl.DateTimeFormat('en-GB', {
                timeZone: 'Africa/Cairo', weekday: 'long', day: '2-digit', month: 'long', year: 'numeric'
            }).format(now);
        }
        if (heroTime) {
            heroTime.textContent = new Intl.DateTimeFormat('en-GB', {
                timeZone: 'Africa/Cairo', hour: '2-digit', minute: '2-digit', hour12: true
            }).format(now);
        }

        if (welcomeTitle) {
            const hour = Number(new Intl.DateTimeFormat('en-GB', {
                timeZone: 'Africa/Cairo', hour: '2-digit', hourCycle: 'h23'
            }).format(now));
            let greeting = 'Good evening';
            if (hour >= 5 && hour < 12) greeting = 'Good morning';
            else if (hour >= 12 && hour < 17) greeting = 'Good afternoon';
            welcomeTitle.textContent = `${greeting}, ${firstName || 'Engineer'} 👋`;
        }
    }

    updateHeroClock();
    window.setInterval(updateHeroClock, 30000);
})();
