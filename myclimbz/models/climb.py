from sqlalchemy import UniqueConstraint

from myclimbz import db


class Climb(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    n_attempts = db.Column(db.Integer, default=0)
    sent = db.Column(db.Boolean, nullable=False)
    flashed = db.Column(db.Boolean, nullable=False)
    comment = db.Column(db.Text)
    link = db.Column(db.String(300))
    route_id = db.Column(db.Integer, db.ForeignKey("route.id"))
    session_id = db.Column(db.Integer, db.ForeignKey("climbing_session.id"))
    videos = db.relationship("Video", backref="climb", cascade="all, delete")

    UniqueConstraint(route_id, session_id, name="unique_route_in_session")

    @property
    def climber_id(self):
        return self.session.climber_id
