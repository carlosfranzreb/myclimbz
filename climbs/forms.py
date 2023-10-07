from flask_wtf import FlaskForm
from wtforms import SubmitField
from flask_wtf.file import FileField, FileRequired, FileAllowed


class FileForm(FlaskForm):
    file = FileField(validators=[FileRequired(), FileAllowed(["csv"])])
    submit = SubmitField("Submit")
