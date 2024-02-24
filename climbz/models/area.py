from sqlalchemy import event

from climbz import db
from climbz.models import Sector


class Area(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey("climber.id"), nullable=False)
    rock_type_id = db.Column(db.Integer, db.ForeignKey("rock_type.id"))
    rock_type = db.relationship("RockType", backref="climbing_areas")
    sessions = db.relationship("Session", backref="area", cascade="all, delete")
    sectors = db.relationship("Sector", backref="area", cascade="all, delete")

    @property
    def n_routes(self) -> int:
        """Return the number of routes in all sectors of this area."""
        return sum(len(sector.routes) for sector in self.sectors)

    def n_sent_routes(self, climber_id: int) -> int:
        """Return the number of sent routes in all sectors of this area by a climber."""
        return sum(sector.n_sent_routes(climber_id) for sector in self.sectors)


@event.listens_for(Sector, "after_delete")
def after_sector_deletion(mapper, connection, target) -> None:
    """
    When a sector is deleted, delete the area as well if it has no sectors left.
    """
    area = target.area
    if not area.sectors:
        db.session.delete(area)
