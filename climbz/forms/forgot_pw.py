from flask_wtf import FlaskForm, RecaptchaField
from wtforms import EmailField
from wtforms.validators import DataRequired


class ForgotPwForm(FlaskForm):
    """Form to get a new password by e-mail."""

    email = EmailField("Email", validators=[DataRequired()])
    recaptcha = RecaptchaField()