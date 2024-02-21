"""
Represents a climber in the database. It is used to store the login information and
personal data of the user.

The role attribute is used to determine the permissions of the user. The options are:
    0: regular user: cannot delete routes or areas, nor edit routes or areas that they
        did not create
    1: admin: can edit and delete routes and areas
"""

from flask_login import UserMixin

from climbz import db, login_manager


class Climber(db.Model, UserMixin):

    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.Integer, nullable=False, default=0)

    # login information
    email = db.Column(db.String(200), nullable=False)
    password = db.Column(db.String(200), nullable=False)

    # personal information
    name = db.Column(db.String(200), nullable=False)
    birthdate = db.Column(db.Date, nullable=True)
    years_climbing = db.Column(db.Integer, nullable=True)
    weight = db.Column(db.Float, nullable=True)
    height = db.Column(db.Float, nullable=True)
    ape_index = db.Column(db.Float, nullable=True)

    # relationships
    sessions = db.relationship("Session", backref="climber", cascade="all, delete")
    opinions = db.relationship("Opinion", backref="climber", cascade="all, delete")


@login_manager.user_loader
def load_climber(climber_id: int) -> Climber:
    """Required by the login manager, which uses it internally."""
    return Climber.query.get(int(climber_id))
