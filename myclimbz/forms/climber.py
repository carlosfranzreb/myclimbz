from __future__ import annotations
from collections.abc import Sequence
from typing import Any, Mapping

from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    SubmitField,
    IntegerField,
    SelectField,
    DateField,
    EmailField,
)
from wtforms.validators import Optional, DataRequired
from sqlalchemy import func

from myclimbz.models import Climber


FIELDS = [
    "email",
    "name",
    "birthdate",
    "year_started_climbing",
    "height",
    "ape_index",
    "grade_scale",
]


class ClimberForm(FlaskForm):
    """Form to edit profile data."""

    # login information
    email = EmailField("Email", validators=[DataRequired()])

    # personal information
    name = StringField("Name", validators=[DataRequired()])
    birthdate = DateField("Birth date", validators=[Optional()])
    year_started_climbing = IntegerField("Climbing since year", validators=[Optional()])
    height = IntegerField("Height (cm)", validators=[Optional()])
    ape_index = IntegerField("Ape index (cm)", validators=[Optional()])

    # preferences
    grade_scale = SelectField(
        "Preferred grading system", choices=[("font", "font"), ("hueco", "hueco")]
    )

    submit = SubmitField("Submit")

    def validate(self, climber_id: int = None) -> bool:
        """
        - Check that the name and email are unique
        """
        is_valid = True
        if not super().validate():
            is_valid = False

        # check that the email is unique
        climber = Climber.query.filter(
            func.lower(Climber.email) == self.email.data.lower()
        ).first()
        if climber and climber.id != climber_id:
            self.email.errors.append("Email already in use")
            is_valid = False

        # check that the name is unique
        climber = Climber.query.filter(
            func.lower(Climber.name) == self.name.data.lower()
        ).first()
        if climber and climber.id != climber_id:
            self.name.errors.append("Name already in use")
            is_valid = False

        return is_valid

    @classmethod
    def create_from_obj(cls, climber) -> ClimberForm:
        """Create the form with data from the Climber object."""
        form = cls()
        for field in FIELDS:
            getattr(form, field).data = getattr(climber, field)
        return form

    def get_edited_obj(self, climber: Climber) -> Climber:
        """Edit the climber object with the data from the form."""
        for field in FIELDS:
            form_data = getattr(self, field).data
            if form_data == "":
                form_data = None
            setattr(climber, field, form_data)
        return climber
