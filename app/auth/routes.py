from datetime import datetime

from flask import (
    render_template,
    redirect,
    url_for,
    flash,
    jsonify,
    request,
)

from flask_login import (
    login_user,
    logout_user,
    login_required,
)

from app.auth import auth_bp
from app.auth.forms import LoginForm
from app.auth.services import authenticate_user
from app.extensions import db


@auth_bp.route("/", methods=["GET", "POST"])
def login():

    form = LoginForm()

    if form.validate_on_submit():

        user = authenticate_user(
            form.username.data,
            form.password.data,
        )

        if user:

            login_user(
                user,
                remember=form.remember.data,
            )

            user.last_login = datetime.utcnow()
            db.session.commit()

            # AJAX Login
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return jsonify(
                    {
                        "success": True,
                        "redirect": url_for("dashboard.dashboard"),
                    }
                )

            flash("Login successful.", "success")

            return redirect(
                url_for("dashboard.dashboard")
            )

        # AJAX Error
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify(
                {
                    "success": False,
                    "message": "Invalid username or password.",
                }
            ), 401

        flash(
            "Invalid username or password.",
            "danger",
        )

    return render_template(
        "auth/login.html",
        form=form,
    )


@auth_bp.route("/logout")
@login_required
def logout():

    logout_user()

    flash(
        "Logged out successfully.",
        "success",
    )

    return redirect(
        url_for("auth.login")
    )