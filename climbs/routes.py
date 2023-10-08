from flask import Blueprint, render_template, request
from climbs.models import Route

routes = Blueprint("routes", __name__)
FILE = "src/static/data/boulders.csv"


@routes.route("/table")
def table():
    page = request.args.get("page", 0, type=int)
    climbs = Route.query.paginate(page=page, per_page=10)
    return render_template("tables.html", climbs=climbs)


@routes.route("/analysis")
def analysis():
    return render_template("analysis.html", title="Analysis")
