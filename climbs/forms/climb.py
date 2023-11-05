from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField, BooleanField
from wtforms.validators import Optional


class ClimbForm(FlaskForm):
    # the route is determined in the route form
    is_project = BooleanField("Project (not climbed yet)", validators=[Optional()])
    n_attempts = IntegerField("Number of attempts", validators=[Optional()])
    sent = BooleanField("Sent", validators=[Optional()])
    submit = SubmitField("Submit")
