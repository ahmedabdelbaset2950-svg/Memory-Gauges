import os
import uuid

from flask import (
    render_template,
    redirect,
    url_for,
    flash,
    current_app
)

from flask_login import (
    login_required
)

from werkzeug.utils import secure_filename

from app.extensions import db

from app.models.app_settings import AppSettings

from app.settings import settings_bp
from app.settings.forms import SettingsForm

from app.users.decorators import admin_required


# ======================================================
# Settings
# ======================================================

@settings_bp.route("/", methods=["GET", "POST"])
@login_required
@admin_required
def index():

    settings = AppSettings.query.first()

    if settings is None:

        settings = AppSettings()

        db.session.add(settings)

        db.session.commit()

    form = SettingsForm(obj=settings)

    # FileField يجب أن يبدأ فارغاً
    form.company_logo.data = None

    if form.validate_on_submit():

        settings.company_name = form.company_name.data
        settings.company_email = form.company_email.data
        settings.company_phone = form.company_phone.data
        settings.company_address = form.company_address.data

        
        settings.theme = form.theme.data

        image = form.company_logo.data

        if image and hasattr(image, "filename") and image.filename:

            filename = secure_filename(image.filename)

            extension = filename.rsplit(".", 1)[1].lower()

            new_name = f"{uuid.uuid4().hex}.{extension}"

            upload_folder = os.path.join(
                current_app.static_folder,
                "uploads",
                "company"
            )

            os.makedirs(upload_folder, exist_ok=True)

            image.save(
                os.path.join(
                    upload_folder,
                    new_name
                )
            )

            settings.company_logo = new_name

        db.session.commit()

        flash(
            "Settings updated successfully.",
            "success"
        )

        return redirect(url_for("settings.index"))

    return render_template(
        "settings/settings.html",
        form=form,
        settings=settings
    )