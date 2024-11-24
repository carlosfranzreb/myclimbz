from flask_login import current_user

from myclimbz import db


class Grade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    level = db.Column(db.Integer, nullable=False)
    font = db.Column(db.String(10), nullable=False)
    hueco = db.Column(db.String(10), nullable=False)

    @property
    def user_grade(self) -> str:
        """Return the grade in the user's preferred scale."""
        return self.font if current_user.grade_scale == "font" else self.hueco

    def as_dict(self) -> dict:
        """Return the relevant attributes of this grade as a dictionary."""
        return {
            "level": self.level,
            "font": self.font,
            "hueco": self.hueco,
            "user_grade_scale": self.user_grade,
        }
