document.addEventListener("DOMContentLoaded", () => {

    const csrfToken = document
        .querySelector('meta[name="csrf-token"]')
        ?.getAttribute("content");

    // ===============================
    // Custom confirm modal (shared pattern)
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
    // Upload modal & AJAX Submit (Fixes CSRF with multipart/form-data)
    // ===============================

    const uploadModal = document.getElementById("uploadModal");
    const openBtn = document.getElementById("openUploadModal");
    const closeBtn = document.getElementById("closeUploadModal");
    const cancelBtn = document.getElementById("cancelUpload");
    const uploadForm = uploadModal?.querySelector("form");

    if (openBtn) openBtn.addEventListener("click", () => {
        uploadModal.style.display = "flex";
    });

    if (closeBtn) closeBtn.addEventListener("click", () => {
        uploadModal.style.display = "none";
    });

    if (cancelBtn) cancelBtn.addEventListener("click", () => {
        uploadModal.style.display = "none";
    });

    if (uploadModal) {
        uploadModal.addEventListener("click", e => {
            if (e.target === uploadModal) uploadModal.style.display = "none";
        });
    }

    // التعامل مع إرسال فورم الرفع عبر Fetch لتجنب مشكلة الـ CSRF مع الملفات
    if (uploadForm) {
        uploadForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            
            const submitBtn = uploadForm.querySelector(".save-btn");
            const originalText = submitBtn.textContent;
            submitBtn.textContent = "Uploading...";
            submitBtn.disabled = true;

            const formData = new FormData(uploadForm);

            try {
                const response = await fetch(uploadForm.action, {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": csrfToken
                    },
                    body: formData
                });

                if (response.redirected) {
                    window.location.href = response.url;
                } else {
                    const result = await response.json();
                    if (result.success) {
                        window.location.reload();
                    } else {
                        alert("Upload failed: " + (result.message || "Unknown error"));
                        submitBtn.textContent = originalText;
                        submitBtn.disabled = false;
                    }
                }
            } catch (error) {
                alert("Server error during upload.");
                submitBtn.textContent = originalText;
                submitBtn.disabled = false;
            }
        });
    }

    // ===============================
    // Category -> show/hide expiry field
    // ===============================

    const categorySelect = document.getElementById("categorySelect");
    const expiryField = document.getElementById("expiryField");

    const syncExpiryVisibility = () => {
        if (!categorySelect || !expiryField) return;
        expiryField.style.display =
            categorySelect.value === "calibration_certificate" ? "block" : "none";
    };

    if (categorySelect) {
        categorySelect.addEventListener("change", syncExpiryVisibility);
        syncExpiryVisibility();
    }

    // ===============================
    // Equipment type -> filter serial dropdown
    // ===============================

    const equipmentTypeSelect = document.getElementById("equipmentTypeSelect");
    const equipmentIdField = document.getElementById("equipmentIdField");
    const equipmentIdSelect = document.getElementById("equipmentIdSelect");

    const syncEquipmentOptions = () => {

        if (!equipmentTypeSelect || !equipmentIdSelect) return;

        const type = equipmentTypeSelect.value;

        if (!type) {
            equipmentIdField.style.display = "none";
            return;
        }

        equipmentIdField.style.display = "block";

        Array.from(equipmentIdSelect.options).forEach(opt => {
            if (!opt.dataset.type) return; // placeholder option
            opt.hidden = opt.dataset.type !== type;
        });

        equipmentIdSelect.value = "";

    };

    if (equipmentTypeSelect) {
        equipmentTypeSelect.addEventListener("change", syncEquipmentOptions);
        syncEquipmentOptions();
    }

    // ===============================
    // Delete document
    // ===============================

    document.querySelectorAll(".del-doc-btn").forEach(btn => {

        btn.addEventListener("click", async () => {

            const card = btn.closest(".doc-card");
            const docId = card?.dataset.docId;

            if (!docId) return;

            const confirmed = await showConfirmModal(
                "This will permanently delete this document and its file. Continue?",
                "Delete"
            );

            if (!confirmed) return;

            fetch(`/documents/${docId}/delete`, {
                method: "POST",
                headers: { "X-CSRFToken": csrfToken }
            })
            .then(r => r.json())
            .then(result => {
                if (result.success) {
                    card.remove();
                } else {
                    alert("Delete failed: " + (result.message || "unknown error"));
                }
            })
            .catch(() => alert("Server error while deleting."));

        });

    });

    // ===============================
    // Inline edit (title / expiry date)
    // ===============================

    document.querySelectorAll(".doc-card .editable").forEach(cell => {

        cell.addEventListener("click", function () {

            if (this.querySelector("input")) return;

            const card = this.closest(".doc-card");
            const docId = card?.dataset.docId;
            const field = this.dataset.field;

            const oldRaw = field === "expiry_date"
                ? (this.dataset.raw || "")
                : this.textContent.trim();

            const input = document.createElement("input");
            input.type = field === "expiry_date" ? "date" : "text";
            input.value = oldRaw;

            const originalHTML = this.innerHTML;
            this.innerHTML = "";
            this.appendChild(input);
            input.focus();

            let settled = false;

            const save = () => {

                if (settled) return;
                settled = true;

                const value = input.value.trim();

                fetch(`/documents/${docId}/update`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": csrfToken
                    },
                    body: JSON.stringify({ field, value })
                })
                .then(r => r.json())
                .then(result => {

                    if (!result.success) {
                        this.innerHTML = originalHTML;
                        alert("Save failed: " + (result.message || "unknown error"));
                        return;
                    }

                    if (field === "title") {
                        this.textContent = value;
                    } else {
                        // reload to re-render the expiry badge state correctly
                        window.location.reload();
                    }

                })
                .catch(() => {
                    this.innerHTML = originalHTML;
                    alert("Server error while saving.");
                });

            };

            input.addEventListener("keydown", e => {
                if (e.key === "Enter") { e.preventDefault(); save(); input.blur(); }
                if (e.key === "Escape") { settled = true; this.innerHTML = originalHTML; }
            });

            input.addEventListener("blur", save);

        });

    });

});
