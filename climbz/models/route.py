from climbz import db
from climbz.models.columns import ConstrainedInteger, Rating


route_crux_association = db.Table(
    "route_crux_association",
    db.Column("route_id", db.Integer, db.ForeignKey("route.id")),
    db.Column("crux_id", db.Integer, db.ForeignKey("crux.id")),
)


class Route(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)

    # route characteristics and ratings
    sit_start = db.Column(db.Boolean)
    height = db.Column(db.Float, db.CheckConstraint("height >= 0"))
    inclination = ConstrainedInteger("inclination", -20, 90)
    landing = Rating("landing")
    rating = Rating("rating")

    # grades
    grade_id = db.Column(db.Integer, db.ForeignKey("grade.id"))
    grade = db.relationship("Grade", foreign_keys=[grade_id], backref="routes")
    grade_felt_id = db.Column(db.Integer, db.ForeignKey("grade.id"), nullable=True)
    grade_felt = db.relationship(
        "Grade", foreign_keys=[grade_felt_id], backref="routes_felt"
    )

    # other relationships
    cruxes = db.relationship(
        "Crux",
        secondary=route_crux_association,
        backref=db.backref("routes", lazy="dynamic"),
    )
    sector_id = db.Column(db.Integer, db.ForeignKey("sector.id"))
    climbs = db.relationship("Climb", backref="route", cascade="all, delete")

    @property
    def sent(self) -> bool:
        """Whether this route has been sent."""
        return any(climb.sent for climb in self.climbs)

    def as_dict(self) -> dict:
        """
        Return the relevant attributes of this route as a dictionary, focusing on
        those that are relevant for analysis.
        """
        n_attempts_all, n_attempts_send, conditions, dates = 0, 0, list(), list()
        first_send = False
        for climb in self.climbs:
            n_attempts_all += climb.n_attempts
            if not first_send:
                n_attempts_send += climb.n_attempts
            first_send = first_send or climb.sent
            conditions.append(climb.session.conditions)
            dates.append(climb.session.date)

        return {
            "id": self.id,
            "name": self.name,
            "sector": self.sector.name,
            "area": self.sector.area.name,
            "level": self.grade.level,
            "level_felt": self.grade_felt.level if self.grade_felt else None,
            "height": self.height,
            "landing": self.landing,
            "inclination": self.inclination,
            "cruxes": [crux.name for crux in self.cruxes],
            "sent": self.sent,
            "n_sessions": len(self.climbs),
            "n_attempts_all": n_attempts_all,
            "n_attempts_send": n_attempts_send,
            "conditions": conditions,
            "dates": dates,
        }
