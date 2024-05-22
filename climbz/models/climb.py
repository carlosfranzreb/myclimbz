from climbz import db


class Climb(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    n_attempts = db.Column(db.Integer, default=0)
    sent = db.Column(db.Boolean, nullable=False)
    flashed = db.Column(db.Boolean, nullable=False)
    comment = db.Column(db.Text)
    link = db.Column(db.String(300))
    climber_id = db.Column(db.Integer, db.ForeignKey("climber.id"))
    route_id = db.Column(db.Integer, db.ForeignKey("route.id"))
    session_id = db.Column(db.Integer, db.ForeignKey("session.id"))
    # TODO: climber_id is not needed, as it can be derived from session
