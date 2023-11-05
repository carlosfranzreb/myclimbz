from flask_wtf import FlaskForm
from wtforms import IntegerField, DateField, StringField, SelectField
from wtforms.validators import Optional

from climbs.models import RockType


class SessionForm(FlaskForm):
    date = DateField("Date", validators=[Optional()])
    conditions = IntegerField("Conditions", validators=[Optional()])
    area = StringField("Area name", validators=[Optional()])
    rock_type = SelectField("Rock Type of new area", validators=[Optional()])

    def add_choices(self):
        """Add choices to select fields: rock types."""
        self.rock_type.choices = [(0, "")] + [
            (r.id, r.name) for r in RockType.query.all()
        ]
