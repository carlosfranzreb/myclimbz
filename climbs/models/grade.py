from climbs import db


class Grade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    level = db.Column(db.Integer, nullable=False)
    french = db.Column(db.String(10), nullable=False)
    hueco = db.Column(db.String(10), nullable=False)
