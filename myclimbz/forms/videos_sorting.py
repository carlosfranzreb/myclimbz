from flask_wtf import FlaskForm
from wtforms import FieldList, StringField


class VideosSortingForm(FlaskForm):
    videos_sorted = FieldList(StringField("Video"), min_entries=0)

    def __init__(self, n_videos: int = 1, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.videos_sorted.min_entries = n_videos
        self.videos_sorted.max_entries = n_videos

        # add new entries if needed
        missing = n_videos - len(self.videos_sorted.entries)
        for _ in range(missing):
            self.videos_sorted.append_entry()

        # TODO: do I need to remove entries?
