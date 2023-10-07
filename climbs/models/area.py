from climbs import db


class Area(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    rock_type_id = db.Cåolumn(db.Integer, db.ForeignKey("rock_type.id"))
    rock_type = db.relationship("RockType", backref="climbing_areas")
