from flask import (
    Blueprint,
    redirect,
    request,
    session as flask_session,
)

from climbz.ner.entities_to_objects import get_route_from_entities
from climbz.models import Climb, Session, Sector
from climbz.forms import ClimbForm, RouteForm
from climbz import db
from climbz.ner.tracking import dump_predictions
from climbz.blueprints.utils import render


climbs = Blueprint("climbs", __name__)


@climbs.route("/add_climb", methods=["GET", "POST"])
def add_climb() -> str:
    entities = flask_session.get("entities", dict())

    # create forms and add choices
    session = Session.query.get(flask_session["session_id"])
    climb_form = None if session.is_project_search else ClimbForm()
    route_form = RouteForm.create_empty()

    # POST: a climb form was submitted => create climb or return error
    if request.method == "POST":
        invalid_climb = not climb_form.validate() if climb_form is not None else False
        if not route_form.validate() or invalid_climb:
            flask_session["error"] = route_form.errors or climb_form.errors
            return render(
                "add_climb.html",
                title="Add climb",
                climb_form=climb_form,
                route_form=route_form,
            )

        # create new sector and new route if necessary
        sector = route_form.get_sector(session.area_id)
        if sector.id is None:
            db.session.add(sector)
            db.session.commit()
            if "predictions" in flask_session:
                flask_session["predictions"]["sector_id"] = sector.id

        route = route_form.get_route_from_climb_form(sector)
        if route is not None and route.id is None:
            db.session.add(route)
            db.session.commit()
            if "predictions" in flask_session:
                flask_session["predictions"]["route_id"] = route.id

        if flask_session.get("project_search", False) is True:
            if "project_ids" not in flask_session:
                flask_session["project_ids"] = list()
            flask_session["project_ids"].append(route.id)

        # create climb if this is not a project
        if flask_session.get("project_search", False) is False:
            climb = Climb(
                **{
                    "n_attempts": climb_form.n_attempts.data,
                    "sent": climb_form.sent.data,
                    "route_id": route.id if route is not None else None,
                    "session_id": flask_session["session_id"],
                }
            )
            db.session.add(climb)
            db.session.commit()
            if "predictions" in flask_session:
                flask_session["predictions"]["climb_id"] = climb.id
                dump_predictions()

        return redirect("/")

    # GET: a recording was uploaded => create forms
    if flask_session.get("project_search", False) is True:
        climb_form = None
    else:
        climb_form = ClimbForm(
            n_attempts=entities.get("n_attempts", None),
            sent=entities.get("sent", False),
        )

    route = get_route_from_entities(entities, session.area_id)
    if route.id is None:
        route_form = RouteForm.create_from_entities(entities)
    else:
        route_form = RouteForm.create_empty()
        route_form.name.data = route.name

    # if no sector was found, add the last sector of the current session if possible
    if route.sector_id is None and flask_session.get("session_id", False) > 0:
        session = Session.query.get(flask_session["session_id"])
        sectors = [c.route.sector for c in session.climbs]
        if len(sectors) > 0:
            route_form.sector.data = sectors[-1].name

    # get existing sectors and routes
    sectors = (
        Sector.query.filter_by(area_id=session.area_id).order_by(Sector.name).all()
    )
    sector_names = [sector.name for sector in sectors]
    routes = list()
    for sector in sectors:
        routes += sector.routes
    route_names = sorted([route.name for route in routes])

    return render(
        "add_climb.html",
        title="Add climb",
        route_form=route_form,
        climb_form=climb_form,
        route_names=route_names,
        sector_names=sector_names,
    )


@climbs.route("/edit_climb/<int:climb_id>", methods=["GET", "POST"])
def edit_climb(climb_id: int) -> str:
    climb = Climb.query.get(climb_id)
    # POST: a climb form was submitted => edit climb or return error
    if request.method == "POST":
        climb_form = ClimbForm()
        # remove the is_project field from the form
        if not climb_form.validate():
            flask_session["error"] = climb_form.errors
            return render("edit_climb.html", title="Edit climb", climb_form=climb_form)
        climb.sent = climb_form.sent.data
        climb.n_attempts = climb_form.n_attempts.data
        db.session.commit()
        return redirect(flask_session.pop("call_from_url"))

    # GET: the user wants to edit a climb
    climb_form = ClimbForm(
        n_attempts=climb.n_attempts,
        sent=climb.sent,
    )
    return render(
        "add_climb.html",
        title="Edit climb",
        climb_form=climb_form,
        route_name=climb.route.name,
    )


@climbs.route("/delete_climb/<int:climb_id>")
def delete_climb(climb_id: int) -> str:
    climb = Climb.query.get(climb_id)
    db.session.delete(climb)
    db.session.commit()
    return redirect(flask_session.pop("call_from_url"))
