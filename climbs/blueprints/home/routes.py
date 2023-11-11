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
from climbs.models import Area, Climb, Session, Sector, Predictions
from climbs.forms import ClimbForm, SessionForm, RouteForm
from climbs import db


ASR_MODEL = whisper.load_model("small.en")
NER_MODEL = ClimbsModel.load_from_checkpoint(
    "climbs/ner/checkpoints/ner-0.ckpt", map_location="cpu"
)

home = Blueprint("home", __name__)


@home.route("/", methods=["GET", "POST"])
def page_home() -> str:
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
        flask_session["predictions"] = Predictions(
            audiofile=filename,
            transcript=transcript,
            entities=json.dumps({k: v[0] for k, v in entities.items() if k != "date"}),
        )

        if "area" in entities:
            return redirect("/add_session")
        else:
            return redirect("/add_climb")

    current_session_id = flask_session.get("session_id", -1)
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
    )


@home.route("/stop_session", methods=["GET", "POST"])
def stop_session() -> str:
    flask_session["session_id"] = -1
    flask_session["area_id"] = -1
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
            flask_session["predictions"].area_id = area.id
        area_id = area.id if area is not None else None

        # create session
        session = Session(
            **{
                "area_id": area_id,
                "conditions": session_form.conditions.data,
                "date": session_form.date.data,
            }
        )
        db.session.add(session)
        db.session.commit()

        # dump predictions to DB
        flask_session["predictions"].session_id = session.id
        db.session.add(flask_session["predictions"])
        db.session.commit()
        flask_session["predictions"] = None

        flask_session["session_id"] = session.id
        flask_session["area_id"] = area_id
        return redirect("/")

    # GET: a recording was uploaded => create session form
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
    climb_form = ClimbForm()
    route_form = RouteForm.create_empty(grade_scale=grade_scale)

    # POST: a climb form was submitted => create climb or return error
    if request.method == "POST":
        if not route_form.validate() or not climb_form.validate():
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
            flask_session["predictions"].sector_id = sector.id

        route = route_form.get_route(sector)
        if route is not None and route.id is None:
            db.session.add(route)
            db.session.commit()
            flask_session["predictions"].route_id = route.id

        # create climb
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

        # dump predictions to DB
        flask_session["predictions"].climb_id = climb.id
        db.session.add(flask_session["predictions"])
        db.session.commit()
        flask_session["predictions"] = None

        return redirect("/")

    # GET: a recording was uploaded => create forms
    climb_form = ClimbForm(
        n_attempts=entities.get("n_attempts", None), sent=entities["sent"]
    )
    route = get_route_from_entities(entities, flask_session["area_id"])
    if route.id is None:
        route_form = RouteForm.create_from_entities(entities, grade_scale)
    else:
        route_form = RouteForm.create_empty(grade_scale)
        route_form.name.data = route.name

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
