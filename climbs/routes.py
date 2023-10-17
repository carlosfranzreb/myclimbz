from flask import Blueprint, render_template, request
from climbs.models import Route, Grade, Area, Session

routes = Blueprint("routes", __name__)
FILE = "src/static/data/boulders.csv"


@routes.route("/routes")
def table_routes():
    page = request.args.get("page", 1, type=int)
    page_routes = Route.query.paginate(page=page, per_page=10)
    return render_template("routes.html", routes=page_routes)


@routes.route("/areas")
def table_areas():
    page = request.args.get("page", 1, type=int)
    page_areas = Area.query.paginate(page=page, per_page=10)
    return render_template("areas.html", areas=page_areas)


@routes.route("/sessions")
def table_sessions():
    page = request.args.get("page", 1, type=int)
    page_sessions = Session.query.paginate(page=page, per_page=10)
    return render_template("sessions.html", sessions=page_sessions)


@routes.route("/analysis")
def analysis():
    routes_dict = [route.as_dict() for route in Route.query.all()]
    grades_dict = [grade.as_dict() for grade in Grade.query.all()]
    return render_template(
        "analysis.html",
        title="Analysis",
        routes=routes_dict,
        grades=grades_dict,
    )
