from climbs import db


route_crux_association = db.Table(
    "route_crux_association",
    db.Column("route_id", db.Integer, db.ForeignKey("route.id")),
    db.Column("crux_id", db.Integer, db.ForeignKey("crux.id")),
)


class Route(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    sit_start = db.Column(db.Boolean)
    grade_id = db.Column(db.Integer, db.ForeignKey("grade.id"))
    grade = db.relationship("Grade", foreign_keys=[grade_id], backref="routes")
    grade_felt_id = db.Column(db.Integer, db.ForeignKey("grade.id"), nullable=True)
    grade_felt = db.relationship(
        "Grade", foreign_keys=[grade_felt_id], backref="routes_felt"
    )
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
