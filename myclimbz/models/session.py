from datetime import datetime
from sqlalchemy import event, UniqueConstraint

from myclimbz import db
from myclimbz.models import Sector, Route, Climb
from myclimbz.models.columns import Rating


class Session(db.Model):
    __tablename__ = "climbing_session"
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, default=datetime.now().date())
    conditions = Rating("conditions")
    comment = db.Column(db.Text)
    climbs = db.relationship("Climb", backref="session", cascade="all, delete")
    area_id = db.Column(db.Integer, db.ForeignKey("area.id"))
    climber_id = db.Column(db.Integer, db.ForeignKey("climber.id"))

    UniqueConstraint(date, area_id, climber_id, name="unique_session")


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
