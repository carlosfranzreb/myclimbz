"""
Table for storing climber's ratings, grades, cruxes and media for routes.
"""

from sqlalchemy import UniqueConstraint

from myclimbz import db
from myclimbz.models.columns import Rating


crux_opinions = db.Table(
    "crux_opinions",
    db.Column("opinion_id", db.Integer, db.ForeignKey("opinion.id")),
    db.Column("crux_id", db.Integer, db.ForeignKey("crux.id")),
)


class Opinion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    route_id = db.Column(db.Integer, db.ForeignKey("route.id"))
    climber_id = db.Column(db.Integer, db.ForeignKey("climber.id"))
    grade_id = db.Column(db.Integer, db.ForeignKey("grade.id"))
    grade = db.relationship("Grade", backref="opinions")
    landing = Rating("landing")
    rating = Rating("rating")
    comment = db.Column(db.Text)
    cruxes = db.relationship(
        "Crux",
        secondary=crux_opinions,
        backref=db.backref("routes", lazy="dynamic"),
    )

    UniqueConstraint(route_id, climber_id, name="unique_opinion")
