from climbz import db


class Predictions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    audiofile = db.Column(db.String(200), nullable=False)
    transcript = db.Column(db.String(3000), nullable=False)
    entities = db.Column(db.String(3000), nullable=False)
    area_id = db.Column(db.Integer, db.ForeignKey("area.id"), nullable=True)
    session_id = db.Column(db.Integer, db.ForeignKey("session.id"), nullable=True)
    route_id = db.Column(db.Integer, db.ForeignKey("route.id"), nullable=True)
    sector_id = db.Column(db.Integer, db.ForeignKey("sector.id"), nullable=True)
    climb_id = db.Column(db.Integer, db.ForeignKey("climb.id"), nullable=True)
