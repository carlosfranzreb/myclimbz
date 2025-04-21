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
import cv2

from myclimbz.models import Video, VideoAttempt
from myclimbz.forms import VideosForm, VideosSortingForm, VideoAnnotationForm
from myclimbz import db
from myclimbz.blueprints.utils import render


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

    frames_fname_prefix, n_frames, fps_video, fps_taken = get_video_frames(
        os.path.join(current_app.config["VIDEOS_FOLDER"], video_fname)
    )
    title = "Annotate"
    form = VideoAnnotationForm()
    flask_session["video_upload_status"] = [video_idx, n_videos]

    # POST: user submitted annotations
    if request.method == "POST":
        if not form.validate():
            if flask_session.get("error", None) is None:
                flask_session["error"] = "An error occurred. Fix it and resubmit."

        else:
            # store video annotations
            video_obj = Video(
                fname=video_fname, fps_video=fps_video, fps_taken=fps_taken
            )
            for section in form.sections.data:
                video_obj.attempts.append(
                    VideoAttempt(start_frame=section["start"], end_frame=section["end"])
                )
            db.session.add(video_obj)
            db.session.commit()

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
    check_access_to_file(filename)

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


def check_access_to_file(filename: str, ignore_session: bool = False):
    """
    Check that the user is the owner of the videos, and that the session of the videos
    is currently open.
    TODO: this may belong in __init__.py, where all access rights are handled.

    Args:
        filename as a string. It is expected to define the user id and the session id
        as the first two elements of the name, separated by underscores.
    """
    user_id, session_id = [int(n) for n in filename.split("_", 2)[:2]]

    if current_user.id != user_id:
        flask_session["error"] = "You are not the owner of this file."
        abort(403)

    if not ignore_session and session_id != flask_session["session_id"]:
        flask_session["error"] = (
            "The session is closed. Redirecting to the session's page."
        )
        return redirect(url_for("sessions.page_session", session_id=session_id))


def get_video_frames(video_path: str, fps: int = 2) -> tuple[str, int, int, int]:
    """
    - Extract and dump `fps` frames per second from the video.
    - Return the prefix of the frames filenames, the number of frames and the FPS of the
    video and the number of frames extracted per second of video.
    - The frames are not extracted again if the filenames exist.
    TODO: some images are rotated
    """

    print("CAP_PROP_ORIENTATION_AUTO", cv2.CAP_PROP_ORIENTATION_AUTO)
    cap = cv2.VideoCapture(video_path)
    video_fps = cap.get(cv2.CAP_PROP_FPS)
    frame_interval = int(video_fps / fps)
    frames = list()

    # if the frames were extracted previously, return the path to them
    video_fname = os.path.splitext(os.path.basename(video_path))[0]
    frames_fname_prefix = f"{video_fname}_fps{fps}_frame"
    n_frames = [
        None
        for fname in os.listdir(current_app.config["FRAMES_FOLDER"])
        if fname.startswith(frames_fname_prefix)
    ]
    if len(n_frames) > 0:
        return frames_fname_prefix, len(n_frames), video_fps, fps

    # extract frames
    frame_count = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        if frame_count % frame_interval == 0:
            frames.append(frame)
        frame_count += 1

    cap.release()

    # dump frames
    for idx, frame in enumerate(frames):
        cv2.imwrite(
            os.path.join(
                current_app.config["FRAMES_FOLDER"],
                f"{frames_fname_prefix}{idx}.jpg",
            ),
            frame,
        )

    return frames_fname_prefix, len(frames), video_fps, fps
