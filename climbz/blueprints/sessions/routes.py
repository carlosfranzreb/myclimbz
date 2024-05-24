from flask import (
    Blueprint,
    redirect,
    request,
    session as flask_session,
)
from flask_login import current_user

from climbz.models import Area, Session
from climbz.forms import SessionForm
from climbz import db
from climbz.blueprints.utils import render


sessions = Blueprint("sessions", __name__)


@sessions.route("/sessions")
def table_sessions() -> str:
    sessions = Session.query.filter_by(climber_id=current_user.id).all()
    return render("sessions.html", title="Sessions", sessions=sessions)


@sessions.route("/session/<int:session_id>")
def page_session(session_id: int) -> str:
    return render("session.html", session=Session.query.get(session_id))


@sessions.route("/stop_session", methods=["GET", "POST"])
def stop_session() -> str:
    flask_session["session_id"] = -1
    flask_session["project_ids"] = list()
    return redirect(flask_session.pop("call_from_url"))


@sessions.route("/reopen_session/<int:session_id>", methods=["GET", "POST"])
def reopen_session(session_id: int) -> str:
    flask_session["session_id"] = session_id
    return redirect(flask_session.pop("call_from_url"))


@sessions.route("/add_session", methods=["GET", "POST"])
def add_session() -> str:
    session_form = SessionForm.create_empty()

    # POST: a session form was submitted => create session or return error
    if request.method == "POST":
        if not session_form.validate():
            flask_session["error"] = session_form.errors
            return render("form.html", title="Add session", forms=[session_form])

        # if new_area, create new area; otherwise, get existing area
        area = session_form.get_area()
        if area is not None and area.id is None:
            db.session.add(area)
            db.session.commit()

        # create session
        session = session_form.get_object(area.id)
        db.session.add(session)
        db.session.commit()
        flask_session["session_id"] = session.id
        return redirect("/")

    # GET: the user wants to start a session
    return render("form.html", title="Add session", forms=[session_form])


@sessions.route("/edit_session/<int:session_id>", methods=["GET", "POST"])
def edit_session(session_id: int) -> str:
    session = Session.query.get(session_id)

    # POST: a session form was submitted => create session or return error
    if request.method == "POST":
        session_form = SessionForm.create_empty(is_edit=True)
        if not session_form.validate():
            flask_session["error"] = session_form.errors
            return render("form.html", title="Edit session", forms=[session_form])

        # edit session with the new data
        session = session_form.get_object(session.area_id, session)
        db.session.commit()
        return redirect(flask_session.pop("call_from_url"))

    # GET: the user wants to edit the session
    session_form = SessionForm.create_from_object(session)
    return render("form.html", title="Edit session", forms=[session_form])


@sessions.route("/delete_session/<int:session_id>", methods=["GET", "POST"])
def delete_session(session_id: int) -> str:
    session = Session.query.get(session_id)
    db.session.delete(session)
    db.session.commit()
    return redirect(flask_session.pop("call_from_url"))
