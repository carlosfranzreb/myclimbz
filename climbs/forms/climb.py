from flask_wtf import FlaskForm
from wtforms import (
    IntegerField,
    StringField,
    SubmitField,
    SelectField,
    FloatField,
    BooleanField,
    SelectMultipleField,
)
from wtforms.validators import Optional

from climbs.forms.check_exclusive import check_exclusivity
from climbs.models import Route, Sector, Grade


class ClimbForm(FlaskForm):
    existing_route = SelectField("Existing route", validators=[Optional()])
    new_route = StringField("New route", validators=[Optional()])
    existing_sector = SelectField("Existing sector", validators=[Optional()])
    new_sector = StringField("New sector", validators=[Optional()])
    n_attempts = IntegerField("Number of attempts", validators=[Optional()])
    sent = BooleanField("Sent", validators=[Optional()])

    # fields for new route
    grade = SelectField("Grade", validators=[Optional()])
    grade_felt = SelectField("Grade felt", validators=[Optional()])
    height = FloatField("Height", validators=[Optional()])
    inclination = IntegerField("Inclination", validators=[Optional()])
    landing = IntegerField("Landing", validators=[Optional()])
    sit_start = BooleanField("Sit Start", validators=[Optional()])
    cruxes = SelectMultipleField("Cruxes", validators=[Optional()])

    submit = SubmitField("Submit")

    def validate(self):
        """
        Ensure that only one of the new and existing fields is filled. Also ensure that
        the new field is not already in the database. If the form is valid, change the
        grades to their objects.
        """
        is_valid = True
        if not super().validate():
            is_valid = False

        error = check_exclusivity(
            Route,
            self.new_route.data,
            self.existing_route.data,
        )
        if error is not None:
            self.new_route.errors.append(error)
            is_valid = False

        error = check_exclusivity(
            Sector, self.new_sector.data, self.existing_sector.data
        )
        if error is not None:
            self.new_sector.errors.append(error)
            is_valid = False

        # if is_valid, change the grades to their objects
        if is_valid:
            for field in ["grade", "grade_felt"]:
                getattr(self, field).data = Grade.query.get(getattr(self, field).data)

        return is_valid
