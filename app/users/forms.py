from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (
    StringField,
    PasswordField,
    SubmitField,
    SelectField,
    BooleanField
)
from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    Length,
    Optional
)


class ProfileForm(FlaskForm):
    full_name = StringField(
        "Full Name",
        validators=[
            DataRequired(),
            Length(max=100)
        ]
    )

    email = StringField(
        "Email",
        validators=[
            DataRequired(),
            Email(),
            Length(max=120)
        ]
    )

    profile_image = FileField(
        "Profile Image",
        validators=[
            Optional(),
            FileAllowed(
                ["jpg", "jpeg", "png", "webp"],
                "Images only!"
            )
        ]
    )

    submit = SubmitField("Save Changes")


class ChangePasswordForm(FlaskForm):

    current_password = PasswordField(
        "Current Password",
        validators=[DataRequired()]
    )

    new_password = PasswordField(
        "New Password",
        validators=[
            DataRequired(),
            Length(min=6)
        ]
    )

    confirm_password = PasswordField(
        "Confirm Password",
        validators=[
            DataRequired(),
            EqualTo(
                "new_password",
                message="Passwords must match."
            )
        ]
    )

    submit = SubmitField("Change Password")


class UserForm(FlaskForm):

    username = StringField(
        "Username",
        validators=[
            DataRequired(),
            Length(max=50)
        ]
    )

    full_name = StringField(
        "Full Name",
        validators=[
            DataRequired(),
            Length(max=100)
        ]
    )

    email = StringField(
        "Email",
        validators=[
            DataRequired(),
            Email()
        ]
    )

    password = PasswordField(
        "Password",
        validators=[
            Optional(),
            Length(min=6)
        ]
    )

    confirm_password = PasswordField(
        "Confirm Password",
        validators=[
            EqualTo(
                "password",
                message="Passwords must match."
            )
        ]
    )

    role = SelectField(
        "Role",
        choices=[
            ("admin", "Administrator"),
            ("user", "User")
        ],
        validators=[DataRequired()]
    )

    is_active = BooleanField(
        "Active",
        default=True
    )

    submit = SubmitField("Save User")