from climbs import db


class Sector(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    area_id = db.Column(db.Integer, db.ForeignKey("area.id"), nullable=False)
    area = db.relationship("Area", backref="sectors")

    @property
    def n_sent_routes(self) -> int:
        """Return the number of sent routes in this sector."""
        return sum(route.sent for route in self.routes)
