from flask import (
    Blueprint,
    redirect,
    request,
    session as flask_session,
)

from climbz.models import Area, Session
from climbz.forms import SessionForm
from climbz import db
from climbz.ner.tracking import dump_predictions
from climbz.blueprints.render import render


sessions = Blueprint("sessions", __name__)


@sessions.route("/sessions")
def table_sessions() -> str:
    flask_session["call_from_url"] = "/sessions"
    return render("sessions.html", title="Sessions", sessions=Session.query.all())


@sessions.route("/session/<int:session_id>")
def page_session(session_id: int) -> str:
    session = Session.query.get(session_id)
    flask_session["call_from_url"] = f"/session/{session_id}"
    return render("session.html", session=session)


@sessions.route("/stop_session", methods=["GET", "POST"])
def stop_session() -> str:
    flask_session["session_id"] = -1
    flask_session["project_ids"] = list()
    return redirect("/")


@sessions.route("/reopen_session/<int:session_id>", methods=["GET", "POST"])
def reopen_session(session_id: int) -> str:
    flask_session["session_id"] = session_id
    return redirect(flask_session.pop("call_from_url"))


@sessions.route("/add_session", methods=["GET", "POST"])
def add_session() -> str:
    # POST: a session form was submitted => create session or return error
    if request.method == "POST":
        session_form = SessionForm.create_empty()
        if not session_form.validate():
            flask_session["error"] = session_form.errors
            return render("add_session.html", session_form=session_form)

        # if new_area, create new area; otherwise, get existing area
        area = session_form.get_area()
        if area is not None and area.id is None:
            db.session.add(area)
            db.session.commit()
            flask_session["predictions"]["area_id"] = area.id
        area_id = area.id if area is not None else None

        # create session
        session = session_form.get_object(area_id)
        db.session.add(session)
        db.session.commit()
        flask_session["session_id"] = session.id
        if "predictions" in flask_session:
            flask_session["predictions"]["session_id"] = session.id
            dump_predictions()

        flask_session.pop("entities", None)
        return redirect("/")

    # GET: the user has uploaded a recording or wants to start a session
    if "entities" not in flask_session:
        flask_session["entities"] = dict()
    session_form = SessionForm.create_from_entities(flask_session["entities"])

    return render(
        "add_session.html",
        session_form=session_form,
        area_names=[area.name for area in Area.query.order_by(Area.name).all()],
    )


@sessions.route("/edit_session/<int:session_id>", methods=["GET", "POST"])
def edit_session(session_id: int) -> str:
    session = Session.query.get(session_id)

    # POST: a session form was submitted => create session or return error
    if request.method == "POST":
        session_form = SessionForm.create_empty()
        if not session_form.validate():
            flask_session["error"] = session_form.errors
            return render("add_session.html", session_form=session_form)

        # if new_area, create new area; otherwise, get existing area
        area = session_form.get_area()
        if area is not None and area.id is None:
            db.session.add(area)
            db.session.commit()
        area_id = area.id if area is not None else None

        # edit session with the new data
        session = session_form.get_object(area_id, session)
        db.session.commit()
        return redirect(flask_session.pop("call_from_url"))

    # GET: the user wants to edit the session
    session_form = SessionForm.create_from_object(session)
    return render(
        "add_session.html",
        session_form=session_form,
        area_names=[area.name for area in Area.query.order_by(Area.name).all()],
    )


@sessions.route("/delete_session/<int:session_id>", methods=["GET", "POST"])
def delete_session(session_id: int) -> str:
    session = Session.query.get(session_id)
    db.session.delete(session)
    db.session.commit()
    return redirect(flask_session.pop("call_from_url"))
