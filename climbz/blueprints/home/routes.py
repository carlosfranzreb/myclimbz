from flask import (
    Blueprint,
    redirect,
    session as flask_session,
)
from flask_login import current_user

from climbz.models import Grade, Climber
from climbz.blueprints.utils import render


home = Blueprint("home", __name__)


@home.route("/", methods=["GET", "POST"])
def page_home() -> str:
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
