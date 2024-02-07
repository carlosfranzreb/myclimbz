from climbz import db


class Area(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    rock_type_id = db.Column(db.Integer, db.ForeignKey("rock_type.id"))
    rock_type = db.relationship("RockType", backref="climbing_areas")
    sessions = db.relationship("Session", backref="area", cascade="all, delete")
    sectors = db.relationship("Sector", backref="area", cascade="all, delete")

    @property
    def n_routes(self) -> int:
        """Return the number of routes in all sectors of this area."""
        return sum(len(sector.routes) for sector in self.sectors)

    @property
    def n_sent_routes(self) -> int:
        """Return the number of sent routes in all sectors of this area."""
        return sum(sector.n_sent_routes for sector in self.sectors)
