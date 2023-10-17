from climbs import db


route_crux_association = db.Table(
    "route_crux_association",
    db.Column("route_id", db.Integer, db.ForeignKey("route.id")),
    db.Column("crux_id", db.Integer, db.ForeignKey("crux.id")),
)


class Route(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    grade_id = db.Column(db.Integer, db.ForeignKey("grade.id"))
    grade = db.relationship("Grade", backref="routes")
    height = db.Column(db.Integer)
    landing = db.Column(db.Integer)
    inclination = db.Column(db.Integer)
    sector_id = db.Column(db.Integer, db.ForeignKey("sector.id"))
    sector = db.relationship("Sector", backref="routes")
    cruxes = db.relationship(
        "Crux",
        secondary=route_crux_association,
        backref=db.backref("routes", lazy="dynamic"),
    )

    @property
    def sent(self) -> bool:
        """Whether this route has been sent."""
        return any(climb.sent for climb in self.climbs)

    def as_dict(self) -> dict:
        """
        Return the relevant attributes of this route as a dictionary, focusing on
        those that are relevant for analysis.
        """
        n_attempts, conditions, dates, grade_felt = 0, list(), list(), list()
        for climb in self.climbs:
            n_attempts += climb.n_attempts
            conditions.append(climb.session.conditions)
            dates.append(climb.session.date)
            grade_felt.append(climb.grade_felt.font if climb.grade_felt else None)

        return {
            "name": self.name,
            "sector": self.sector.name,
            "area": self.sector.area.name,
            "font": self.grade.font,
            "hueco": self.grade.hueco,
            "level": self.grade.level,
            "height": self.height,
            "landing": self.landing,
            "inclination": self.inclination,
            "cruxes": [crux.name for crux in self.cruxes],
            "sent": self.sent,
            "n_sessions": len(self.climbs),
            "n_attempts": n_attempts,
            "conditions": conditions,
            "dates": dates,
            "grade_felt": grade_felt,
        }
