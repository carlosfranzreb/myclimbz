from myclimbz import db


class VideoAttempt(db.Model):
    db.Column("video_id", db.Integer, db.ForeignKey("video.id"))
    db.Column("start_frame_pred", db.Integer)
    db.Column("end_frame_pred", db.Integer)
    db.Column("start_frame", db.Integer)
    db.Column("end_frame", db.Integer)


class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(200), unique=True)
    climb_id = db.Column(db.Integer, db.ForeignKey("climb.id"))
    fps_video = db.Column(db.Integer)  # video's FPS, measured by cv2
    fps_taken = db.Column(db.Integer)  # FPS shown to the user for annotation
    attempts = db.relationship("VideoAttempt", backref="video", cascade="all, delete")
