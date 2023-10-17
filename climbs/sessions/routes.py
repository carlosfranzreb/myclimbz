from flask import Blueprint, render_template, request
from climbs.models import Session


sessions = Blueprint("sessions", __name__)


@sessions.route("/sessions")
def table_sessions() -> str:
    page = request.args.get("page", 1, type=int)
    page_sessions = Session.query.paginate(page=page, per_page=10)
    return render_template("sessions.html", sessions=page_sessions)


@sessions.route("/session/<int:session_id>")
def page_session(session_id: int) -> str:
    session = Session.query.get(session_id)
    return render_template("session.html", session=session)
