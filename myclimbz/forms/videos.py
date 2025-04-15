from flask import session as flask_session
from flask_wtf import FlaskForm
from flask_wtf.file import MultipleFileField, FileRequired, FileAllowed


ALLOWED_EXTS = ["mp4", "mov", "webm", "avi"]


class VideosForm(FlaskForm):
    videos = MultipleFileField(
        validators=[
            FileRequired(),
            FileAllowed(
                ALLOWED_EXTS, f"Only videos are allowed: {', '.join(ALLOWED_EXTS)}"
            ),
        ],
    )

    def validate(self) -> bool:
        is_valid = True
        if not super().validate():
            flask_session["error"] = self.videos.errors[0]
            is_valid = False

        return is_valid
