/* ==========================================================
                    EQUIPMENT JS
========================================================== */

document.addEventListener("DOMContentLoaded", () => {

    initSearch();

    initMemoryGauge();

    initBundleCarrier();

    initBattery();

    initDeleteModal();
    // =====================================
// Open modal from Dashboard
// =====================================

if (window.openEquipment === "gauge") {

    const gaugeModal = document.getElementById("gaugeModal");

    if (gaugeModal) {

        new bootstrap.Modal(gaugeModal).show();

    }

}

if (window.openEquipment === "bundle") {

    const bundleModal = document.getElementById("bundleModal");

    if (bundleModal) {

        new bootstrap.Modal(bundleModal).show();

    }

}

});



if (window.openEquipment === "bundle") {

    const modalElement = document.getElementById("bundleModal");

    if (modalElement) {

        const modal = new bootstrap.Modal(modalElement);

        modal.show();

    }

}

/* ==========================================================
                        HELPERS
========================================================== */

function $(selector){
    return document.querySelector(selector);
}

function $all(selector){
    return document.querySelectorAll(selector);
}


/* ==========================================================
                        SEARCH
========================================================== */

function initSearch(){

    // Memory Gauge Search
    const gaugeSearch =
        $('input[placeholder="Search Memory Gauge"]');

    if(gaugeSearch){

        const rows =
            $all(".equipment-section")[0]
            .querySelectorAll("tbody tr");

        gaugeSearch.addEventListener("keyup", function(){

            const value =
                this.value.toLowerCase();

            rows.forEach(row=>{

                row.style.display =
                    row.innerText
                    .toLowerCase()
                    .includes(value)
                    ? ""
                    : "none";

            });

        });

    }


    // Bundle Search

    const bundleSearch =
        $('input[placeholder="Search Bundle Carrier"]');

    if(bundleSearch){

        const rows =
            $all(".equipment-section")[1]
            .querySelectorAll("tbody tr");

        bundleSearch.addEventListener("keyup",function(){

            const value =
                this.value.toLowerCase();

            rows.forEach(row=>{

                row.style.display =
                    row.innerText
                    .toLowerCase()
                    .includes(value)
                    ? ""
                    : "none";

            });

        });

    }

    // Battery Search

    const batterySearch =
        $('input[placeholder="Search Battery"]');

    if(batterySearch){

        const rows =
            $all(".equipment-section")[2]
            .querySelectorAll("tbody tr");

        batterySearch.addEventListener("keyup",function(){

            const value =
                this.value.toLowerCase();

            rows.forEach(row=>{

                row.style.display =
                    row.innerText
                    .toLowerCase()
                    .includes(value)
                    ? ""
                    : "none";

            });

        });

    }

}


/* ==========================================================
                    MEMORY GAUGE
========================================================== */

function initMemoryGauge(){

    const form =
        $("#gaugeForm");

    if(!form) return;


    /* ==========================
            ADD
    ========================== */

    const addBtn =
        document.querySelectorAll(".green-btn")[0];

    if(addBtn){

        addBtn.addEventListener("click",()=>{

            form.reset();

            form.action =
                form.dataset.addUrl;

            $("#gaugeModalTitle").innerText =
                "Add New Memory Gauge";

            $("#gaugeSubmitBtn").innerHTML =
                '<i class="bi bi-check-circle-fill me-2"></i>Save Memory Gauge';

            $("#editingGaugeId").value="";

        });

    }


    /* ==========================
            EDIT
    ========================== */

    document
    .querySelectorAll(".edit-gauge-btn")
    .forEach(button=>{

        button.addEventListener("click",function(){

            const id =
                this.dataset.id;

            form.action =
                form.dataset.editUrl
                .replace("0",id);

            $("#editingGaugeId").value =
                id;

            $("#gaugeModalTitle").innerText =
                "Edit Memory Gauge";

            $("#gaugeSubmitBtn").innerHTML =
                '<i class="bi bi-check-circle-fill me-2"></i>Update Memory Gauge';


            form.querySelector('[name="serial_number"]').value =
                this.dataset.serial || "";

            form.querySelector('[name="company"]').value =
                this.dataset.company || "";

            form.querySelector('[name="gauge_type"]').value =
                this.dataset.type || "";

            form.querySelector('[name="battery_serial"]').value =
                this.dataset.battery || "";

            form.querySelector('[name="calibration_date"]').value =
                this.dataset.calibration || "";

            form.querySelector('[name="status"]').value =
                this.dataset.status || "";

            form.querySelector('[name="notes"]').value =
                this.dataset.notes || "";


            form.querySelector('[name="supports_dual"]').checked =
                this.dataset.dual === "True";

            form.querySelector('[name="supports_quad"]').checked =
                this.dataset.quad === "True";


            if(form.querySelector('[name="dual_type"]')){

                form.querySelector('[name="dual_type"]').value =
                    this.dataset.dualtype || "";

            }

            if(form.querySelector('[name="quad_type"]')){

                form.querySelector('[name="quad_type"]').value =
                    this.dataset.quadtype || "";

            }

        });

    });

}
/* ==========================================================
                    BUNDLE CARRIER
========================================================== */

function initBundleCarrier(){

    const form = $("#bundleForm");

    if(!form) return;


    /* ==========================
            ADD
    ========================== */

    const addBtn =
        document.querySelectorAll(".green-btn")[1];

    if(addBtn){

        addBtn.addEventListener("click",()=>{

            form.reset();

            form.action =
                form.dataset.addUrl;

            $("#editingBundleId").value = "";

            $("#bundleModalTitle").innerText =
                "Add New Bundle Carrier";

            $("#bundleSubmitBtn").innerHTML =
                '<i class="bi bi-check-circle-fill me-2"></i>Save Bundle Carrier';

        });

    }


    /* ==========================
            EDIT
    ========================== */

    document
    .querySelectorAll(".edit-bundle-btn")
    .forEach(button=>{

        button.addEventListener("click",function(){

            const id =
                this.dataset.id;

            form.action =
                form.dataset.editUrl.replace("0",id);

            $("#editingBundleId").value =
                id;

            $("#bundleModalTitle").innerText =
                "Edit Bundle Carrier";

            $("#bundleSubmitBtn").innerHTML =
                '<i class="bi bi-check-circle-fill me-2"></i>Update Bundle Carrier';


            form.querySelector('[name="serial_number"]').value =
                this.dataset.serial || "";

            form.querySelector('[name="company"]').value =
                this.dataset.company || "";

            form.querySelector('[name="type"]').value =
                this.dataset.type || "";

            form.querySelector('[name="position"]').value =
    this.dataset.position || "";

// Pressure Test
form.querySelector('[name="pressure_test_date"]').value =
    this.dataset.pressure || "";

form.querySelector('[name="current_location"]').value =
    this.dataset.location || "";

            form.querySelector('[name="allen_key"]').value =
                this.dataset.allen || "";

            form.querySelector('[name="notes"]').value =
                this.dataset.notes || "";

        });

    });

}

/* ==========================================================
                    BATTERY
========================================================== */

function initBattery(){

    const form = $("#batteryForm");

    if(!form) return;


    /* ==========================
            ADD
    ========================== */

    const addBtn =
        document.querySelectorAll(".green-btn")[2];

    if(addBtn){

        addBtn.addEventListener("click",()=>{

            form.reset();

            form.action =
                form.dataset.addUrl;

            $("#editingBatteryId").value = "";

            $("#batteryModalTitle").innerText =
                "Add New Battery";

            $("#batterySubmitBtn").innerHTML =
                '<i class="bi bi-check-circle-fill me-2"></i>Save Battery';


            // ==========================================
            // New battery starts with zero previous usage
            // ==========================================

            const previousConsumption =
                form.querySelector('[name="previous_consumption"]');

            if(previousConsumption){

                previousConsumption.value = "0";

            }

        });

    }


    /* ==========================
            EDIT
    ========================== */

    document
    .querySelectorAll(".edit-battery-btn")
    .forEach(button=>{

        button.addEventListener("click",function(){

            const id =
                this.dataset.id;

            form.action =
                form.dataset.editUrl.replace("0",id);

            $("#editingBatteryId").value =
                id;

            $("#batteryModalTitle").innerText =
                "Edit Battery";

            $("#batterySubmitBtn").innerHTML =
                '<i class="bi bi-check-circle-fill me-2"></i>Update Battery';


            /* ==========================
                    BASIC DATA
            ========================== */

            form.querySelector('[name="serial_number"]').value =
                this.dataset.serial || "";

            form.querySelector('[name="compatible_gauge_type"]').value =
                this.dataset.gaugeType || "";

            form.querySelector('[name="capacity"]').value =
                this.dataset.capacity || "";

            form.querySelector('[name="capacity_unit"]').value =
                this.dataset.unit || "";


            /* ==========================
                PREVIOUS CONSUMPTION
            ========================== */

            const previousConsumption =
                form.querySelector('[name="previous_consumption"]');

            if(previousConsumption){

                previousConsumption.value =
                    this.dataset.previousConsumption || "0";

            }


            /* ==========================
                    STATUS
            ========================== */

            form.querySelector('[name="status"]').value =
                this.dataset.status || "";


            /* ==========================
                    NOTES
            ========================== */

            form.querySelector('[name="notes"]').value =
                this.dataset.notes || "";

        });

    });

}
/* ==========================================================
                    DELETE MODAL
========================================================== */

function initDeleteModal() {

    const modalElement = document.getElementById("deleteModal");

    if (!modalElement) return;

    const modal = new bootstrap.Modal(modalElement);

    const title = document.getElementById("deleteTitle");
    const confirmBtn = document.getElementById("confirmDeleteBtn");

    let currentForm = null;

    document.querySelectorAll(".delete-form .delete").forEach(btn => {

        btn.addEventListener("click", function () {

            currentForm = this.closest("form");

            const name = this.dataset.name || "";

            title.innerHTML =
                `Delete <strong>${name}</strong> ?`;

            modal.show();

        });

    });

    confirmBtn.addEventListener("click", function () {

        if (currentForm) {

            currentForm.submit();

        }

    });

}