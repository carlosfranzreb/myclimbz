from flask_wtf import FlaskForm
from wtforms import IntegerField, DateField, StringField, SubmitField, SelectField
from wtforms.validators import Optional

from climbs.models import Session


class SessionForm(FlaskForm):
    date = DateField("Date", validators=[Optional()])
    conditions = IntegerField("Conditions", validators=[Optional()])
    existing_area = SelectField("Existing Area", validators=[Optional()])
    new_area = StringField("New Area", validators=[Optional()])
    rock_type = SelectField("Rock Type of new area", validators=[Optional()])
    submit = SubmitField("Submit")

    def validate(self):
        """
        Ensure that only one of the new and existing fields is filled. Also ensure that
        the new field is not already in the database.
        """
        is_valid = True
        if not super().validate():
            is_valid = False

        error = check_exclusivity(
            Session,
            self.new_area.data,
            self.existing_area.data,
        )
        if error is not None:
            self.new_area.errors.append(error)
            is_valid = False

        return is_valid
