from flask_wtf import FlaskForm
from wtforms import IntegerField, DateField, StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, Optional


class SessionForm(FlaskForm):
    date = DateField("Date", validators=[DataRequired()])
    conditions = IntegerField("Conditions", validators=[DataRequired()])
    existing_area = SelectField("Existing Area", validators=[Optional()])
    new_area = StringField("New Area", validators=[Optional()])
    rock_type = SelectField("Rock Type of new area", validators=[Optional()])
    submit = SubmitField("Submit")
