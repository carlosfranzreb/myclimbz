from flask import (
    Blueprint,
    request,
    url_for,
    redirect,
    session as flask_session,
)
from flask_login import current_user

from myclimbz.models import Route, Climber
from myclimbz.forms import RouteForm
from myclimbz import db
from myclimbz.blueprints.utils import render

routes = Blueprint("routes", __name__)


@routes.route("/route/<int:route_id>")
def page_route(route_id: int) -> str:
    route = Route.query.get(route_id)
    return render("route.html", title=route.name, route=route)


@routes.route("/edit_route/<int:route_id>", methods=["GET", "POST"])
def edit_route(route_id: int) -> str:
    route = Route.query.get(route_id)
    title = "Edit route"
    # POST: a route form was submitted => edit route or return error
    route_form = RouteForm.create_empty(route.sector.area_id)
    if request.method == "POST":
        if not route_form.validate():
            return render("form.html", title=title, forms=[route_form])

        # if the name has changed, check if it already exists
        if route_form.name.data != route.name:
            if Route.query.filter_by(name=route_form.name.data).first() is not None:
                route_form.name.errors.append("A route with that name already exists.")
                flask_session["error"] = "An error occurred. Fix it and resubmit."
                return render("form.html", title=title, forms=[route_form])

        route = route_form.get_edited_route(route_id)
        db.session.add(route)
        db.session.commit()

        # if the user wants to add an opinion, redirect to the opinion form
        if route_form.add_opinion.data is True:
            return redirect(f"/get_opinion_form/{current_user.id}/{route.id}")
        else:
            return redirect(flask_session.pop("call_from_url"))

    # GET: return the edit route page
    route_form = RouteForm.create_from_obj(route)
    return render("form.html", title=title, forms=[route_form])


@routes.route("/delete_route/<int:route_id>", methods=["GET", "POST"])
def delete_route(route_id: int) -> str:
    """
    Deleting a route is only possible if these two conditions are met:
    1. The user is the owner of the route, or an admin.
        - This is checked in check_request_validity (./myclimbz/__init__.py)
    2. The route has not been climbed or marked as a project by other climbers.
    """
    route = Route.query.get(route_id)
    flask_session["error"] = None
    if route is None:
        flask_session["error"] = "Route not found."

    if flask_session["error"] is None and route.climbs:
        for climb in route.climbs:
            if climb.climber_id != current_user.id:
                flask_session["error"] = (
                    "This route has been climbed by other climbers."
                )
                break

    if flask_session["error"] is None:
        for climber in Climber.query.all():
            if route in climber.projects:
                flask_session["error"] = (
                    "This route has been marked as a project by other climbers."
                )
                break

    last_url = flask_session.pop("call_from_url")
    if flask_session["error"] is None:
        db.session.delete(route)
        db.session.commit()
        flask_session["error"] = "Route deleted."
        if "route" in last_url:
            return redirect(url_for("areas.page_area", area_id=route.sector.area_id))

    return redirect(last_url)
