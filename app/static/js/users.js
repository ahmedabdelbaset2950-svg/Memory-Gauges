// ======================================================
// USER MODAL
// ======================================================

const modalTitle = document.getElementById("userModalTitle");
const form = document.getElementById("userForm");

const userId = document.getElementById("userId");

const passwordFields = document.getElementById("passwordFields");

const saveBtn = document.getElementById("saveUserBtn");


// ==========================
// NEW USER
// ==========================

document.querySelector(".new-user-btn").addEventListener("click", () => {

    form.reset();

    userId.value = "";

    passwordFields.style.display = "";

    modalTitle.innerHTML = "Create User";

    saveBtn.innerHTML = `
        <i class="bi bi-check-circle"></i>
        Save User
    `;

    form.action = "/users/create";

});


// ==========================
// EDIT USER
// ==========================

document.querySelectorAll(".edit-user-btn").forEach(btn=>{

    btn.addEventListener("click",()=>{

        modalTitle.innerHTML="Edit User";

        passwordFields.style.display="none";

        saveBtn.innerHTML=`
            <i class="bi bi-pencil"></i>
            Update User
        `;

        userId.value=btn.dataset.id;

        document.getElementById("full_name").value=btn.dataset.fullname;

        document.getElementById("username").value=btn.dataset.username;

        document.getElementById("email").value=btn.dataset.email;

        document.getElementById("role").value=btn.dataset.role;

        document.getElementById("is_active").checked=
            btn.dataset.active==="True";

        form.action="/users/"+btn.dataset.id+"/edit";

    });

});
// ======================================================
// DELETE USER
// ======================================================

let deleteForm = null;

document.querySelectorAll(".delete-form .delete").forEach(btn => {

    btn.addEventListener("click", () => {

        deleteForm = btn.closest("form");

        document.getElementById("deleteTitle").textContent =
            `Delete "${btn.dataset.name}" ?`;

        const modal = new bootstrap.Modal(
            document.getElementById("deleteModal")
        );

        modal.show();

    });

});

document.getElementById("confirmDeleteBtn").addEventListener("click", () => {

    if (deleteForm) {

        deleteForm.submit();

    }

});