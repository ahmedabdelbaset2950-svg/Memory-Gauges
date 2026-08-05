from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):

    username = StringField(
        "Username or Email",
        validators=[DataRequired(message="Please enter your username or email.")]
    )

    password = PasswordField(
        "Password",
        validators=[DataRequired(message="Please enter your password.")]
    )

    remember = BooleanField("Remember Me")

    submit = SubmitField("Sign In")