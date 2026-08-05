/* ==========================================================
                        JOBS JS
========================================================== */

document.addEventListener("DOMContentLoaded", () => {

    const csrfToken = document
        .querySelector('meta[name="csrf-token"]')
        ?.getAttribute("content");

    // ===============================
    // Highlight cell when arriving from Information page (?well=...)
    // ===============================

    const params = new URLSearchParams(window.location.search);
    const highlightWell = params.get("well");

    if (highlightWell) {

        const links = Array.from(document.querySelectorAll(".job-cell .job-link"))
            .filter(a => a.textContent.trim() === highlightWell.trim());

        links.forEach(link => {

            const cell = link.closest(".job-cell");
            if (!cell) return;

            cell.classList.add("highlight-cell");

        });

        if (links.length > 0) {

            links[0].scrollIntoView({
                behavior: "smooth",
                block: "center",
                inline: "center"
            });

            setTimeout(() => {
                links.forEach(link => {
                    link.closest(".job-cell")?.classList.remove("highlight-cell");
                });
            }, 4000);

        }

    }

    // ===============================
    // Sidebar: expand / collapse year
    // ===============================

    document.querySelectorAll(".year-btn").forEach(btn => {

    const group = btn.closest(".year-group");
    const months = group?.querySelector(".months");

    if (!months) return;

    // يبدأ مقفول
    btn.classList.add("collapsed");
    months.classList.add("collapsed");

    btn.addEventListener("click", () => {

        btn.classList.toggle("collapsed");
        months.classList.toggle("collapsed");

    });

});

    // ===============================
    // Custom confirm modal (replaces native confirm())
    // ===============================

    const showConfirmModal = (message, confirmText = "Confirm") => {

        return new Promise(resolve => {

            const overlay = document.createElement("div");
            overlay.className = "mgms-confirm-overlay";

            overlay.innerHTML = `
                <div class="mgms-confirm-box">
                    <div class="mgms-confirm-icon">
                        <i class="bi bi-exclamation-triangle-fill"></i>
                    </div>
                    <p class="mgms-confirm-message">${message}</p>
                    <div class="mgms-confirm-actions">
                        <button type="button" class="mgms-confirm-cancel">Cancel</button>
                        <button type="button" class="mgms-confirm-ok">${confirmText}</button>
                    </div>
                </div>
            `;

            document.body.appendChild(overlay);

            const cleanup = (result) => {
                overlay.remove();
                resolve(result);
            };

            overlay.querySelector(".mgms-confirm-cancel")
                .addEventListener("click", () => cleanup(false));

            overlay.querySelector(".mgms-confirm-ok")
                .addEventListener("click", () => cleanup(true));

            overlay.addEventListener("click", e => {
                if (e.target === overlay) cleanup(false);
            });

        });

    };

    // ===============================
    // Worked-days badge live update
    // ===============================

    const renderWorkedBadge = (count) => {

        if (count >= 20) {
            return `<span class="badge bg-success">${count} Days</span>`;
        }

        if (count >= 10) {
            return `<span class="badge bg-warning text-dark">${count} Days</span>`;
        }

        if (count > 0) {
            return `<span class="badge bg-danger">${count} Days</span>`;
        }

        return `<span class="badge bg-secondary">Idle</span>`;

    };

    const updateWorkedBadge = (equipmentType, equipmentId, workedDays) => {

        if (workedDays === undefined || workedDays === null) return;

        const target = document.getElementById(
            `worked-${equipmentType}-${equipmentId}`
        );

        if (target) {
            target.innerHTML = renderWorkedBadge(workedDays);
        }

    };

    // ===============================
    // Editable Cells
    // ===============================
    document.querySelectorAll(".job-cell").forEach(cell => {

    cell.addEventListener("click", function () {

        // منع المستخدم العادي من التعديل
        if (!document.body.classList.contains("admin-user")) {
            return;
        }

        if (this.querySelector("input")) return;

            if (this.querySelector("input")) return;

            const oldValue = this.textContent.trim();

            const input = document.createElement("input");
            input.type = "text";
            input.className = "job-input";
            input.placeholder = "Well...";
            input.value = oldValue;

            this.innerHTML = "";
            this.appendChild(input);

            input.focus();
            input.select();

            let settled = false;

            const restoreLink = (value) => {
                this.innerHTML =
                    `<span class="job-link">${value} <a href="/information/?search=${encodeURIComponent(value)}" class="job-info-link" title="View in Information" onclick="event.stopPropagation();"><i class="bi bi-box-arrow-up-right"></i></a></span>`;
            };

            const syncToServer = (value) => {

                return fetch("/jobs/save", {

                    method: "POST",

                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": csrfToken
                    },

                    body: JSON.stringify({

                        year: this.dataset.year,
                        month: this.dataset.month,
                        day: this.dataset.day,

                        well_number: value,

                        equipment_type: this.dataset.equipmentType,
                        equipment_id: this.dataset.equipmentId

                    })

                })

                .then(async r => {

                    if (!r.ok) {
                        const text = await r.text();
                        throw new Error(
                            `HTTP ${r.status}: ${text.slice(0, 200)}`
                        );
                    }

                    return r.json();

                });

            };

            const saveValue = () => {

                if (settled) return;

                const value = input.value.trim();

                // مفيش أي تغيير فعلي عن القيمة الأصلية
                if (value === oldValue) {
                    settled = true;
                    if (value === "") this.innerHTML = "";
                    else restoreLink(value);
                    return;
                }

                settled = true;

                syncToServer(value)

                .then(result => {

                    if (!result.success) {

                        alert(
                            "Save Failed: " +
                            (result.message || "unknown error")
                        );
                        this.innerHTML = oldValue
                            ? `<span class="job-link">${oldValue} <a href="/information/?search=${encodeURIComponent(oldValue)}" class="job-info-link" title="View in Information" onclick="event.stopPropagation();"><i class="bi bi-box-arrow-up-right"></i></a></span>`
                            : "";
                        return;

                    }

                    if (value === "") {
                        this.innerHTML = "";
                    } else {
                        restoreLink(value);
                    }

                    updateWorkedBadge(
                        this.dataset.equipmentType,
                        this.dataset.equipmentId,
                        result.worked_days
                    );

                })

                .catch(err => {

                    console.error("Job save error:", err);
                    alert("Server Error: " + err.message);
                    this.innerHTML = oldValue
                        ? `<span class="job-link">${oldValue} <a href="/information/?search=${encodeURIComponent(oldValue)}" class="job-info-link" title="View in Information" onclick="event.stopPropagation();"><i class="bi bi-box-arrow-up-right"></i></a></span>`
                        : "";

                });

            };

            input.addEventListener("keydown", e => {

                if (e.key === "Enter") {
                    e.preventDefault();
                    saveValue();
                    input.blur();
                }

                if (e.key === "Escape") {
                    settled = true;
                    if (oldValue) restoreLink(oldValue);
                    else this.innerHTML = "";
                }

            });

            input.addEventListener("blur", saveValue);

        });

    });

   
// ===============================
// Export Excel
// ===============================

const exportBtn = document.getElementById("exportExcelBtn");

if (exportBtn) {

    exportBtn.addEventListener("click", () => {

        window.location.href =
            `/jobs/export?year=${window.currentYear}&month=${window.currentMonth}`;

    });

}

    // ===============================
    // Close Month
    // ===============================

    const closeBtn =
        document.getElementById("closeMonthBtn");

    if (closeBtn) {

        closeBtn.addEventListener("click", async () => {

            const confirmed = await showConfirmModal(
                "Closing this month will archive it and open the next month. You'll still be able to edit entries later if needed. Continue?",
                "Close Month"
            );

            if (!confirmed) return;

            const first =
                document.querySelector(".job-cell");

            if (!first) {

                alert("No data found.");
                return;

            }

            const response = await fetch(
                "/jobs/close-month",
                {

                    method: "POST",

                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": csrfToken
                    },

                    body: JSON.stringify({

                        year: first.dataset.year,
                        month: first.dataset.month

                    })

                }
            );

            const result =
                await response.json();

            if (result.success) {

                window.location.href =
                    result.redirect;

            } else {

                alert("Failed to close month.");

            }

        });

    }

});
/* ==========================================================
   ENGINEER WALK ANIMATION
========================================================== */

document.addEventListener("DOMContentLoaded", () => {

    const engineer = document.getElementById("engineerCharacter");
    const sprite = document.getElementById("engineerSprite");

    if (!engineer || !sprite) return;


    engineer.addEventListener("animationend", (event) => {

        if (event.animationName !== "engineerMove") {
            return;
        }

        // وقف تبديل Frames بعد الوصول
        sprite.style.animation = "none";

        // استخدم Frame الوقوف
        sprite.style.backgroundPositionX = "0px";

        engineer.classList.add("arrived");

    });

});
/* ==========================================================
                    IMPORT JOBS
========================================================== */

const importJobsForm = document.getElementById("importJobsForm");

if (importJobsForm) {

    importJobsForm.addEventListener("submit", async function (e) {

        e.preventDefault();

        const formData = new FormData(this);
        const csrfToken = formData.get("csrf_token");
        for (const pair of formData.entries()) {
    console.log(pair[0], pair[1]);
}
        console.log(formData.get("excel_file"));

        const preview = document.getElementById("jobsPreview");

        preview.innerHTML = `
            <div class="text-center py-4">
                <div class="spinner-border text-primary"></div>
                <div class="mt-2">Reading Excel...</div>
            </div>
        `;

        const response = await fetch("/jobs/import-preview", {
    method: "POST",
    body: formData,
    headers: {
        "X-CSRFToken": csrfToken
    }
});

console.log("Status:", response.status);

const data = await response.json();

console.log("Response:", data);

if (!data.success) {
    preview.innerHTML = `
                <div class="alert alert-danger">
                    ${data.message}
                </div>
            `;

            return;
        }

        let html = `

            <div class="alert alert-success">

                <strong>${data.total}</strong> rows found.

            </div>

            <div class="table-responsive">

            <table class="table table-bordered table-sm">

            <thead>

            <tr>
        `;

        data.columns.forEach(col => {

            html += `<th>${col}</th>`;

        });

        html += "</tr></thead><tbody>";

        data.rows.forEach(row => {

            html += "<tr>";

            data.columns.forEach(col => {

                html += `<td>${row[col] ?? ""}</td>`;

            });

            html += "</tr>";

        });

        html += `
            </tbody>
            </table>
            </div>
        `;

        preview.innerHTML = html;
        document.getElementById("confirmImportBtn").style.display = "inline-block";

    });

}
const confirmImportBtn = document.getElementById("confirmImportBtn");

if (confirmImportBtn) {

    confirmImportBtn.addEventListener("click", async () => {

        const form = document.getElementById("importJobsForm");
        const formData = new FormData(form);

        const response = await fetch("/jobs/import", {

            method: "POST",

            body: formData,

            headers: {
                "X-CSRFToken": formData.get("csrf_token")
            }

        });

        const data = await response.json();

        if (!data.success) {

            alert(data.message);
            return;

        }

        alert(`Imported ${data.imported} rows successfully.`);
        window.location.href =
    `/jobs?year=${data.year}&month=${data.month}`;
    });

}