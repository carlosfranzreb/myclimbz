from sqlalchemy import event

from climbz import db
from climbz.models import Route


class Sector(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey("climber.id"), nullable=False)
    area_id = db.Column(db.Integer, db.ForeignKey("area.id"))
    routes = db.relationship("Route", backref="sector", cascade="all, delete")
    comment = db.Column(db.Text)

    def n_sent_routes(self, climber_id: int) -> int:
        """Return the number of sent routes in this sector by a climber."""
        return sum(route.sent(climber_id) for route in self.routes)


@event.listens_for(Route, "after_delete")
def after_sector_deletion(mapper, connection, target) -> None:
    """
    When a route is deleted, delete its sector as well if it has no routes left.
    """
    sector = target.sector
    if not sector.routes:
        db.session.delete(sector)
