/* ==========================================================
                    INFORMATION PAGE JS
========================================================== */

document.addEventListener("DOMContentLoaded", () => {
    const isAdmin = document.body.dataset.role === "admin";

    const csrfToken = document
        .querySelector('meta[name="csrf-token"]')
        ?.getAttribute("content");

    // ===============================
    // Custom confirm modal (shared pattern with Jobs)
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

    const postJSON = (url, body) => {

        return fetch(url, {

            method: "POST",

            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken
            },

            body: JSON.stringify(body)

        })

        .then(async r => {

            if (!r.ok) {
                const text = await r.text();
                throw new Error(`HTTP ${r.status}: ${text.slice(0, 200)}`);
            }

            return r.json();

        });

    };

    // ===============================
    // Sidebar: expand / collapse year
    // ===============================

    document.querySelectorAll(".year-btn").forEach(btn => {

    const group = btn.closest(".year-group");
    const months = group?.querySelector(".months");

    if (!months) return;

    // اقفل السنوات عند تحميل الصفحة
    btn.classList.add("collapsed");
    months.classList.add("collapsed");

    btn.addEventListener("click", () => {

        btn.classList.toggle("collapsed");
        months.classList.toggle("collapsed");

    });

});
     if (isAdmin) {
    // ===============================
    // Editable cells (click → edit → save on Enter/blur)
    // ===============================

    document.querySelectorAll(".information-table .editable").forEach(cell => {

        // خلية اسم البئر: الضغط على الرابط نفسه = بحث سريع، مش تعديل
        const wellLink = cell.querySelector(".well-link");

        if (wellLink) {

            wellLink.addEventListener("click", e => {

                e.preventDefault();

                const input = document.getElementById("searchInput");
                const form = cell.closest("form") || document.querySelector(".search-bar");

                if (input && form) {
                    input.value = wellLink.textContent.trim();
                    form.submit();
                }

            });

        }

        cell.addEventListener("click", function (e) {

            if (this.querySelector("input")) return;

            // لو دوس على رابط البئر، سيبها لل listener بتاعها فوق
            if (e.target.classList.contains("well-link")) return;

            const row = this.closest("tr");
            const rowId = row?.dataset.rowId;

            if (!rowId) return;

            const field = this.dataset.field;
            const type = this.dataset.type || "text";

            const oldRaw = type === "date"
                ? (this.dataset.raw || "")
                : this.textContent.trim();

            const input = document.createElement("input");
            input.type = type === "date" ? "date" : (type === "number" ? "number" : "text");
            if (type === "number") input.step = "0.01";
            input.value = oldRaw;

            this.innerHTML = "";
            this.appendChild(input);
            input.focus();
            input.select();

            let settled = false;

            const restoreDisplay = (raw) => {

                if (type === "date") {

                    if (!raw) {
                        this.innerHTML = "";
                        this.dataset.raw = "";
                        return;
                    }

                    const d = new Date(raw + "T00:00:00");
                    const label = d.toLocaleDateString("en-GB", {
                        day: "2-digit", month: "short", year: "numeric"
                    }).replace(/ /g, " ");

                    this.textContent = label;
                    this.dataset.raw = raw;

                } else if (field === "well_number") {

                    this.innerHTML = raw
                        ? `<a href="#" class="well-link">${raw}</a>`
                        : "";

                    const link = this.querySelector(".well-link");
                    if (link) {
                        link.addEventListener("click", ev => {
                            ev.preventDefault();
                            const searchInput = document.getElementById("searchInput");
                            const form = document.querySelector(".search-bar");
                            if (searchInput && form) {
                                searchInput.value = raw;
                                form.submit();
                            }
                        });
                    }

                } else {

                    this.textContent = raw;

                }

            };

            const save = () => {

                if (settled) return;

                const value = input.value.trim();

                if (value === oldRaw) {
                    settled = true;
                    restoreDisplay(oldRaw);
                    return;
                }

                settled = true;

                postJSON(`/information/row/${rowId}/update`, { field, value })

                .then(result => {

                    if (!result.success) {
                        alert("Save Failed: " + (result.message || "unknown error"));
                        restoreDisplay(oldRaw);
                        return;
                    }

                    restoreDisplay(value);

                    // لو عدّلنا From/To، حدّث خلية Days في نفس الصف لايف
                    if ((field === "from_date" || field === "to_date") && result.days !== undefined && result.days !== null) {

                        const daysCell = row.querySelector('.editable[data-field="days"]');

                        if (daysCell && !daysCell.querySelector("input")) {
                            daysCell.textContent = result.days;
                        }

                    }

                })

                .catch(err => {
                    console.error("Information save error:", err);
                    alert("Server Error: " + err.message);
                    restoreDisplay(oldRaw);
                });

            };

            input.addEventListener("keydown", e2 => {

                if (e2.key === "Enter") {
                    e2.preventDefault();
                    save();
                    input.blur();
                }

                if (e2.key === "Escape") {
                    settled = true;
                    restoreDisplay(oldRaw);
                }

            });

            input.addEventListener("blur", save);

        });

    });

    // ===============================
    // Edit Row modal
    // ===============================

    const editModal = document.getElementById("editRowModal");
    const closeEditModalBtn = document.getElementById("closeEditRowModal");
    const cancelEditBtn = document.getElementById("cancelEditRow");
    const saveEditBtn = document.getElementById("saveEditRow");

    let editingRowId = null;

    const getCellRaw = (row, field) => {
        const cell = row.querySelector(`.editable[data-field="${field}"]`);
        if (!cell) return "";
        if (cell.dataset.type === "date") return cell.dataset.raw || "";
        return cell.textContent.trim();
    };

    document.querySelectorAll(".edit-row-btn").forEach(btn => {

        btn.addEventListener("click", () => {

            const row = btn.closest("tr");
            editingRowId = row?.dataset.rowId;

            if (!editingRowId || !editModal) return;

            document.getElementById("editGaugeSerial").value = getCellRaw(row, "gauge_serial");
            document.getElementById("editChangedTo").value = getCellRaw(row, "changed_to");
            document.getElementById("editWellNumber").value = getCellRaw(row, "well_number");
            document.getElementById("editFromDate").value = getCellRaw(row, "from_date");
            document.getElementById("editToDate").value = getCellRaw(row, "to_date");
            document.getElementById("editSurvey").value = getCellRaw(row, "survey");
            document.getElementById("editRigName").value = getCellRaw(row, "rig_name");
            document.getElementById("editPosition").value =
              getCellRaw(row, "position");
            document.getElementById("editBundleCarrier").value = getCellRaw(row, "bundle_carrier_sn");
            document.getElementById("editBatterySn").value = getCellRaw(row, "battery_sn");
            document.getElementById("editEngineer").value = getCellRaw(row, "engineer");
            document.getElementById("editTotalHours").value = getCellRaw(row, "total_hours");
            document.getElementById("editTotalSamples").value = getCellRaw(row, "total_samples");
            document.getElementById("editComment").value = getCellRaw(row, "comment");

            editModal.style.display = "flex";

        });

    });

    const closeEditModal = () => {
        if (editModal) editModal.style.display = "none";
        editingRowId = null;
    };

    if (closeEditModalBtn) closeEditModalBtn.addEventListener("click", closeEditModal);
    if (cancelEditBtn) cancelEditBtn.addEventListener("click", closeEditModal);

    if (editModal) {
        editModal.addEventListener("click", e => {
            if (e.target === editModal) closeEditModal();
        });
    }

    if (saveEditBtn) {

        saveEditBtn.addEventListener("click", async () => {

            if (!editingRowId) return;

            const row = document.querySelector(`tr[data-row-id="${editingRowId}"]`);
            if (!row) return;

            const fieldMap = {
                gauge_serial: "editGaugeSerial",
                changed_to: "editChangedTo",
                well_number: "editWellNumber",
                from_date: "editFromDate",
                to_date: "editToDate",
                survey: "editSurvey",
                rig_name: "editRigName",
                position: "editPosition",
                bundle_carrier_sn: "editBundleCarrier",
                battery_sn: "editBatterySn",
                engineer: "editEngineer",
                total_hours: "editTotalHours",
                total_samples: "editTotalSamples",
                comment: "editComment"
            };

            saveEditBtn.disabled = true;
            saveEditBtn.textContent = "Saving...";

            try {

                for (const [field, inputId] of Object.entries(fieldMap)) {

                    const newValue = document.getElementById(inputId).value.trim();
                    const oldValue = getCellRaw(row, field);

                    if (newValue === oldValue) continue;

                    const result = await postJSON(
                        `/information/row/${editingRowId}/update`,
                        { field, value: newValue }
                    );

                    if (!result.success) {
                        alert(`Failed to save "${field}": ` + (result.message || "unknown error"));
                        continue;
                    }

                    const cell = row.querySelector(`.editable[data-field="${field}"]`);

                    if (cell) {

                        if (cell.dataset.type === "date") {

                            cell.dataset.raw = newValue;

                            cell.textContent = newValue
                                ? new Date(newValue + "T00:00:00").toLocaleDateString("en-GB", {
                                    day: "2-digit", month: "short", year: "numeric"
                                })
                                : "";

                        } else if (field === "well_number") {

                            cell.innerHTML = newValue
                                ? `<a href="#" class="well-link">${newValue}</a>`
                                : "";

                            const link = cell.querySelector(".well-link");

                            if (link) {
                                link.addEventListener("click", ev => {
                                    ev.preventDefault();
                                    const searchInput = document.getElementById("searchInput");
                                    const form = document.querySelector(".search-bar");
                                    if (searchInput && form) {
                                        searchInput.value = newValue;
                                        form.submit();
                                    }
                                });
                            }

                        } else {

                            cell.textContent = newValue;

                        }

                    }

                    if ((field === "from_date" || field === "to_date") && result.days !== undefined && result.days !== null) {
                        const daysCell = row.querySelector('.editable[data-field="days"]');
                        if (daysCell) daysCell.textContent = result.days;
                    }

                }

                closeEditModal();

            } catch (err) {

                alert("Server Error: " + err.message);

            } finally {

                saveEditBtn.disabled = false;
                saveEditBtn.textContent = "Save Changes";

            }

        });

    }

    // ===============================
    // Delete row
    // ===============================

    document.querySelectorAll(".del-row-btn").forEach(btn => {

        btn.addEventListener("click", async () => {

            const row = btn.closest("tr");
            const rowId = row?.dataset.rowId;

            if (!rowId) return;

            const confirmed = await showConfirmModal(
                "This will permanently delete this gauge entry. Continue?",
                "Delete"
            );

            if (!confirmed) return;

            postJSON(`/information/row/${rowId}/delete`, {})

            .then(result => {

                if (result.success) {
                    row.remove();
                } else {
                    alert("Delete Failed: " + (result.message || "unknown error"));
                }

            })

            .catch(err => {
                alert("Server Error: " + err.message);
            });

        });

    });

    // ===============================
    // Attachments
    // ===============================

    const wireAttachmentCell = (cell) => {

        const row = cell.closest("tr");
        const rowId = row?.dataset.rowId;
        const fileInput = cell.querySelector(".attachment-input");
        const triggerBtn = cell.querySelector(".attach-btn:not(.has-file):not(.replace-attach-btn)");
        const replaceBtn = cell.querySelector(".replace-attach-btn");

        if (!fileInput || !rowId) return;

        if (triggerBtn) triggerBtn.addEventListener("click", () => fileInput.click());
        if (replaceBtn) replaceBtn.addEventListener("click", () => fileInput.click());

        fileInput.addEventListener("change", () => {

            const file = fileInput.files[0];
            if (!file) return;

            const formData = new FormData();
            formData.append("file", file);

            fetch(`/information/row/${rowId}/attachment`, {

                method: "POST",
                headers: { "X-CSRFToken": csrfToken },
                body: formData

            })

            .then(r => r.json())

            .then(result => {

                if (!result.success) {
                    alert("Upload Failed: " + (result.message || "unknown error"));
                    return;
                }

                cell.innerHTML = `
                    <input type="file" class="attachment-input" hidden accept=".xlsx,.xls,.csv">
                    <a href="${result.attachment_url}" class="attach-btn has-file" title="${result.attachment_name}">
                        <i class="bi bi-file-earmark-excel"></i>
                    </a>
                    <button type="button" class="attach-btn replace-attach-btn" title="Replace file">
                        <i class="bi bi-arrow-repeat"></i>
                    </button>
                `;

                wireAttachmentCell(cell);

            })

            .catch(() => alert("Server Error while uploading file."));

        });

    };

    document.querySelectorAll(".attachment-cell").forEach(cell => {
        wireAttachmentCell(cell);
    });

    // ===============================
    // Close Month
    // ===============================

    const closeBtn = document.getElementById("closeMonthBtn");

    if (closeBtn) {

        closeBtn.addEventListener("click", async () => {

            const confirmed = await showConfirmModal(
                "Closing this month will archive it and open the next month. You'll still be able to edit entries later if needed. Continue?",
                "Close Month"
            );

            if (!confirmed) return;

            postJSON("/information/close-month", {
                year: window.informationYear,
                month: window.informationMonth
            })

            .then(result => {

                if (result.success && result.redirect) {
                    window.location.href = result.redirect;
                } else {
                    alert("Failed to close month.");
                }

            })

            .catch(err => alert("Server Error: " + err.message));

        });

    }
    }

    // ===============================
    // Export Excel
    // ===============================

    const exportBtn = document.getElementById("exportExcelBtn");

    if (exportBtn) {

        exportBtn.addEventListener("click", () => {

            window.location.href =
                `/information/export?year=${window.informationYear}&month=${window.informationMonth}`;

        });

    }

    // ===============================
    // Add Entry modal
    // ===============================

    const modal = document.getElementById("addEntryModal");
    const addBtn = document.getElementById("addEntryBtn");
    const closeModalBtn = document.getElementById("closeAddEntryModal");
    const cancelBtn = document.getElementById("cancelAddEntry");
    const saveBtn = document.getElementById("saveAddEntry");
    const bundleSelect = document.getElementById("bundleTypeSelect");
    const gaugeRowsContainer = document.getElementById("gaugeRowsContainer");

    const gaugeRowTemplate = (index) => `
    <div class="gauge-row-card" data-index="${index}">

        <div class="field">
            <label>Gauge S/N #${index + 1}</label>
            <input
                type="text"
                class="g-gauge-serial"
                placeholder="e.g. S6005">
        </div>

        <div class="field">
            <label>Position</label>
            <select class="g-position">
                <option value="Tandem">Tandem</option>
                <option value="Internal">Internal</option>
                <option value="External">External</option>
            </select>
        </div>

        <div class="field">
            <label>Changed To</label>
            <input
                type="text"
                class="g-changed-to"
                placeholder="optional">
        </div>

        <div class="field">
            <label>Battery S/N</label>
            <input
                type="text"
                class="g-battery-sn">
        </div>

        <div class="field">
            <label>Engineer</label>
            <input
                type="text"
                class="g-engineer">
        </div>

        <div class="field">
            <label>Total Hours</label>
            <input
                type="number"
                min="0"
                step="0.01"
                class="g-total-hours"
                placeholder="Gauge working hours">
        </div>

        <div class="field">
            <label>Total Samples</label>
            <input
                type="number"
                min="0"
                step="1"
                class="g-total-samples"
                placeholder="Number of readings">
        </div>

        <div class="field full">
            <label>Comment</label>
            <input
                type="text"
                class="g-comment"
                placeholder="optional">
        </div>

    </div>
`;

    const renderGaugeRows = () => {

    if (!gaugeRowsContainer || !bundleSelect) return;

    let count = 2;

    if (bundleSelect.value === "single") {
        count = 2;
    }

    else if (bundleSelect.value === "dual") {
        count = 2;
    }

    else if (bundleSelect.value === "quad") {
        count = 4;
    }

    gaugeRowsContainer.innerHTML = "";

    for (let i = 0; i < count; i++) {

        gaugeRowsContainer.insertAdjacentHTML(
            "beforeend",
            gaugeRowTemplate(i)
        );

    }

};

    const openModal = () => {
        if (!modal) return;
        modal.style.display = "flex";
        renderGaugeRows();
    };

    const closeModal = () => {
        if (!modal) return;
        modal.style.display = "none";
    };

    if (addBtn) addBtn.addEventListener("click", openModal);
    if (closeModalBtn) closeModalBtn.addEventListener("click", closeModal);
    if (cancelBtn) cancelBtn.addEventListener("click", closeModal);

    if (modal) {
        modal.addEventListener("click", e => {
            if (e.target === modal) closeModal();
        });
    }

    if (bundleSelect) bundleSelect.addEventListener("change", renderGaugeRows);

    if (saveBtn) {

        saveBtn.addEventListener("click", () => {

            const wellNumber = document.getElementById("sharedWellNumber")?.value.trim();
            const fromDate = document.getElementById("sharedFromDate")?.value;
            const toDate = document.getElementById("sharedToDate")?.value;
            const survey = document.getElementById("sharedSurvey")?.value.trim();
            const rigName = document.getElementById("sharedRigName")?.value.trim();
            const bundleCarrier = document.getElementById("sharedBundleCarrier")?.value.trim();
            
            if (!wellNumber) {
                alert("Well No is required.");
                return;
            }

            let days = 0;

            if (fromDate && toDate) {
                const d1 = new Date(fromDate);
                const d2 = new Date(toDate);
                days = Math.round((d2 - d1) / (1000 * 60 * 60 * 24)) + 1;
            }

            const gaugeCards = gaugeRowsContainer
                ? Array.from(gaugeRowsContainer.querySelectorAll(".gauge-row-card"))
                : [];

            if (gaugeCards.length === 0) {
                alert("At least one gauge row is required.");
                return;
            }

            const rows = gaugeCards.map(card => ({

    // =========================
    // Gauge-specific data
    // =========================

    gauge_serial:
        card.querySelector(".g-gauge-serial")?.value.trim() || "",
    position:
    card.querySelector(".g-position")?.value || "",

    changed_to:
        card.querySelector(".g-changed-to")?.value.trim() || "",

    battery_sn:
        card.querySelector(".g-battery-sn")?.value.trim() || "",

    engineer:
        card.querySelector(".g-engineer")?.value.trim() || "",

    total_hours:
        parseFloat(
            card.querySelector(".g-total-hours")?.value || "0"
        ),

    total_samples:
        parseInt(
            card.querySelector(".g-total-samples")?.value || "0",
            10
        ),

    comment:
        card.querySelector(".g-comment")?.value.trim() || "",


    // =========================
    // Shared Job data
    // =========================

    well_number: wellNumber,

    from_date:
        fromDate || null,

    to_date:
        toDate || null,

    days: days,

    survey:
        survey || "",

        rig_name:
        rigName || "",

    bundle_carrier_sn:
        bundleCarrier || ""

}));
            postJSON("/information/add-group", {
                year: window.informationYear,
                month: window.informationMonth,
                rows: rows
            })

            .then(result => {

                if (result.success) {
                    window.location.reload();
                } else {
                    alert("Failed to save entry.");
                }

            })

            .catch(err => alert("Server Error: " + err.message));

        });

    }

});
document
.getElementById("importExcelBtn")
.addEventListener("click", () => {

    document
    .getElementById("importExcelFile")
    .click();

});


const importInput = document.getElementById("importExcelFile");

if (importInput) {

    importInput.addEventListener("change", async function () {

        console.log("Selected file:", this.files);

        if (!this.files.length)
            return;

        const formData = new FormData();
        formData.append("file", this.files[0]);

        console.log("Sending request...");

        try {

            const csrfToken = document
    .querySelector('meta[name="csrf-token"]')
    ?.getAttribute("content");

const res = await fetch("/information/import", {

    method: "POST",

    headers: {
        "X-CSRFToken": csrfToken
    },

    body: formData

});

            console.log("Status:", res.status);

            const text = await res.text();
            console.log("Response:", text);

        } catch (err) {

            console.error(err);

        }

    });

}
