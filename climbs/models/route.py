from climbs import db


route_crux_association = db.Table(
    "route_crux_association",
    db.Column("route_id", db.Integer, db.ForeignKey("route.id")),
    db.Column("crux_id", db.Integer, db.ForeignKey("crux.id")),
)


class Route(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    grade_id = db.Column(db.Integer, db.ForeignKey("grade.id"))
    grade = db.relationship("Grade", backref="routes")
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
