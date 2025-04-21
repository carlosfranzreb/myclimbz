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

from myclimbz.models import Climb, Session, Climber, Video, VideoAttempt
from myclimbz.forms import (
    ClimbForm,
    RouteForm,
    VideosForm,
    VideosSortingForm,
    VideoAnnotationForm,
)
from myclimbz import db
from myclimbz.blueprints.utils import render, redirect_after_form_submission


climbs = Blueprint("climbs", __name__)


@climbs.route("/add_climb", methods=["GET", "POST"])
def add_climb() -> str:
    """
    TODO: the same route can be added more than once in a session.
    """

    # create forms and add choices
    title = "Add climb"
    is_project_search = flask_session["session_id"] == "project_search"
    if is_project_search:
        area_id = flask_session["area_id"]
        climb_form = None
    else:
        session = Session.query.get(flask_session["session_id"])
        area_id = session.area_id
        climb_form = ClimbForm.create_empty()
    route_form = RouteForm.create_empty(area_id)

    # get video object if there is one
    video_id = flask_session.get("video_id", None)
    if video_id:
        video_obj = Video.query.get(video_id)
        climb_form.n_attempts.data = len(video_obj.attempts)

    # POST: a climb form was submitted => create climb or return error
    if request.method == "POST":
        invalid_climb = (
            not climb_form.validate_from_name(
                route_form.name.data, route_form.sector.data
            )
            if not is_project_search
            else False
        )
        if not route_form.validate() or invalid_climb:
            if flask_session.get("error", None) is None:
                flask_session["error"] = "An error occurred. Fix it and resubmit."
            forms = [route_form]
            if not is_project_search:
                forms.append(climb_form)
            return render("form.html", title=title, forms=forms)

        # create new sector and new route if necessary
        sector = route_form.get_sector(area_id)
        if sector.id is None:
            db.session.add(sector)
            db.session.commit()

        route = route_form.get_object(sector)
        if route.id is None:
            db.session.add(route)
            db.session.commit()

        # add as project or create climb, and add it to video object if appropriate
        climber = Climber.query.get(current_user.id)
        if is_project_search or climb_form.is_project.data:
            climber.projects.append(route)
        else:
            climb = climb_form.get_object(route)
            db.session.add(climb)
            if video_obj:
                video_obj.climb = climb
        db.session.commit()

        # if the user wants to add an opinion, redirect to the opinion form
        if route_form.add_opinion.data is True:
            return redirect(f"/get_opinion_form/{climber.id}/{route.id}")
        else:
            return redirect_after_form_submission()

    # GET: the climber wants to add a route (+ climb if not in a project search)
    route_form.title = "Route"
    forms = [route_form]
    if not is_project_search:
        climb_form.title = "Climb"
        forms.append(climb_form)
    return render("form.html", title=title, forms=forms)


@climbs.route("/edit_climb/<int:climb_id>", methods=["GET", "POST"])
def edit_climb(climb_id: int) -> str:
    climb = Climb.query.get(climb_id)
    title = f"Edit climb on {climb.route.name}"

    # POST: a climb form was submitted => edit climb or return error
    if request.method == "POST":
        climb_form = ClimbForm()
        if not climb_form.validate(climb.route, climb.session_id, climb_id=climb_id):
            if flask_session.get("error", None) is None:
                flask_session["error"] = "An error occurred. Fix it and resubmit."
            return render("form.html", title=title, forms=[climb_form])
        climb = climb_form.get_edited_climb(climb_id)
        db.session.commit()
        return redirect(flask_session.pop("call_from_url"))

    # GET: the user wants to edit a climb
    climb_form = ClimbForm.create_from_object(climb)
    return render("form.html", title=title, forms=[climb_form])


@climbs.route("/delete_climb/<int:climb_id>")
def delete_climb(climb_id: int) -> str:
    """
    Deleting a climb is only possible if the user is the owner of the climb, or an
    admin. This is checked in check_request_validity (./myclimbz/__init__.py)
    """
    climb = Climb.query.get(climb_id)
    db.session.delete(climb)
    db.session.commit()
    return redirect(flask_session.pop("call_from_url"))


@climbs.route("/climb/<int:climb_id>")
def view_climb(climb_id: int) -> str:
    climb = Climb.query.get(climb_id)
    return render("climb.html", climb=climb, title=f"Climb on {climb.route.name}")


@climbs.route("/add_videos", methods=["GET", "POST"])
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


@climbs.route("/sort_videos", methods=["GET", "POST"])
def sort_videos() -> str:
    """
    The user can sort the videos chronologically and is then sent to `process_videos`.
    """

    videos = sorted(flask_session["video_fnames"])
    check_access_to_videos(videos[0])

    # if there is only one video, skip this and go to process_videos
    if len(videos) == 1:
        videos[0] = videos[0].replace("added", "sorted")
        flask_session["video_fnames"] = videos
        return redirect(f"/annotate_video/1/0")

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
            return redirect(f"/annotate_video/{len(videos)}/0")

    return render("form_sort_videos.html", title=title, form=form, videos=videos)


@climbs.route(
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
    check_access_to_videos(video_fname)

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


@climbs.route("/files/<filetype>/<filename>")
def serve_file(filetype: str, filename: str):
    """
    Serves files from the UPLOAD_FOLDER.
    TODO: protect access to videos in __init__.py, where all access rights are handled.
    """
    check_access_to_videos(filename)

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


def check_access_to_videos(filename: str, ignore_session: bool = False):
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
        flask_session["error"] = "You are not allowed to access this page."
        return redirect(flask_session.pop("call_from_url"))

    if not ignore_session and session_id != flask_session["session_id"]:
        flask_session["error"] = (
            "The session is closed. Redirecting to the session's page"
        )
        return redirect(f"/session/{session_id}")


def get_video_frames(video_path: str, fps: int = 2) -> tuple[str, int, int, int]:
    """
    - Extract and dump `fps` frames per second from the video.
    - Return the prefix of the frames filenames, the number of frames and the FPS of the
    video and the number of frames extracted per second of video.
    - The frames are not extracted again if the filenames exist.
    TODO: some images are rotated
    """

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
