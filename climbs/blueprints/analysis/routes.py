from flask import Blueprint, render_template
from climbs.models import Route, Grade


analysis = Blueprint("analysis", __name__)


@analysis.route("/analysis")
def analyze() -> str:
    routes_dict = [route.as_dict() for route in Route.query.all()]
    grades_dict = [grade.as_dict() for grade in Grade.query.all()]
    return render_template(
        "analysis.html",
        title="Analysis",
        routes=routes_dict,
        grades=grades_dict,
    )


@analysis.route("/table")
def table() -> str:
    routes_dict = [route.as_dict() for route in Route.query.all()]
    grades_dict = [grade.as_dict() for grade in Grade.query.all()]
    return render_template(
        "table.html",
        title="Table",
        routes=routes_dict,
        grades=grades_dict,
    )
