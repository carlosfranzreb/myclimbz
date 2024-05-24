from flask import (
    Blueprint,
    request,
    url_for,
    redirect,
    session as flask_session,
)

from climbz.models import Route
from climbz.forms import RouteForm
from climbz import db
from climbz.blueprints.utils import render

routes = Blueprint("routes", __name__)


@routes.route("/route/<int:route_id>")
def page_route(route_id: int) -> str:
    route = Route.query.get(route_id)
    return render("route.html", route=route)


@routes.route("/edit_route/<int:route_id>", methods=["GET", "POST"])
def edit_route(route_id: int) -> str:
    route = Route.query.get(route_id)
    # POST: a route form was submitted => edit route or return error
    route_form = RouteForm.create_empty(route.sector.area_id)
    if request.method == "POST":
        if not route_form.validate():
            return render("form.html", title="Edit route", forms=[route_form])

        # if the name has changed, check if it already exists
        if route_form.name.data != route.name:
            if Route.query.filter_by(name=route_form.name.data).first() is not None:
                flask_session["error"] = "A route with that name already exists."
                return render("form.html", forms=[route_form])

        route = route_form.get_edited_route(route_id)
        db.session.add(route)
        db.session.commit()
        return redirect(url_for("routes.page_route", route_id=route.id))

    # GET: return the edit route page
    route_form = RouteForm.create_from_obj(route)
    return render("form.html", title="Edit Route", forms=[route_form])


@routes.route("/delete_route/<int:route_id>", methods=["GET", "POST"])
def delete_route(route_id: int) -> str:
    route = Route.query.get(route_id)
    db.session.delete(route)
    db.session.commit()
    return redirect(flask_session.pop("call_from_url"))
