from flask import Blueprint, render_template, request, url_for, redirect
from climbs.models import Route
from climbs.forms import RouteForm
from climbs import db

routes = Blueprint("routes", __name__)
FILE = "src/static/data/boulders.csv"


@routes.route("/routes")  # ? Missing "methods" argument
def table_routes() -> str:
    page_routes = Route.query.all()
    return render_template("routes.html", title="Routes", routes=page_routes)


@routes.route("/route/<int:route_id>")
def page_route(route_id: int) -> str:
    route = Route.query.get(route_id)
    return render_template("route.html", route=route)


@routes.route("/edit_route/<int:route_id>", methods=["GET", "POST"])
def edit_route(route_id: int) -> str:
    route_form = RouteForm.create_empty()

    # POST: a route form was submitted => edit route or return error
    if request.method == "POST":
        if not route_form.validate():
            return render_template("route.html", title="Route", route_id=route_id)
        route = route_form.get_edited_route(route_id)
        db.session.add(route)
        db.session.commit()
        return redirect(url_for("routes.page_route", route_id=route.id))

    # GET: return the edit route page
    route = Route.query.get(route_id)
    route_form = RouteForm.create_from_obj(route)
    return render_template("edit_route.html", title="Edit Route", route_form=route_form)
