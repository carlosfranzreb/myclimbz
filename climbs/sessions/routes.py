from flask import Blueprint, render_template, request
from climbs.models import Session


sessions = Blueprint("sessions", __name__)


@sessions.route("/sessions")
def table_sessions() -> str:
    page = request.args.get("page", 1, type=int)
    page_sessions = Session.query.paginate(page=page, per_page=10)
    return render_template("sessions.html", sessions=page_sessions)
