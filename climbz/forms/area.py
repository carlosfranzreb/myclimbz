from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField, StringField
from wtforms.validators import Optional

from climbz.models import RockType


class AreaForm(FlaskForm):
    name = StringField("Area name", validators=[Optional()])
    rock_type = SelectField("Rock Type", validators=[Optional()])
    submit = SubmitField("Submit")

    def add_choices(self):
        """Add choices to select fields: rock types."""
        self.rock_type.choices = [(0, "")] + [
            (r.id, r.name) for r in RockType.query.all()
        ]
