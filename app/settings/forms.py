from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed

from wtforms import (
    StringField,
    SelectField,
    SubmitField
)

from wtforms.validators import DataRequired, Optional


class SettingsForm(FlaskForm):

    company_name = StringField(
        "Company Name",
        validators=[DataRequired()]
    )

    company_email = StringField(
        "Company Email"
    )

    company_phone = StringField(
        "Company Phone"
    )

    company_address = StringField(
        "Company Address"
    )

    company_logo = FileField(
        "Company Logo",
        validators=[
            Optional(),
            FileAllowed(
                ["png","jpg","jpeg","webp"],
                "Images only"
            )
        ]
    )



    theme = SelectField(
        "Theme",
        choices=[
            ("Light","Light"),
            ("Dark","Dark")
        ]
    )

    submit = SubmitField("Save Settings")