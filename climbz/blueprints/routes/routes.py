from flask import Blueprint, render_template, request, url_for, redirect
from climbz.models import Route
from climbz.forms import RouteForm
from climbz import db

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

    route = Route.query.get(route_id)
    # POST: a route form was submitted => edit route or return error
    route_form = RouteForm.create_empty()
    if request.method == "POST":
        if not route_form.validate():
            return render_template("route.html", title="Route", route_id=route_id)

        # if the name has changed, check if it already exists
        if route_form.name.data != route.name:
            if Route.query.filter_by(name=route_form.name.data).first() is not None:
                return render_template(
                    "edit_route.html",
                    route_form=route_form,
                    error="A route with that name already exists.",
                )

        route = route_form.get_edited_route(route_id)
        db.session.add(route)
        db.session.commit()
        return redirect(url_for("routes.page_route", route_id=route.id))

    # GET: return the edit route page
    route_form = RouteForm.create_from_obj(route)
    return render_template("edit_route.html", title="Edit Route", route_form=route_form)


@routes.route("/delete_route/<int:route_id>", methods=["GET", "POST"])
def delete_route(route_id: int) -> str:
    return redirect(url_for("routes.page_route", route_id=route_id))
