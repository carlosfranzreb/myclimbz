from flask import (
    Blueprint,
    redirect,
    request,
    session as flask_session,
)

from climbz.models import Climb, Session, Opinion
from climbz.forms import ClimbForm, RouteForm
from climbz import db
from climbz.blueprints.utils import render


climbs = Blueprint("climbs", __name__)


@climbs.route("/add_climb", methods=["GET", "POST"])
def add_climb() -> str:

    # create forms and add choices
    session = Session.query.get(flask_session["session_id"])
    route_form = RouteForm.create_empty(session.area_id)
    climb_form = ClimbForm.create_empty() if not session.is_project_search else None
    title = "Add climb"

    # POST: a climb form was submitted => create climb or return error
    if request.method == "POST":
        route_name = route_form.name.data
        invalid_climb = (
            not climb_form.validate_from_name(route_name)
            if not session.is_project_search
            else False
        )
        if not route_form.validate() or invalid_climb:
            flask_session["error"] = "An error occurred. Fix it and resubmit."
            return render("form.html", title=title, forms=[route_form, climb_form])

        # create new sector and new route if necessary
        sector = route_form.get_sector(session.area_id)
        if sector.id is None:
            db.session.add(sector)
            db.session.commit()

        route = route_form.get_object(sector)
        if route is not None and route.id is None:
            db.session.add(route)
            db.session.commit()

        if session.is_project_search:
            if "project_ids" not in flask_session:
                flask_session["project_ids"] = list()
            flask_session["project_ids"].append(route.id)

        # add as project or create climb
        if session.is_project_search or climb_form.is_project.data:
            session.climber.projects.append(route)
            db.session.commit()
        else:
            climb = climb_form.get_object(route)
            db.session.add(climb)
            db.session.commit()

        # if the user wants to add an opinion, redirect to the opinion form
        if climb_form.add_opinion.data is True:
            opinion = Opinion.query.filter_by(
                climber_id=session.climber_id, route_id=route.id
            ).first()
            if opinion is not None:
                return redirect(f"/edit_opinion/{opinion.id}")
            else:
                return redirect(f"/add_opinion/{session.climber_id}/{route.id}")
        else:
            return redirect("/")

    # GET: the climber wants to add a route (+climb)
    route_form.title = "Route"
    if session.is_project_search:
        return render("form.html", title=title, forms=[route_form])
    else:
        climb_form.title = "Climb"
        return render("form.html", title=title, forms=[route_form, climb_form])


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
