from flask import (
    Blueprint,
    redirect,
    session as flask_session,
    request,
)
from flask_login import current_user

import pandas as pd

from climbz.models import Grade, Climber
from climbz.blueprints.utils import render
from climbz.blueprints.climbs import routes as climbs_route
from climbz.blueprints.sessions import routes as sessions_route
from climbz.forms.session import SessionForm
from climbz import db


home = Blueprint("home", __name__)


@home.route("/", methods=["GET", "POST"])
def page_home() -> str:
    if request.method == "POST":
        try:
            csv_json = request.form["csv_data"]
        except KeyError:
            flask_session["error"] = "No file was uploaded."
            return redirect("/")
        csv_json = request.form["csv_data"]
        # group climbs by date and area
        climbs = pd.read_json(csv_json)
        climbs_by_date = climbs.groupby("dates")
        for date, climbs in climbs_by_date:
            climbs_by_area = climbs.groupby("area")
            for area, climbs in climbs_by_area:
                # TODO:create a session
                session_form = SessionForm.create_empty()
                session_form.area.data = area
                area_obj = session_form.get_area()
                session_form.date.data = date
                # TODO: What to do about conditions in sessions
                sessions_route.add_session(True)

                for climb in climbs.itertuples():
                    # TODO: add necessary info to entities.
                    route_form = climbs_route.RouteForm.create_empty()
                    # obligatory options
                    route_form.name.data = climb.name
                    # TODO add option for nonexistent
                    route_form.height.data = climb.height
                    route_form.inclination.data = climb.inclination
                    route_form.sit_start.data = climb.sit_start
                    route_form.sector.data = climb.sector

                    is_project = climb.attempts == 0

                    climb_form = climbs_route.ClimbForm() if not is_project else None
                    if not is_project:
                        climb_form.n_attempts.data = climb.attempts
                        climb_form.sent.data = climb.sent

                    climbs_route.add_climb(True)
    return render(
        "data.html",
        title="Routes",
        routes=Climber.query.get(current_user.id).all_routes_as_dict(),
        grades=[grade.as_dict() for grade in Grade.query.all()],
    )


@home.route("/cancel_form")
def cancel_form() -> str:
    """Cancel the addition of a session."""
    flask_session.pop("entities", None)
    flask_session.pop("predictions", None)
    return redirect(flask_session.pop("call_from_url"))


@home.route("/guide")
def guide() -> str:
    return render("guide.html", title="User Guide")
