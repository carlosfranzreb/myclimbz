from climbz import db


class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    conditions = db.Column(db.Integer)
    is_project_search = db.Column(db.Boolean, nullable=False, default=False)
    climbs = db.relationship("Climb", backref="session", cascade="all, delete")
    area_id = db.Column(db.Integer, db.ForeignKey("area.id"))
