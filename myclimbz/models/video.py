from sqlalchemy import UniqueConstraint

from myclimbz import db


class VideoAttempt(db.Model):
    """
    Stores an attempt that has been annotated for a video.
    """

    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.Integer, db.ForeignKey("video.id"))
    attempt_number = db.Column(db.Integer, nullable=False)
    start = db.Column(db.Integer, nullable=False)
    end = db.Column(db.Integer, nullable=False)
    sent = db.Column(db.Boolean, nullable=False)
    UniqueConstraint(video_id, attempt_number, name="unique_attempt")


class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    base_fname = db.Column(db.String(200), unique=True, nullable=False)
    climb_id = db.Column(db.Integer, db.ForeignKey("climb.id"))
    attempts = db.relationship("VideoAttempt", backref="video", cascade="all, delete")
