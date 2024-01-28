from flask import Blueprint, render_template
from climbs.models import Route, Grade


analysis = Blueprint("analysis", __name__)


@analysis.route("/analysis")
def analyze() -> str:
    return render_template(
        "analysis.html",
        title="Analysis",
        routes=[route.as_dict() for route in Route.query.all()],
        grades=[grade.as_dict() for grade in Grade.query.all()],
    )


@analysis.route("/table")
def table() -> str:
    return render_template(
        "table.html",
        title="Table",
        routes=[route.as_dict() for route in Route.query.all()],
        grades=[grade.as_dict() for grade in Grade.query.all()],
    )
