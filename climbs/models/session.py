from climbs import db


class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    conditions = db.Column(db.Integer)
    is_project_search = db.Column(db.Boolean, nullable=False, default=False)
    area_id = db.Column(db.Integer, db.ForeignKey("area.id"), nullable=False)
    area = db.relationship("Area", backref="sessions")
