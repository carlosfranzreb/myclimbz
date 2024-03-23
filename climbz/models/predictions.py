from climbz import db


class Predictions(db.Model):

    # required columns
    id = db.Column(db.Integer, primary_key=True)
    audiofile = db.Column(db.String(200), nullable=False)
    transcript = db.Column(db.String(3000), nullable=False)
    entities = db.Column(db.String(3000), nullable=False)
    climber_id = db.Column(db.Integer, db.ForeignKey("climber.id"), nullable=False)

    # optional columns
    area_id = db.Column(db.Integer, db.ForeignKey("area.id"), nullable=True)
    session_id = db.Column(db.Integer, db.ForeignKey("session.id"), nullable=True)
    route_id = db.Column(db.Integer, db.ForeignKey("route.id"), nullable=True)
    sector_id = db.Column(db.Integer, db.ForeignKey("sector.id"), nullable=True)
    climb_id = db.Column(db.Integer, db.ForeignKey("climb.id"), nullable=True)
