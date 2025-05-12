from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, FileAllowed, FileField
from wtforms import IntegerField, FieldList, FormField
from wtforms.validators import DataRequired


ALLOWED_EXTS = ["mp4", "mov", "webm", "avi"]


class VideoAttemptForm(FlaskForm):
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


class VideosUploadForm(FlaskForm):
    videos = FieldList(FormField(VideoAttemptForm), min_entries=1)
