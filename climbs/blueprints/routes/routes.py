from flask import Blueprint, render_template, request
from climbs.models import Route
from climbs.forms import RouteForm

routes = Blueprint("routes", __name__)
FILE = "src/static/data/boulders.csv"


@routes.route("/routes")
def table_routes() -> str:
    page = request.args.get("page", 1, type=int)
    page_routes = Route.query.paginate(page=page, per_page=10)
    return render_template("routes.html", routes=page_routes)


@routes.route("/route/<int:route_id>")
def page_route(route_id: int) -> str:
    route = Route.query.get(route_id)
    return render_template("route.html", route=route)


@routes.route("/edit_route/<int:route_id>", methods=["GET", "POST"])
def edit_route(route_id: int) -> str:
    route = Route.query.get(route_id)
    route_form = RouteForm()
    route_form.add_choices("font")

    # POST: a route form was submitted => edit climb or return error
    if request.method == "POST":
        if not route_form.validate(is_edit=True):
            return render_template(
                "edit_route.html", route_form=route_form, error=route_form.errors
            )
        route = route_form.get_obj(route)
        # TODO: save route and return to route page

    # GET: return the edit route page
    route_form = RouteForm()
    route_form.add_choices("font")
    route_form.populate_from_obj(route)
    return render_template("edit_route.html", route_form=route_form)
