from climbs import db


class Climb(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    n_attempts = db.Column(db.Integer)
    grade_felt_id = db.Column(db.Integer, db.ForeignKey("grade.id"))
    grade_felt = db.relationship("Grade", backref="climbs_felt")
    sent = db.Column(db.Boolean, nullable=False)
    route_id = db.Column(db.Integer, db.ForeignKey("route.id"))
    route = db.relationship("Route", backref="climbs")
    session_id = db.Column(db.Integer, db.ForeignKey("session.id"), nullable=False)
    session = db.relationship("Session", backref="climbs")
