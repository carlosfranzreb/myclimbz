"""
Represents a climber in the database. It is used to store the login information and
personal data of the user.

The `role` attribute is used to determine the permissions of the user. The options are:
    0: regular user: cannot delete routes or areas, nor edit routes or areas that they
        did not create
    1: admin: can edit and delete routes and areas
"""

from datetime import datetime

from flask_login import UserMixin

from climbz import db, login_manager
from climbz.models import Grade


# many-to-many relationship between climbers and routes, for storing projects
climber_projects = db.Table(
    "climber_projects",
    db.Column("climber_id", db.Integer, db.ForeignKey("climber.id")),
    db.Column("route_id", db.Integer, db.ForeignKey("route.id")),
)


class Climber(db.Model, UserMixin):

    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.Integer, nullable=False, default=0)

    # login information
    email = db.Column(db.String(200), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)

    # personal information
    name = db.Column(db.String(200), nullable=False)
    birthdate = db.Column(db.Date, nullable=True)
    year_started_climbing = db.Column(db.Integer, nullable=True)
    height = db.Column(db.Integer, nullable=True)
    ape_index = db.Column(db.Integer, nullable=True)

    # preferences
    grade_scale = db.Column(db.String(10), nullable=False, default="font")

    # relationships
    climbs = db.relationship("Climb", backref="climber", cascade="all, delete")
    sessions = db.relationship("Session", backref="climber", cascade="all, delete")
    opinions = db.relationship("Opinion", backref="climber", cascade="all, delete")
    routes = db.relationship("Route", backref="creator")
    sectors = db.relationship("Sector", backref="creator")
    areas = db.relationship("Area", backref="creator")
    projects = db.relationship(
        "Route",
        secondary=climber_projects,
        backref=db.backref("climbers", lazy="dynamic"),
    )

    @property
    def year_started_climbing_str(self) -> str:
        """Return the year the climber started climbing as a string."""
        if self.year_started_climbing is None:
            if self.sessions:
                return str(self.sessions[0].date.year)
            else:
                return "N/A"
        else:
            return str(self.year_started_climbing)

    @property
    def age_str(self) -> str:
        """Return the age of the climber as a string."""
        if self.birthdate is None:
            return "N/A"
        else:
            return str((datetime.now().date() - self.birthdate).days // 365)

    @property
    def max_grade(self) -> Grade:
        """Return the highest grade sent by the climber."""
        if not self.climbs or len(self.climbs) == 0:
            return None
        else:
            max_grade = Grade.query.filter_by(level=0).first()
            for climb in self.climbs:
                opinion = climb.route.opinion
                if opinion is not None and opinion.grade is not None:
                    if opinion.grade.level > max_grade.level:
                        max_grade = opinion.grade
            return max_grade

    @property
    def n_sends(self) -> int:
        """Return the number of routes sent by the climber, without repetitions."""
        sent_routes = list()
        for climb in self.climbs:
            if climb.sent and climb.route.id not in sent_routes:
                sent_routes.append(climb.route.id)
        return len(sent_routes)

    @property
    def favorite_areas(self) -> list[str]:
        """Return the 3 areas with the most sessions by the climber."""
        areas = dict()
        for session in self.sessions:
            if session.area.name in areas:
                areas[session.area.name] += 1
            else:
                areas[session.area.name] = 1
        areas = {
            k: v
            for k, v in sorted(areas.items(), key=lambda item: item[1], reverse=True)
        }
        favorite_areas = list(areas.keys())[:3]
        return favorite_areas

    def all_routes_as_dict(self) -> list[dict]:
        """
        Return all the routes the climber has tried or marked as projects as a list
        of dictionaries.
        """
        added_route_ids = list()
        routes = list()

        # add tried routes
        for climb in self.climbs:
            if climb.route.id not in added_route_ids:
                routes.append(climb.route.as_dict(self.id))
                added_route_ids.append(climb.route.id)

        # add projects
        for route in self.projects:
            if route.id not in added_route_ids:
                routes.append(route.as_dict(self.id))
                added_route_ids.append(route.id)

        return routes


@login_manager.user_loader
def load_climber(climber_id: int) -> Climber:
    """Required by the login manager, which uses it internally."""
    return Climber.query.get(int(climber_id))
