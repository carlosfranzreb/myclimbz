from flask import (
    Blueprint,
    redirect,
    request,
    session as flask_session,
)
from flask_login import current_user

from climbz.models import Climb, Session, Climber
from climbz.forms import ClimbForm, RouteForm
from climbz import db
from climbz.blueprints.utils import render


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
        route_name = route_form.name.data
        invalid_climb = (
            not climb_form.validate_from_name(route_name)
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
        if not climb_form.validate(climb.route, climb.session_id):
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
    climb = Climb.query.get(climb_id)
    db.session.delete(climb)
    db.session.commit()
    return redirect(flask_session.pop("call_from_url"))
