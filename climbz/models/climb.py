from climbz import db


class Climb(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    n_attempts = db.Column(db.Integer)
    sent = db.Column(db.Boolean, nullable=False)
    comment = db.Column(db.Text)
    route_id = db.Column(db.Integer, db.ForeignKey("route.id"))
    session_id = db.Column(db.Integer, db.ForeignKey("session.id"))