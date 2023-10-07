from climbs import db


class Area(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    rock_type = db.Column(db.String(50), nullable=False)
