import os
from time import time

from flask import (
    Blueprint,
    redirect,
    request,
    session as flask_session,
    current_app,
    send_from_directory,
    abort,
    url_for,
)
from flask_login import current_user
from werkzeug.utils import secure_filename

from myclimbz.models import Video, VideoAttempt
from myclimbz.forms import VideosForm, VideosSortingForm, VideoAnnotationForm
from myclimbz import db
from myclimbz.blueprints.utils import render
from myclimbz.blueprints.videos.utils import (
    check_access_to_file,
    get_video_frames,
    trim_video,
)

videos = Blueprint("videos", __name__)


@videos.route("/add_videos", methods=["GET", "POST"])
def add_videos() -> str:
    """
    Provides a form for the user to upload one or multiple videos.
    When the user clicks "Save", the user is sent to the page where videos are sorted
    (see `sort_videos`).
    """
    # create forms and add choices
    title = "Add videos"
    form = VideosForm()
    session_id = flask_session["session_id"]

    # POST: form was submitted => add videos or return error
    if request.method == "POST":
        if not form.validate():
            if flask_session.get("error", None) is None:
                flask_session["error"] = "An error occurred. Fix it and resubmit."

        # upload videos
        else:
            fnames = list()
            timestamp = int(time())
            for f_idx, f in enumerate(form.videos.data):
                f_ext = os.path.splitext(f.filename)[1]
                fnames.append(
                    secure_filename(
                        f"{current_user.id}_{session_id}_{timestamp}_added-{f_idx}{f_ext}"
                    )
                )
                f.save(os.path.join(current_app.config["VIDEOS_FOLDER"], fnames[-1]))

            flask_session["video_fnames"] = fnames
            return redirect("/sort_videos")

    # GET: the user wants to upload videos
    return render("form.html", title=title, forms=[form], enctype="multipart/form-data")


@videos.route("/sort_videos", methods=["GET", "POST"])
def sort_videos() -> str:
    """
    The user can sort the videos chronologically and is then sent to `process_videos`.
    TODO: display frames instead of videos, and allow user to navigate them.
    """

    videos = sorted(flask_session["video_fnames"])
    check_access_to_file(videos[0])

    # if there is only one video, skip this and go to process_videos
    if len(videos) == 1:
        flask_session["video_fnames"] = videos
        return redirect(url_for("videos.annotate_video", n_videos=1, video_idx=0))

    # create the form for sorting the videos
    title = "Sort videos"
    form = VideosSortingForm(n_videos=len(videos))

    # POST: the form was submitted => sort videos or return error
    if request.method == "POST":
        if not form.validate():
            if flask_session.get("error", None) is None:
                flask_session["error"] = form.videos_sorted.errors[0]

        # rename the videos according to the given order
        else:
            for f_idx in range(len(videos)):
                f = videos[f_idx]
                fname, ext = os.path.splitext(videos[f_idx])
                f_sort_idx = form.videos_sorted.data.index(f)
                f_new = secure_filename(
                    f"{fname.rsplit('_', 1)[0]}_sorted-{f_sort_idx}{ext}"
                )
                os.rename(
                    os.path.join(current_app.config["VIDEOS_FOLDER"], f),
                    os.path.join(current_app.config["VIDEOS_FOLDER"], f_new),
                )
                videos[f_idx] = f_new

            flask_session["video_fnames"] = videos
            return redirect(
                url_for("videos.annotate_video", n_videos=len(videos), video_idx=0)
            )

    return render("form_sort_videos.html", title=title, form=form, videos=videos)


@videos.route(
    "/annotate_video/<int:n_videos>/<int:video_idx>",
    methods=["GET", "POST"],
)
def annotate_video(n_videos: int, video_idx: int) -> str:
    """
    The user is shown a video and is asked to mark the portions of each video where
    there is climbing. Only the marked will be saved. The number of attempts is inferred
    from the marked portions.

    Afterwards, the user is sent to `add_climb` to fill in route information. And after
    that, if there are more videos, the user is sent back here to annotate the next video.
    """

    # create title, frames and form
    video_fname = sorted(flask_session["video_fnames"])[video_idx]
    check_access_to_file(video_fname)

    video_path = os.path.join(current_app.config["VIDEOS_FOLDER"], video_fname)
    frames_fname_prefix, n_frames, fps_video, fps_taken = get_video_frames(video_path)
    title = "Annotate"
    form = VideoAnnotationForm()
    flask_session["video_upload_status"] = [video_idx, n_videos]

    # POST: user submitted annotations
    if request.method == "POST":
        if not form.validate():
            if flask_session.get("error", None) is None:
                flask_session["error"] = "An error occurred. Fix it and resubmit."

        else:
            # store video annotations and trim video
            video_obj = Video(
                fname=video_fname, fps_video=fps_video, fps_taken=fps_taken
            )
            for section in form.sections.data:
                video_obj.attempts.append(
                    VideoAttempt(start_frame=section["start"], end_frame=section["end"])
                )
                trim_video(video_obj, section["start"], section["end"])

            db.session.add(video_obj)
            db.session.commit()
            os.remove(video_path)

            # go to "Add climb" form
            flask_session["video_id"] = video_obj.id
            return redirect(url_for("climbs.add_climb"))

    # GET: the user wants to upload videos
    return render(
        "form_annotate_video.html",
        title=title,
        form=form,
        frames_fname_prefix=frames_fname_prefix,
        n_frames=n_frames,
    )


@videos.route("/files/<filetype>/<filename>")
def serve_file(filetype: str, filename: str):
    """
    Serves files from the UPLOAD_FOLDER.
    TODO: protect access to videos in __init__.py, where all access rights are handled.
    """
    check_access_to_file(filename, ignore_session=True)

    if filetype == "videos":
        folder = current_app.config["VIDEOS_FOLDER"]
    elif filetype == "frames":
        folder = current_app.config["FRAMES_FOLDER"]
    else:
        abort(404)

    try:
        return send_from_directory(folder, filename)
    except FileNotFoundError:
        abort(404)
