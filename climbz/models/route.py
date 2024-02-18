from collections import Counter

from climbz import db
from climbz.models.columns import ConstrainedInteger


class Route(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)

    # route characteristics
    sit_start = db.Column(db.Boolean)
    height = db.Column(db.Float, db.CheckConstraint("height >= 0"))
    inclination = ConstrainedInteger("inclination", -20, 90)

    # grades
    grade_id = db.Column(db.Integer, db.ForeignKey("grade.id"))
    grade = db.relationship("Grade", foreign_keys=[grade_id], backref="routes")

    # other relationships
    sector_id = db.Column(db.Integer, db.ForeignKey("sector.id"))
    climbs = db.relationship("Climb", backref="route", cascade="all, delete")
    opinions = db.relationship("Opinion", backref="route", cascade="all, delete")

    def sent(self, climber_id: int) -> bool:
        """Whether a climber has sent this route."""
        return any(
            climb.sent
            for climb in self.climbs
            if climb.session.climber_id == climber_id
        )

    def as_dict(self, climber_id: int) -> dict:
        """
        Return the relevant attributes of this route for a climber as a dictionary,
        focusing on those that are relevant for analysis.
        """
        n_sessions, n_attempts_all, n_attempts_send = 0, 0, 0
        conditions, dates = list(), list()
        first_send = False
        for climb in self.climbs:
            if climb.session.climber_id != climber_id:
                continue
            n_sessions += 1
            n_attempts_all += climb.n_attempts
            if not first_send:
                n_attempts_send += climb.n_attempts
            first_send = first_send or climb.sent
            conditions.append(climb.session.conditions)
            dates.append(climb.session.date)

        opinion = None
        level_counts = Counter()
        for op in self.opinions:
            if op.climber_id == climber_id:
                opinion = op
            level_counts[op.grade.level] += 1
        consensus_level = level_counts.most_common(1)[0][0] if level_counts else None

        return {
            "id": self.id,
            "name": self.name,
            "sector": self.sector.name,
            "area": self.sector.area.name,
            "level": consensus_level,
            "level_felt": opinion.grade.level,
            "height": self.height,
            "landing": self.landing,
            "inclination": self.inclination,
            "cruxes": [crux.name for crux in opinion.cruxes],
            "sent": self.sent(climber_id),
            "n_sessions": n_sessions,
            "n_attempts_all": n_attempts_all,
            "n_attempts_send": n_attempts_send,
            "conditions": conditions,
            "dates": dates,
        }
