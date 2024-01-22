import os
from time import time
import json

from flask import (
    Blueprint,
    render_template,
    redirect,
    request,
    session as flask_session,
)
import whisper

from climbs.ner import transcribe, parse_climb, ClimbsModel
from climbs.ner.entities_to_objects import get_route_from_entities
from climbs.models import Area, Climb, Session, Sector, Predictions, Route, Grade
from climbs.forms import ClimbForm, SessionForm, RouteForm
from climbs import db


ASR_MODEL = whisper.load_model("small.en")
NER_MODEL = ClimbsModel.load_from_checkpoint(
    "climbs/ner/checkpoints/ner-0.ckpt", map_location="cpu"
)

home = Blueprint("home", __name__)


@home.route("/", methods=["GET", "POST"])
def page_home() -> str:
    current_session_id = flask_session.get("session_id", -1)
    project_search = flask_session.get("project_search", False)

    routes_dict = [route.as_dict() for route in Route.query.all()]
    grades_dict = [grade.as_dict() for grade in Grade.query.all()]

    # POST: an audio file was uploaded
    if request.method == "POST":
        try:
            audio_file = request.files["audioFile"]
        except KeyError:
            flask_session["error"] = "No audio file was uploaded."
            return redirect("/")

        timestamp = str(int(time()))
        filename = os.path.join("audios", f"{timestamp}.webm")
        audio_file.save(filename)
        transcript = transcribe(ASR_MODEL, filename)
        entities = parse_climb(NER_MODEL, transcript)

        flask_session["entities"] = entities
        flask_session["predictions"] = {
            "audiofile": filename,
            "transcript": transcript,
        }

        if project_search is True or current_session_id > 0:
            return redirect("/add_climb")
        else:
            return redirect("/add_session")

    # GET: no audio file was uploaded => show home page
    if project_search is True:
        area = Area.query.get(flask_session["area_id"])
        project_ids = flask_session.get("project_ids", [])
        projects = [Route.query.get(pid) for pid in project_ids]
        return render_template(
            "index.html",
            title="Home",
            session_started=False,
            project_search_started=True,
            area_name=area.name,
            projects=projects,
            error=flask_session.pop("error", None),
            routes=routes_dict,
            grades=grades_dict,
        )
    else:
        if current_session_id > 0:
            last_session = Session.query.get(current_session_id)
        else:
            # get the session with the largest ID
            last_session = Session.query.order_by(Session.id.desc()).first()
        return render_template(
            "index.html",
            title="Home",
            session_started=current_session_id > 0,
            last_session=last_session,
            error=flask_session.pop("error", None),
            routes=routes_dict,
            grades=grades_dict,
        )


@home.route("/stop_session", methods=["GET", "POST"])
def stop_session() -> str:
    flask_session["session_id"] = -1
    flask_session["area_id"] = -1
    flask_session["project_search"] = False
    flask_session["project_ids"] = list()
    return redirect("/")


@home.route("/reopen_session/<int:session_id>", methods=["GET", "POST"])
def reopen_session(session_id: int) -> str:
    flask_session["session_id"] = session_id
    flask_session["area_id"] = Session.query.get(session_id).area_id
    return redirect("/")


@home.route("/add_session", methods=["GET", "POST"])
def add_session() -> str:
    area_names = [area.name for area in Area.query.order_by(Area.name).all()]
    session_form = SessionForm.create_empty()

    # POST: a session form was submitted => create session or return error
    if request.method == "POST":
        if not session_form.validate():
            return render_template(
                "add_session.html",
                session_form=session_form,
                error=session_form.errors,
            )
        # if new_area, create new area; otherwise, get existing area
        area = session_form.get_area()
        if area is not None and area.id is None:
            db.session.add(area)
            db.session.commit()
            flask_session["predictions"]["area_id"] = area.id
        area_id = area.id if area is not None else None

        # create session if this is not a project search
        if session_form.is_project_search.data is False:
            session = Session(
                **{
                    "area_id": area_id,
                    "conditions": session_form.conditions.data,
                    "date": session_form.date.data,
                }
            )
            db.session.add(session)
            db.session.commit()
            flask_session["predictions"]["session_id"] = session.id
            flask_session["session_id"] = session.id
        else:
            flask_session["project_search"] = True

        dump_predictions()
        flask_session["area_id"] = area_id
        return redirect("/")

    # GET: the user has uploaded a recording or wants to start a session
    if "entities" not in flask_session:
        flask_session["entities"] = dict()
    session_form = SessionForm.create_from_entities(flask_session["entities"])
    return render_template(
        "add_session.html",
        session_form=session_form,
        area_names=area_names,
    )


@home.route("/add_climb", methods=["GET", "POST"])
def add_climb() -> str:
    # define the grade scale
    entities = flask_session["entities"]
    grade_scale = "font"
    for field in ["grade", "grade_felt"]:
        if field in entities:
            grade_scale = "hueco" if entities[field][0] == "V" else "font"
            break

    # create forms and add choices
    climb_form = None if flask_session.get("project_search", False) else ClimbForm()
    route_form = RouteForm.create_empty(grade_scale=grade_scale)

    # POST: a climb form was submitted => create climb or return error
    if request.method == "POST":
        invalid_climb = not climb_form.validate() if climb_form is not None else False
        if not route_form.validate() or invalid_climb:
            return render_template(
                "add_climb.html",
                climb_form=climb_form,
                route_form=route_form,
                error=route_form.errors or climb_form.errors,
            )

        # create new sector and new route if necessary
        sector = route_form.get_sector(flask_session["area_id"])
        if sector.id is None:
            db.session.add(sector)
            db.session.commit()
            flask_session["predictions"]["sector_id"] = sector.id

        route = route_form.get_route_from_climb_form(sector)
        if route is not None and route.id is None:
            db.session.add(route)
            db.session.commit()
            flask_session["predictions"]["route_id"] = route.id
        if flask_session.get("project_search", False) is True:
            if "project_ids" not in flask_session:
                flask_session["project_ids"] = list()
            flask_session["project_ids"].append(route.id)

        # create climb if this is not a project
        if flask_session.get("project_search", False) is False:
            climb = Climb(
                **{
                    "n_attempts": climb_form.n_attempts.data,
                    "sent": climb_form.sent.data,
                    "route_id": route.id if route is not None else None,
                    "session_id": flask_session["session_id"],
                }
            )
            db.session.add(climb)
            db.session.commit()
            flask_session["predictions"]["climb_id"] = climb.id

        dump_predictions()
        return redirect("/")

    # GET: a recording was uploaded => create forms
    if flask_session.get("project_search", False) is True:
        climb_form = None
    else:
        climb_form = ClimbForm(
            n_attempts=entities.get("n_attempts", None), sent=entities["sent"]
        )

    route = get_route_from_entities(entities, flask_session["area_id"])
    if route.id is None:
        route_form = RouteForm.create_from_entities(entities, grade_scale)
    else:
        route_form = RouteForm.create_empty(grade_scale)
        route_form.name.data = route.name

    # if no sector was found, add the last sector of the current session if possible
    if route.sector_id is None and flask_session.get("session_id", False) > 0:
        session = Session.query.get(flask_session["session_id"])
        sectors = [c.route.sector for c in session.climbs]
        if len(sectors) > 0:
            route_form.sector.data = sectors[-1].name

    # get existing sectors and routes
    sectors = (
        Sector.query.filter_by(area_id=flask_session["area_id"])
        .order_by(Sector.name)
        .all()
    )
    sector_names = [sector.name for sector in sectors]
    routes = list()
    for sector in sectors:
        routes += sector.routes
    route_names = sorted([route.name for route in routes])

    return render_template(
        "add_climb.html",
        route_form=route_form,
        climb_form=climb_form,
        route_names=route_names,
        sector_names=sector_names,
    )


def dump_predictions() -> None:
    predictions = Predictions(**flask_session["predictions"])
    predictions.entities = json.dumps(
        {k: v for k, v in flask_session["entities"].items() if k != "date"}
    )
    db.session.add(predictions)
    db.session.commit()
    flask_session["predictions"] = None
