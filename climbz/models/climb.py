from climbz import db


class Climb(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    n_attempts = db.Column(db.Integer)
    sent = db.Column(db.Boolean, nullable=False)
    route_id = db.Column(db.Integer, db.ForeignKey("route.id"))
    route = db.relationship("Route", backref="climbs")
    session_id = db.Column(db.Integer, db.ForeignKey("session.id"), nullable=False)
    session = db.relationship("Session", backref="climbs")
