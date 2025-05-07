import os

from sqlalchemy import UniqueConstraint

from myclimbz import db


class Climb(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    n_attempts = db.Column(db.Integer, default=0)
    sent = db.Column(db.Boolean, nullable=False)
    flashed = db.Column(db.Boolean, nullable=False)
    comment = db.Column(db.Text)
    link = db.Column(db.String(300))
    route_id = db.Column(db.Integer, db.ForeignKey("route.id"))
    session_id = db.Column(db.Integer, db.ForeignKey("climbing_session.id"))
    videos = db.relationship("Video", backref="climb", cascade="all, delete")

    UniqueConstraint(route_id, session_id, name="unique_route_in_session")

    @property
    def climber_id(self):
        return self.session.climber_id

    @property
    def climb_videos(self) -> list[dict[str]]:
        """
        Returns this climb's videos, as expected by the `video_manager` macro.
        """

        # return empty if empty
        if len(self.videos) == 0:
            return list()

        out = list()
        session_attempts = 0
        for video in self.videos:

            # iterate over attempts and store video information
            base, ext = os.path.splitext(video.fname)
            for attempt_idx, attempt in enumerate(video.attempts):
                attempt_video = (
                    f"{base}_trim{attempt.start_frame}-{attempt.end_frame}{ext}"
                )
                out.append(
                    {
                        "attempt_number": session_attempts + attempt_idx + 1,
                        "attempt_video": attempt_video,
                    }
                )

            # update attempt counter and last session ID
            session_attempts += len(video.attempts)

        return out[::-1]
