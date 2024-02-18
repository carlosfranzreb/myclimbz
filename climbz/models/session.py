from sqlalchemy import event

from climbz import db
from climbz.models import Sector, Route, Climb
from climbz.models.columns import Rating


class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    conditions = Rating("conditions")
    is_project_search = db.Column(db.Boolean, nullable=False, default=False)
    comment = db.Column(db.Text)
    climbs = db.relationship("Climb", backref="session", cascade="all, delete")
    area_id = db.Column(db.Integer, db.ForeignKey("area.id"))


@event.listens_for(Sector, "after_delete")
def after_sector_deletion(mapper, connection, target) -> None:
    """
    When a sector is deleted, delete any sessions with no climbs.
    """
    area = target.area
    for session in area.sessions:
        if not session.climbs:
            db.session.delete(session)


@event.listens_for(Route, "after_delete")
def after_route_deletion(mapper, connection, target) -> None:
    """
    When a route is deleted, delete any sessions with no climbs.
    """
    area = target.sector.area
    for session in area.sessions:
        if not session.climbs:
            db.session.delete(session)


@event.listens_for(Climb, "after_delete")
def after_climb_deletion(mapper, connection, target) -> None:
    """
    When a climb is deleted, delete any sessions with no climbs
    """
    session = Session.query.filter_by(id=target.session_id).first()
    if session and not session.climbs:
        db.session.delete(session)
