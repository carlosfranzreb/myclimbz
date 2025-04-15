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
)
from flask_login import current_user
from werkzeug.utils import secure_filename

from myclimbz.models import Climb, Session, Climber
from myclimbz.forms import ClimbForm, RouteForm, VideosForm, VideosSortingForm
from myclimbz import db
from myclimbz.blueprints.utils import render


climbs = Blueprint("climbs", __name__)


@climbs.route("/add_climb", methods=["GET", "POST"])
def add_climb() -> str:

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

        # add as project or create climb
        climber = Climber.query.get(current_user.id)
        if is_project_search or climb_form.is_project.data:
            climber.projects.append(route)
        else:
            climb = climb_form.get_object(route)
            db.session.add(climb)
        db.session.commit()

        # if the user wants to add an opinion, redirect to the opinion form
        if route_form.add_opinion.data is True:
            return redirect(f"/get_opinion_form/{climber.id}/{route.id}")
        else:
            return redirect(flask_session.pop("call_from_url"))

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

    # POST: a climb form was submitted => create climb or return error
    if request.method == "POST":
        if not form.validate():
            if flask_session.get("error", None) is None:
                flask_session["error"] = "An error occurred. Fix it and resubmit."
            return render(
                "form.html", title=title, forms=[form], enctype="multipart/form-data"
            )

        # upload videos
        fnames = list()
        timestamp = int(time())
        for f_idx, f in enumerate(form.videos.data):
            f_ext = os.path.splitext(f.filename)[1]
            fnames.append(
                secure_filename(
                    f"{current_user.id}_{session_id}_{timestamp}_added-{f_idx}{f_ext}"
                )
            )
            f.save(os.path.join(current_app.config["UPLOAD_FOLDER"], fnames[-1]))

        return redirect(f"/sort_videos/{current_user.id}/{session_id}/{timestamp}")

    # GET: the user wants to upload videos
    return render("form.html", title=title, forms=[form], enctype="multipart/form-data")


@climbs.route(
    "/sort_videos/<int:user_id>/<int:session_id>/<int:timestamp>",
    methods=["GET", "POST"],
)
def sort_videos(user_id: int, session_id: int, timestamp: int) -> str:
    """
    The user can sort the videos chronologically and is then sent to `process_videos`.
    """

    check_access_to_videos(user_id, session_id)

    # get the video filenames
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    video_prefix = f"{user_id}_{session_id}_{timestamp}"
    videos = list()
    videos = sorted(
        [fname for fname in os.listdir(upload_folder) if fname.startswith(video_prefix)]
    )

    # if there is only one video, skip this and go to process_videos
    if len(videos) == 1:
        return redirect(f"/process_videos/{user_id}/{timestamp}")

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
                    os.path.join(current_app.config["UPLOAD_FOLDER"], f),
                    os.path.join(current_app.config["UPLOAD_FOLDER"], f_new),
                )
                videos[f_idx] = f_new

            return redirect(f"/process_videos/{user_id}/{session_id}/{timestamp}")

    return render(
        "form_sort_videos.html",
        title=title,
        form=form,
        videos=videos,
        timestamp=timestamp,
    )


@climbs.route(
    "/process_videos/<int:user_id>/<int:session_id>/<int:timestamp>",
    methods=["GET", "POST"],
)
def process_videos(user_id: int, session_id: int, timestamp: int) -> str:
    """
    The user can perform here the following actions:

    1. Sort the videos chronologically.
    2. Mark the portions of each video where there is climbing.
        - Only the marked will be saved.
        - The number of attempts is inferred from the marked portions
    3. Fill in the remaining route and climb info for each video:
        - Route information.
        - Whether the route was sent or flashed.
        - Add or edit an opinion.
    """

    check_access_to_videos(user_id, session_id)

    pass


@climbs.route("/videos/<filename>")
def uploaded_video(filename):
    """
    Serves files from the UPLOAD_FOLDER.
    TODO: protect access to videos in __init__.py, where all access rights are handled.
    """
    file_user_id = int(filename.split("_")[0])
    check_access_to_videos(file_user_id)

    try:
        return send_from_directory(current_app.config["UPLOAD_FOLDER"], filename)
    except FileNotFoundError:
        abort(404)


def check_access_to_videos(user_id: int, session_id: int = None):
    """
    Check that the user is the owner of the videos, and that the session of the videos
    is currently open.
    TODO: this may belong in __init__.py, where all access rights are handled.
    """
    if current_user.id != user_id:
        flask_session["error"] = "You are not allowed to access this page."
        return redirect(flask_session.pop("call_from_url"))

    if session_id and session_id != flask_session["session_id"]:
        flask_session["error"] = (
            "The session is closed. Redirecting to the session's page"
        )
        return redirect(f"/session/{session_id}")
