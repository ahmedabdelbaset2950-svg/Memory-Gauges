// ======================================================
// MGMS Dashboard
// Version 1.0
// ======================================================

// -------------------------
// Live Date & Time
// -------------------------

function updateDateTime() {

    const now = new Date();

    const optionsDate = {
        weekday: "short",
        day: "2-digit",
        month: "short",
        year: "numeric"
    };

    document.getElementById("liveDate").innerHTML =
        now.toLocaleDateString("en-GB", optionsDate);

    document.getElementById("liveTime").innerHTML =
        now.toLocaleTimeString("en-GB");

}

updateDateTime();

setInterval(updateDateTime,1000);


// ======================================================
// Charts
// ======================================================

Chart.defaults.font.family = "Poppins";

Chart.defaults.color = "#64748b";


// -------------------------
// Gauge Usage Year
// -------------------------

const dashboardData = window.MGMS_DASHBOARD_DATA || {};
const gaugeUsedYearLabels =
    (dashboardData.gaugeUsedYear || []).map(r => r[0]);

const gaugeUsedYearData =
    (dashboardData.gaugeUsedYear || []).map(r => r[1]);

const gaugeUsedMonthLabels =
    (dashboardData.gaugeUsedMonth || []).map(r => r[0]);

const gaugeUsedMonthData =
    (dashboardData.gaugeUsedMonth || []).map(r => r[1]);

const changedGaugeYearLabels =
    (dashboardData.changedGaugeYear || []).map(r => r[0]);

const changedGaugeYearData =
    (dashboardData.changedGaugeYear || []).map(r => r[1]);

const changedGaugeMonthLabels =
    (dashboardData.changedGaugeMonth || []).map(r => r[0]);

const changedGaugeMonthData =
    (dashboardData.changedGaugeMonth || []).map(r => r[1]);

new Chart(document.getElementById("gaugeYearChart"),{

    type:"bar",

    data:{
        labels:gaugeUsedYearLabels,
        datasets:[{
            label:"Gauge Used",
            data:gaugeUsedYearData,
            borderRadius:8
        }]
    },

    options:{
        responsive:true,
        maintainAspectRatio:false,
        plugins:{
            legend:{display:false}
        }
    }

});


new Chart(document.getElementById("gaugeMonthChart"),{

    type:"bar",

    data:{
        labels:gaugeUsedMonthLabels,
        datasets:[{
            label:"Gauge Used",
            data:gaugeUsedMonthData,
            borderRadius:8
        }]
    },

    options:{
        responsive:true,
        maintainAspectRatio:false,
        plugins:{
            legend:{display:false}
        }
    }

});


new Chart(document.getElementById("changedGaugeYearChart"),{

    type:"bar",

    data:{
        labels:changedGaugeYearLabels,
        datasets:[{
            label:"Changed Gauge",
            data:changedGaugeYearData,
            borderRadius:8
        }]
    },

    options:{
        responsive:true,
        maintainAspectRatio:false,
        plugins:{
            legend:{display:false}
        }
    }

});


new Chart(document.getElementById("changedGaugeMonthChart"),{

    type:"bar",

    data:{
        labels:changedGaugeMonthLabels,
        datasets:[{
            label:"Changed Gauge",
            data:changedGaugeMonthData,
            borderRadius:8
        }]
    },

    options:{
        responsive:true,
        maintainAspectRatio:false,
        plugins:{
            legend:{display:false}
        }
    }

});

// ======================================================
// Counter Animation
// ======================================================

const counters = document.querySelectorAll(".stat-number");

counters.forEach(counter=>{

const target = Number(counter.innerText) || 0;

let current = 0;

const speed = Math.max(1,Math.ceil(target/60));

const update=()=>{

if(current<target){

current+=speed;

if(current>target){

current=target;

}

counter.innerText=current;

requestAnimationFrame(update);

}

};

update();

});


// ======================================================
// Quick Action Hover
// ======================================================

document.querySelectorAll(".action-btn").forEach(btn=>{

btn.addEventListener("mouseenter",()=>{

btn.style.transform="translateY(-4px)";

});

btn.addEventListener("mouseleave",()=>{

btn.style.transform="translateY(0px)";

});

});


// ======================================================
// Console
// ======================================================

function reloadDashboard() {

    const year =
        document.getElementById("yearFilter")?.value;

    const month =
        document.getElementById("monthFilter")?.value;

    if (!year || !month) return;

    window.location.href =
        `/dashboard?year=${year}&month=${month}`;
}


document.getElementById("yearFilter")
    ?.addEventListener("change", reloadDashboard);

document.getElementById("monthFilter")
    ?.addEventListener("change", reloadDashboard);

document.getElementById("yearFilter2")
    ?.addEventListener("change", reloadDashboard);

document.getElementById("monthFilter2")
    ?.addEventListener("change", reloadDashboard);