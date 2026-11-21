from datetime import datetime, timedelta
from time import monotonic

from flask import render_template, redirect, url_for, flash, jsonify, request, session
from flask_login import login_user, logout_user, login_required

from app.auth import auth_bp
from app.auth.forms import LoginForm
from app.auth.services import authenticate_user
from app.extensions import db


_login_attempts = {}
_LOCKOUT_SECONDS = 15 * 60
_MAX_ATTEMPTS = 5


def _login_key():
    username = (request.form.get("username") or "unknown").strip().lower()
    return f"{request.remote_addr}:{username}"


def _is_locked():
    attempt = _login_attempts.get(_login_key())
    return bool(attempt and attempt[0] >= _MAX_ATTEMPTS and monotonic() - attempt[1] < _LOCKOUT_SECONDS)


def _record_failure():
    key = _login_key()
    attempts = _login_attempts.get(key)
    count = 1 if not attempts else attempts[0] + 1
    _login_attempts[key] = (count, monotonic())


def _clear_failure():
    _login_attempts.pop(_login_key(), None)


@auth_bp.route("/", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        if _is_locked():
            message = "Too many failed attempts. Try again in 15 minutes."
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return jsonify({"success": False, "message": message}), 429
            flash(message, "danger")
            return render_template("auth/login.html", form=form)

        user = authenticate_user(form.username.data, form.password.data)
        if user:
            _clear_failure()
            session.permanent = bool(form.remember.data)
            login_user(user, remember=form.remember.data)
            user.normalize_role()
            user.last_login = datetime.utcnow()
            db.session.commit()

            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return jsonify({"success": True, "redirect": url_for("dashboard.dashboard")})

            flash("Login successful.", "success")
            return redirect(url_for("dashboard.dashboard"))

        _record_failure()
        message = "Invalid username or password."
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"success": False, "message": message}), 401
        flash(message, "danger")

    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.", "success")
    return redirect(url_for("auth.login"))
