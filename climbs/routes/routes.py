from flask import Blueprint, render_template, request
from climbs.models import Route

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
