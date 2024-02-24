from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import InputRequired

from climbz.models import Climber
from climbz import bcrypt


class LoginForm(FlaskForm):
    """Form to login."""

    email = StringField("Email", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])
    remember = BooleanField("Remember me")
    submit = SubmitField("Submit")

    def validate(self) -> bool:
        """
        Check that the form is valid, that the email is in the database, and that the
        password matches the one in the database.
        """
        is_valid = True
        if not super().validate():
            is_valid = False
        else:
            # check if the email is in the database
            climber = Climber.query.filter_by(email=self.email.data).first()
            if climber is None:
                self.email.errors.append("Wrong e-mail")
                is_valid = False
            else:
                # check if the password is correct
                if not bcrypt.check_password_hash(climber.password, self.password.data):
                    self.password.errors.append("Wrong password")
                    is_valid = False

        return is_valid
