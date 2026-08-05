import os
import uuid

from flask import (
    render_template,
    redirect,
    url_for,
    flash,
    request,
    current_app
)

from flask_login import (
    login_required,
    current_user
)

from werkzeug.utils import secure_filename

from app.extensions import db
from app.models.user import User

from app.users import users_bp
from app.users.forms import (
    ProfileForm,
    ChangePasswordForm,
    UserForm
)

from app.users.decorators import admin_required
from sqlalchemy.exc import IntegrityError

# ======================================================
# Profile
# ======================================================

@users_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():

    form = ProfileForm()

    if request.method == "GET":
        form.full_name.data = current_user.full_name
        form.email.data = current_user.email

    if form.validate_on_submit():

        current_user.full_name = form.full_name.data
        current_user.email = form.email.data

        image = form.profile_image.data

        if image:

            filename = secure_filename(image.filename)

            extension = filename.rsplit(".", 1)[1].lower()

            new_filename = (
                f"{uuid.uuid4().hex}.{extension}"
            )

            upload_folder = os.path.join(
                current_app.root_path,
                "static",
                "uploads",
                "profiles"
            )

            os.makedirs(
                upload_folder,
                exist_ok=True
            )

            image.save(
                os.path.join(
                    upload_folder,
                    new_filename
                )
            )

            current_user.profile_image = new_filename

        db.session.commit()

        flash(
            "Profile updated successfully.",
            "success"
        )

        return redirect(
            url_for("users.profile")
        )

    return render_template(
        "users/profile.html",
        form=form
    )


# ======================================================
# Change Password
# ======================================================

@users_bp.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():

    form = ChangePasswordForm()

    if form.validate_on_submit():

        if not current_user.check_password(
            form.current_password.data
        ):

            flash(
                "Current password is incorrect.",
                "danger"
            )

            return redirect(
                url_for("users.change_password")
            )

        current_user.set_password(
            form.new_password.data
        )

        db.session.commit()

        flash(
            "Password changed successfully.",
            "success"
        )

        return redirect(
            url_for("users.profile")
        )

    return render_template(
        "users/change_password.html",
        form=form
    )
# ======================================================
# Users List
# ======================================================

@users_bp.route("/")
@login_required
@admin_required
def users():

    users = User.query.order_by(User.full_name).all()

    return render_template(
        "users/users.html",
        users=users,
        form=UserForm()
    )

# ======================================================
# Create User
# ======================================================

@users_bp.route("/create", methods=["POST"])
@login_required
@admin_required
def create_user():

    form = UserForm()

    if form.validate_on_submit():

        if User.query.filter_by(username=form.username.data).first():
            flash("Username already exists.", "danger")
            return redirect(url_for("users.users"))

        if User.query.filter_by(email=form.email.data).first():
            flash("Email already exists.", "danger")
            return redirect(url_for("users.users"))

        user = User(

            full_name=form.full_name.data,

            username=form.username.data,

            email=form.email.data,

            role=form.role.data,

            is_active=form.is_active.data

        )

        user.set_password(form.password.data)

        db.session.add(user)

        db.session.commit()

        flash(
            "User created successfully.",
            "success"
        )

    else:

        flash(
            "Please check the entered data.",
            "danger"
        )

    return redirect(url_for("users.users"))

# ======================================================
# Edit User
# ======================================================

@users_bp.route("/<int:user_id>/edit", methods=["POST"])
@login_required
@admin_required
def edit_user(user_id):

    user = User.query.get_or_404(user_id)

    form = UserForm()

    if form.validate_on_submit():

        user.full_name = form.full_name.data

        user.username = form.username.data

        user.email = form.email.data

        user.role = form.role.data

        user.is_active = form.is_active.data

        db.session.commit()

        flash(
            "User updated successfully.",
            "success"
        )

    else:

        flash(
            "Please check the entered data.",
            "danger"
        )

    return redirect(url_for("users.users"))

# ======================================================
# Delete User
# ======================================================

@users_bp.route("/delete/<int:user_id>", methods=["POST"])
@login_required
@admin_required
def delete_user(user_id):

    user = User.query.get_or_404(user_id)

    if user.id == current_user.id:

        flash(
            "You cannot delete your own account.",
            "warning"
        )

        return redirect(
            url_for("users.users")
        )

    db.session.delete(user)
    db.session.commit()

    flash(
        "User deleted successfully.",
        "success"
    )

    return redirect(
        url_for("users.users")
    )


# ======================================================
# Toggle Active
# ======================================================

@users_bp.route("/toggle/<int:user_id>", methods=["POST"])
@login_required
@admin_required
def toggle_user(user_id):

    user = User.query.get_or_404(user_id)

    if user.id == current_user.id:

        flash(
            "You cannot deactivate your own account.",
            "warning"
        )

        return redirect(
            url_for("users.users")
        )

    user.is_active = not user.is_active

    db.session.commit()

    flash(
        "User status updated.",
        "success"
    )

    return redirect(
        url_for("users.users")
    )