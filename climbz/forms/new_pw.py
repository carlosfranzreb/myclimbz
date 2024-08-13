"""
Form used in the form to register a new climber.
"""

from __future__ import annotations

from flask_wtf import FlaskForm, RecaptchaField
from wtforms import PasswordField
from wtforms.validators import DataRequired


class NewPwForm(FlaskForm):
    """Form to create a password when registering a new climber."""

    new_pw = PasswordField("Password", validators=[DataRequired()])
    confirm_pw = PasswordField("Confirm password", validators=[DataRequired()])
    recaptcha = RecaptchaField()

    def validate(self) -> bool:
        """
        Check that the old password is correct and that the new password is
        confirmed.
        """
        if not super().validate():
            return False

        # check that the new password is confirmed
        if self.new_pw.data != self.confirm_pw.data:
            self.confirm_pw.errors.append("Passwords don't match")
            return False

        return True
