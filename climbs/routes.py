from flask import Blueprint, render_template, request
from climbs.models import Route, Grade

routes = Blueprint("routes", __name__)
FILE = "src/static/data/boulders.csv"


@routes.route("/table")
def table():
    page = request.args.get("page", 1, type=int)
    page_routes = Route.query.paginate(page=page, per_page=10)
    return render_template("tables.html", title="Routes", routes=page_routes)


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
