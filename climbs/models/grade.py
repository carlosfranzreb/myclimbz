from climbs import db


class Grade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    level = db.Column(db.Integer, nullable=False)
    font = db.Column(db.String(10), nullable=False)
    hueco = db.Column(db.String(10), nullable=False)

    def as_dict(self) -> dict:
        """Return the relevant attributes of this grade as a dictionary."""
        return {
            "level": self.level,
            "font": self.font,
            "hueco": self.hueco,
        }
