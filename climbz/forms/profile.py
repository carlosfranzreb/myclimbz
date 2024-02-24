""" Forms related to users. """

from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    SubmitField,
    IntegerField,
)


class ProfileForm(FlaskForm):
    """Form to edit profile data."""

    # login information
    email = StringField("Email")
    password = PasswordField("Password")

    # personal information
    name = StringField("Name")
    birthdate = StringField("Birthdate")
    years_climbing = IntegerField("Years climbing")
    weight = IntegerField("Weight (kg)")
    height = IntegerField("Height (cm)")
    ape_index = IntegerField("Ape index (cm)")

    submit = SubmitField("Submit")
