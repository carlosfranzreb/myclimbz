from climbs import db


class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    conditions = db.Column(db.Integer, nullable=False)
    area_id = db.Column(db.Integer, db.ForeignKey("area.id"), nullable=False)
    area = db.relationship("Area", backref="sessions")
    climbs = db.relationship("Climb", backref="session", lazy=True)
