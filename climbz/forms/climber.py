from __future__ import annotations

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

from climbz.models import Climber


FIELDS = [
    "email",
    "name",
    "birthdate",
    "year_started_climbing",
    "weight",
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
    birthdate = DateField("Birthdate", validators=[Optional()])
    year_started_climbing = IntegerField("Years climbing", validators=[Optional()])
    weight = IntegerField("Weight (kg)", validators=[Optional()])
    height = IntegerField("Height (cm)", validators=[Optional()])
    ape_index = IntegerField("Ape index (cm)", validators=[Optional()])

    # preferences
    grade_scale = SelectField(
        "Preferred grading system", choices=[("font", "font"), ("hueco", "hueco")]
    )

    submit = SubmitField("Submit")

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
