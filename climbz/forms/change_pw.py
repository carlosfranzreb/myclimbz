from __future__ import annotations

from flask_wtf import FlaskForm
from wtforms import PasswordField
from wtforms.validators import DataRequired

from climbz.models import Climber
from climbz import bcrypt


class ChangePwForm(FlaskForm):
    old_pw = PasswordField("Old password", validators=[DataRequired()])
    new_pw = PasswordField("New password", validators=[DataRequired()])
    confirm_pw = PasswordField("Confirm new password", validators=[DataRequired()])

    def validate(self, climber: Climber) -> bool:
        """
        Check that the old password is correct and that the new password is
        confirmed.
        """
        if not super().validate():
            return False

        # check that the old password is correct
        if not bcrypt.check_password_hash(climber.password, self.old_pw.data):
            self.old_pw.errors.append("Old password is wrong")
            return False

        # check that the new password is confirmed
        if self.new_pw.data != self.confirm_pw.data:
            self.confirm_pw.errors.append("New passwords don't match")
            return False

        # check that the new password is different from the old password
        if self.new_pw.data == self.old_pw.data:
            self.new_pw.errors.append(
                "New password must be different from old password"
            )
            return False

        return True
