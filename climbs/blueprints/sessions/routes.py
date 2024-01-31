from flask import Blueprint, render_template
from climbs.models import Session


sessions = Blueprint("sessions", __name__)


@sessions.route("/sessions")
def table_sessions() -> str:
    return render_template(
        "sessions.html", title="Sessions", sessions=Session.query.all()
    )


@sessions.route("/session/<int:session_id>")
def page_session(session_id: int) -> str:
    session = Session.query.get(session_id)
    return render_template("session.html", session=session)
