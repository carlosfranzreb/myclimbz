from flask import (
    Blueprint,
    redirect,
    session as flask_session,
    render_template,
    request,
    url_for,
)
from flask_login import current_user

from myclimbz.models import Grade, Climber
from myclimbz.blueprints.utils import render


home = Blueprint("home", __name__)


@home.route("/", methods=["GET", "POST"])
def page_home() -> str:
    return render(
        "data.html",
        title="Home",
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
    next = request.referrer
    if not current_user.is_authenticated:
        next = url_for("climbers.register")
    elif not next or "guide" in next:
        next = url_for("home.page_home")

    return render_template("docs/guide.html", title="myclimbz - User Guide", next=next)


@home.route("/example_analysis")
def example_analysis() -> str:
    next = request.referrer
    if not current_user.is_authenticated:
        next = url_for("climbers.register")
    elif not next or "guide" in next:
        next = url_for("home.page_home")

    return render_template(
        "docs/example_analysis.html", title="myclimbz - Examples", next=next
    )
