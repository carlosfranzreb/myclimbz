from myclimbz import db


class VideoAttempt(db.Model):
    """
    Stores an attempt that has been annotated for a video.
    """

    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.Integer, db.ForeignKey("video.id"))
    start_frame_pred = db.Column(db.Integer)
    end_frame_pred = db.Column(db.Integer)
    start_frame = db.Column(db.Integer)
    end_frame = db.Column(db.Integer)


class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(200), unique=True)
    climb_id = db.Column(db.Integer, db.ForeignKey("climb.id"))
    fps_video = db.Column(db.Integer)  # video's FPS, measured by cv2
    fps_taken = db.Column(db.Integer)  # FPS shown to the user for annotation
    attempts = db.relationship("VideoAttempt", backref="video", cascade="all, delete")
