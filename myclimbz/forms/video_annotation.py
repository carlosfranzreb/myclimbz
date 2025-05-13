from flask import session as flask_session
from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, FileAllowed, FileField
from wtforms import FieldList, FormField, IntegerField
from wtforms.validators import DataRequired


ALLOWED_EXTS = ["mp4", "mov", "webm", "avi"]


class VideoSectionForm(FlaskForm):
    start = IntegerField("Start", validators=[DataRequired()])
    end = IntegerField("End", validators=[DataRequired()])
    file = FileField(
        "File",
        validators=[
            FileRequired(),
            FileAllowed(
                ALLOWED_EXTS, f"Only videos are allowed: {', '.join(ALLOWED_EXTS)}"
            ),
        ],
    )

    def validate(self):
        if not super(VideoSectionForm, self).validate():
            return False
        if self.start.data > self.end.data:
            error_msg = "'Start' must be smaller than 'End'."
            self.start.errors.append(error_msg)
            flask_session["error"] = error_msg
            return False
        return True


class VideoAnnotationForm(FlaskForm):
    sections = FieldList(FormField(VideoSectionForm), min_entries=1)
