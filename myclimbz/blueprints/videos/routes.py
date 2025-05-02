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

from myclimbz.models import Video, VideoAttempt, Session
from myclimbz.forms import (
    VideosForm,
    VideosSortingForm,
    VideoAnnotationForm,
    RouteForm,
    ClimbForm,
    OpinionForm,
)
from myclimbz import db
from myclimbz.blueprints.utils import render, delete_video_info
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

    # create video annotation form
    title = "Annotate"
    video_path = os.path.join(current_app.config["VIDEOS_FOLDER"], video_fname)
    frames_fname_prefix, n_frames, fps_video, fps_taken = get_video_frames(video_path)
    video_form = VideoAnnotationForm()
    flask_session["video_upload_status"] = [video_idx, n_videos]

    # create other forms
    area_id = Session.query.get(flask_session["session_id"]).area_id
    route_form = RouteForm.create_empty(area_id)
    climb_form = ClimbForm.create_empty()
    opinion_form = OpinionForm.create_empty()

    # POST: user submitted forms
    if request.method == "POST":

        # validate forms
        flask_session["error"] = None
        for form in [video_form, route_form, opinion_form]:
            if not form.validate():
                if not flask_session[
                    "error"
                ]:  # TODO: can't this be added automatically somewhere else?
                    flask_session["error"] = "An error occurred. Fix it and resubmit."

        if not climb_form.validate_from_name(
            route_form.name.data, route_form.sector.data
        ):
            if not flask_session["error"]:
                flask_session["error"] = "An error occurred. Fix it and resubmit."

        # store info if forms are valid
        if not flask_session["error"]:
            # store video annotations and trim video
            video_obj = Video(
                fname=video_fname, fps_video=fps_video, fps_taken=fps_taken
            )
            for section in video_form.sections.data:
                video_obj.attempts.append(
                    VideoAttempt(start_frame=section["start"], end_frame=section["end"])
                )
                trim_video(video_obj, section["start"], section["end"])

            db.session.add(video_obj)
            db.session.commit()
            os.remove(video_path)

            # store route, climb and opinion (TODO: use code from climbs.add_climb?)
            sector = route_form.get_sector(area_id)
            route = route_form.get_object(sector)
            for obj in [sector, route]:
                if obj.id is None:
                    db.session.add(obj)
            opinion = opinion_form.get_object(current_user.id, route.id)
            if opinion.id is None:
                db.session.add(opinion)
            db.session.commit()

            climb = climb_form.get_object(route)
            if video_obj not in climb.videos:
                climb.videos.append(video_obj)
            db.session.add(climb)
            db.session.commit()

            # go to next video or back to previous page if all videos were annotated
            video_idx, n_videos = flask_session["video_upload_status"]
            if video_idx + 1 < n_videos:
                return redirect(
                    url_for(
                        "videos.annotate_video",
                        n_videos=n_videos,
                        video_idx=video_idx + 1,
                    )
                )
            else:
                delete_video_info()
                return redirect(flask_session.pop("call_from_url"))

    # GET: the user is asked to annotate a video
    route_form.title = "Route"  # TODO: should I define the titles somewhere else?
    climb_form.title = "Climb"
    opinion_form.title = "Opinion"
    return render(
        "form_annotate_video.html",
        title=title,
        video_form=video_form,
        other_forms=[route_form, climb_form, opinion_form],
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
