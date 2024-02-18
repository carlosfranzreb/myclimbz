"""
Table for storing climber's ratings, grades, cruxes and media for routes.
"""

from climbz import db
from climbz.models.columns import Rating


route_crux_association = db.Table(
    "route_crux_association",
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
    link = db.Column(db.String(300))  # link to a photo or video
    cruxes = db.relationship(
        "Crux",
        secondary=route_crux_association,
        backref=db.backref("routes", lazy="dynamic"),
    )
