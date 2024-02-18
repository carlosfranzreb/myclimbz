from flask_login import UserMixin

from climbz import db, login_manager


def load_user(user_id):
    """Required by the login manager, which uses it internally."""
    return Climber.query.get(int(user_id))


class Climber(db.Model):
    # login information
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(200), nullable=False)
    password = db.Column(db.String(200), nullable=False)

    # personal information
    name = db.Column(db.String(200), nullable=False)
    birthdate = db.Column(db.Date, nullable=True)
    years_climbing = db.Column(db.Integer, nullable=True)
    weight = db.Column(db.Float, nullable=True)
    height = db.Column(db.Float, nullable=True)
    ape_index = db.Column(db.Float, nullable=True)

    sessions = db.relationship("Session", backref="climber", cascade="all, delete")
