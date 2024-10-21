from flask import (
    Blueprint,
    redirect,
    request,
    session as flask_session,
)
from flask_login import current_user

from climbz.models import Session
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
    session = Session.query.get(session_id)
    return render(
        "session.html", title=f"Session on {session.area.name}", session=session
    )


@sessions.route("/stop_session", methods=["GET", "POST"])
def stop_session() -> str:
    if flask_session["session_id"] == "project_search":
        del flask_session["area_id"]
    del flask_session["session_id"]
    return redirect(flask_session.pop("call_from_url"))


@sessions.route("/reopen_session/<int:session_id>", methods=["GET", "POST"])
def reopen_session(session_id: int) -> str:
    flask_session["session_id"] = session_id
    return redirect(flask_session.pop("call_from_url"))


@sessions.route("/add_session", methods=["GET", "POST"])
def add_session() -> str:
    session_form = SessionForm.create_empty()
    title = "Add session"

    # POST: a session form was submitted => create session or return error
    if request.method == "POST":
        if not session_form.validate():
            flask_session["error"] = "An error occurred. Fix it and resubmit."
            return render("form.html", title=title, forms=[session_form])

        # if new_area, create new area; otherwise, get existing area
        area = session_form.get_area()
        if area.id is None:
            db.session.add(area)
            db.session.commit()

        # create session if this is not a project search; otherwise save the area
        if session_form.is_project_search.data:
            flask_session["session_id"] = "project_search"
            flask_session["area_id"] = area.id
        else:
            session = session_form.get_object(area.id)
            db.session.add(session)
            db.session.commit()
            flask_session["session_id"] = session.id
        return redirect("/")

    # GET: the user wants to start a session
    return render("form.html", title=title, forms=[session_form])


@sessions.route("/edit_session/<int:session_id>", methods=["GET", "POST"])
def edit_session(session_id: int) -> str:
    session = Session.query.get(session_id)
    title = f"Edit session on {session.area.name}"

    # POST: a session form was submitted => create session or return error
    if request.method == "POST":
        session_form = SessionForm.create_empty(is_edit=True)
        if not session_form.validate():
            flask_session["error"] = "An error occurred. Fix it and resubmit."
            return render("form.html", title=title, forms=[session_form])

        # edit session with the new data
        session = session_form.edit_object(session)
        db.session.commit()
        return redirect(flask_session.pop("call_from_url"))

    # GET: the user wants to edit the session
    session_form = SessionForm.create_from_object(session)
    return render("form.html", title=title, forms=[session_form])


@sessions.route("/delete_session/<int:session_id>", methods=["GET", "POST"])
def delete_session(session_id: int) -> str:
    session = Session.query.get(session_id)
    db.session.delete(session)
    db.session.commit()
    last_url = flask_session.pop("call_from_url")
    if last_url.endswith(f"/session/{session_id}"):
        return redirect("/")
    else:
        return redirect(last_url)
