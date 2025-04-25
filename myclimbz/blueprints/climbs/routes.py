from flask import Blueprint, redirect, request, session as flask_session
from flask_login import current_user

from myclimbz.models import Climb, Session, Climber, Video
from myclimbz.forms import ClimbForm, RouteForm
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
            if video_obj:
                climb.videos.append(video_obj)
            db.session.add(climb)
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
