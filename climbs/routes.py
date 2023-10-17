from flask import Blueprint, render_template, request
from climbs.models import Route, Grade, Area, Session

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


@routes.route("/areas")
def table_areas() -> str:
    page = request.args.get("page", 1, type=int)
    page_areas = Area.query.paginate(page=page, per_page=10)
    return render_template("areas.html", areas=page_areas)


@routes.route("/area/<int:area_id>")
def page_area(area_id: int) -> str:
    area = Area.query.get(area_id)
    return render_template("area.html", area=area)


@routes.route("/sessions")
def table_sessions() -> str:
    page = request.args.get("page", 1, type=int)
    page_sessions = Session.query.paginate(page=page, per_page=10)
    return render_template("sessions.html", sessions=page_sessions)


@routes.route("/analysis")
def analysis() -> str:
    routes_dict = [route.as_dict() for route in Route.query.all()]
    grades_dict = [grade.as_dict() for grade in Grade.query.all()]
    return render_template(
        "analysis.html",
        title="Analysis",
        routes=routes_dict,
        grades=grades_dict,
    )
