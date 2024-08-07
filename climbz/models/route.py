from collections import Counter

from flask_login import current_user
from sqlalchemy import UniqueConstraint

from climbz import db
from climbz.models import Grade, Opinion
from climbz.models.columns import ConstrainedInteger


class Route(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey("climber.id"), nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    comment = db.Column(db.Text)
    link = db.Column(db.String(300))

    # route characteristics
    sit_start = db.Column(db.Boolean, nullable=False, default=False)
    height = db.Column(db.Float, db.CheckConstraint("height >= 0"))
    inclination = ConstrainedInteger("inclination", -50, 90)

    # relationships
    sector_id = db.Column(db.Integer, db.ForeignKey("sector.id"))
    climbs = db.relationship("Climb", backref="route", cascade="all, delete")
    opinions = db.relationship("Opinion", backref="route", cascade="all, delete")

    UniqueConstraint("name", "sector_id", name="unique_route_name_in_sector")

    def sent_by(self, climber_id: int) -> bool:
        """Whether a climber has sent this route."""
        return any(
            climb.sent
            for climb in self.climbs
            if climb.session.climber_id == climber_id
        )

    @property
    def sent(self) -> bool:
        """Whether a climber has sent this route."""
        return any(
            climb.sent
            for climb in self.climbs
            if climb.session.climber_id == current_user.id
        )

    @property
    def tried(self) -> bool:
        """Whether a climber has tried this route."""
        return any(
            climb.n_attempts > 0
            for climb in self.climbs
            if climb.session.climber_id == current_user.id
        )

    @property
    def is_project(self) -> bool:
        """Whether the climber has marked this route as a project."""
        return self in current_user.projects

    @property
    def opinion(self):
        """The opinion of a climber about this route."""
        return Opinion.query.filter_by(
            route_id=self.id, climber_id=current_user.id
        ).first()

    @property
    def n_sends(self) -> int:
        """The number of climbers that have sent this route."""
        climbers = list()
        for climb in self.climbs:
            if climb.sent and climb.session.climber_id not in climbers:
                climbers.append(climb.session.climber_id)
        return len(climbers)

    @property
    def n_climbers(self) -> int:
        """The number of climbers that have tried this route."""
        climbers = list()
        for climb in self.climbs:
            if climb.session.climber_id not in climbers:
                climbers.append(climb.session.climber_id)
        return len(climbers)

    @property
    def consensus_level(self) -> int:
        """Most common given level to this route or null."""
        level_counts = Counter(op.grade.level for op in self.opinions if op.grade)
        return level_counts.most_common(1)[0][0] if level_counts else None

    @property
    def consensus_grade(self) -> Grade:
        """The `consensus_level` as a grade object"""
        return Grade.query.filter_by(level=self.consensus_level).first()

    @property
    def consensus_grade_str(self) -> str:
        """The `consensus_grade`, as displayed by the user."""
        grade_scale = current_user.grade_scale
        return getattr(self.consensus_grade, grade_scale)

    @property
    def grade(self) -> Grade:
        """
        The grade of this route according to the climber. If the climber has not
        given an opinion, return the consensus grade.
        """
        return self.opinion.grade if self.opinion else self.consensus_grade

    @property
    def rating(self) -> float:
        """The average rating given to this route."""
        ratings = [op.rating for op in self.opinions if op.rating is not None]
        return sum(ratings) / len(ratings) if ratings else None

    @property
    def landing(self) -> float:
        """The average landing rating given to this route."""
        landings = [op.landing for op in self.opinions if op.landing is not None]
        return sum(landings) / len(landings) if landings else None

    @property
    def cruxes(self) -> list:
        """The 3 most common cruxes given to this route."""
        crux_counts = Counter(crux.name for op in self.opinions for crux in op.cruxes)
        return [crux[0] for crux in crux_counts.most_common(3)]

    def n_sessions_str(self, climber_id: int) -> str:
        """Return the number of sessions a climber has spent on this route."""
        n_sessions = str(
            len([1 for climb in self.climbs if climb.session.climber_id == climber_id])
        )
        if n_sessions == "1":
            return "1 session"
        else:
            return f"{n_sessions} sessions"

    def last_media(self, climber_id: int) -> str:
        """Return the last media URL of this climber on this route."""
        climbs = [
            climb for climb in self.climbs if climb.session.climber_id == climber_id
        ]
        sorted_climbs = sorted(climbs, key=lambda climb: climb.session.date)
        if not sorted_climbs:
            return "N/A"
        elif not sorted_climbs[-1].link:
            return "N/A"
        else:
            sorted_climbs[-1].link

    def as_dict(self, climber_id: int) -> dict:
        """
        Return the relevant attributes of this route for a climber as a dictionary,
        focusing on those that are relevant for analysis.
        """
        n_sessions, n_attempts_all, n_attempts_send = 0, 0, 0
        conditions, dates = list(), list()
        first_send = False
        sorted_climbs = sorted(self.climbs, key=lambda climb: climb.session.date)
        for climb in sorted_climbs:
            if climb.session.climber_id != climber_id:
                continue
            n_attempts = climb.n_attempts if climb.n_attempts is not None else 0
            n_attempts_all += n_attempts
            if not first_send:
                n_attempts_send += n_attempts
                n_sessions += 1
            first_send = first_send or climb.sent
            conditions.append(climb.session.conditions)
            dates.append(climb.session.date)

        level_mine = None
        if self.opinion and self.opinion.grade:
            level_mine = self.opinion.grade.level

        return {
            # route characteristics
            "id": self.id,
            "name": self.name,
            "sector": self.sector.name,
            "area": self.sector.area.name,
            "level_consensus": self.consensus_level,
            "height": self.height,
            "inclination": self.inclination,
            "sit_start": self.sit_start,
            # climber's relationship to the route
            "tried": self.tried,
            "project": self.is_project,
            "sent": self.sent,
            # climber's opinion
            "landing": self.opinion.landing if self.opinion else None,
            "rating": self.opinion.rating if self.opinion else None,
            "level_mine": level_mine,
            "cruxes": (
                [crux.name for crux in self.opinion.cruxes] if self.opinion else None
            ),
            # climbing history
            "n_sessions": n_sessions,
            "n_attempts_all": n_attempts_all,
            "n_attempts_send": n_attempts_send,
            "conditions": conditions,
            "dates": dates,
            # level to be displayed
            "level": self.grade.level if self.grade else None,
        }
