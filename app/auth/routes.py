from flask import render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required

from app.auth import auth_bp
from app.auth.forms import LoginForm
from app.auth.services import authenticate_user
from datetime import datetime
from app.extensions import db

@auth_bp.route("/", methods=["GET", "POST"])
def login():

    form = LoginForm()

    if form.validate_on_submit():

        user = authenticate_user(
            form.username.data,
            form.password.data
        )

        if user:
            login_user(
                 user,
                 remember=form.remember.data
            )

            user.last_login = datetime.utcnow()
            db.session.commit()

        return redirect(url_for("dashboard.dashboard"))

        flash(
            "Invalid username/email or password.",
            "danger"
        )

    return render_template(
        "auth/login.html",
        form=form
    )


@auth_bp.route("/logout")
@login_required
def logout():

    logout_user()

    flash(
        "Logged out successfully.",
        "success"
    )

    return redirect(url_for("auth.login"))


