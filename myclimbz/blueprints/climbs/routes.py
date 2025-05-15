from flask import Blueprint, redirect, request, session as flask_session, abort, jsonify
from flask_login import current_user

from myclimbz.models import Climb, Session, Climber, Route
from myclimbz.forms import RouteForm, ClimbForm, OpinionForm
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
    opinion_form = OpinionForm.create_empty()

    # POST: a climb form was submitted => create climb or return error
    if request.method == "POST":
        flask_session["all_forms_valid"] = True
        if not is_project_search:
            climb_form.validate_from_name(route_form.name.data, route_form.sector.data)

        for form in [route_form, opinion_form]:
            flask_session["all_forms_valid"] &= form.validate()

        if flask_session["all_forms_valid"]:
            # create opinion, sector and route if necessary
            sector = route_form.get_sector(area_id)
            route = route_form.get_object(sector)
            for obj in [sector, route]:
                if obj.id is None:
                    db.session.add(obj)
                    db.session.commit()

            if not opinion_form.skip_opinion.data:
                opinion = opinion_form.get_object(current_user.id, route.id)
                if opinion.id is None:
                    db.session.add(opinion)
                    db.session.commit()

            # add as project or create climb
            climber = Climber.query.get(current_user.id)
            if is_project_search or climb_form.is_project.data:
                if not route.tried and not route.is_project:
                    climber.projects.append(route)
            else:
                climb = climb_form.get_object(route)
                db.session.add(climb)
            db.session.commit()

            return redirect(flask_session.pop("call_from_url"))

    # serve the page
    forms = [route_form]
    if not is_project_search:
        forms.append(climb_form)
    forms.append(opinion_form)  # the opinion form should appear last
    return render("form.html", title=title, forms=forms)


@climbs.route("/edit_climb/<int:climb_id>", methods=["GET", "POST"])
def edit_climb(climb_id: int) -> str:
    climb = Climb.query.get(climb_id)
    title = f"Edit climb on {climb.route.name}"

    # POST: a climb form was submitted => edit climb or return error
    if request.method == "POST":
        climb_form = ClimbForm()
        if not climb_form.validate(climb.route, climb.session_id):
            flask_session["all_forms_valid"] = False

        else:
            climb = climb_form.get_edited_climb(climb_id)
            db.session.commit()
            return redirect(flask_session.pop("call_from_url"))

    # GET: the user wants to edit a climb
    elif request.method == "GET":
        climb_form = ClimbForm.create_from_object(climb, remove_title=True)
        del climb_form.is_project

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


@climbs.route("/get_climb_from_route_name/<route_name>")
def get_climb_from_route_name(route_name: str) -> str:
    """
    Given a route name by the frontend, return the opinion info required to populate
    the form, if there is an opinion. We assume that the user is the current user.
    """
    route = Route.query.filter_by(name=route_name).first()
    if route is None:
        abort(404)

    climb = Climb.query.filter_by(
        route_id=route.id, session_id=flask_session["session_id"]
    ).first()
    if climb is None:
        return jsonify({})

    # return opinion information
    return jsonify(
        {
            "n_attempts": climb.n_attempts,
            "sent": climb.sent,
            "flashed": climb.flashed,
            "climb_comment": climb.comment,
            "climb_link": climb.link,
        }
    )
