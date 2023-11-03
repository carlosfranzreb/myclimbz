import os
from time import time

from flask import (
    Blueprint,
    render_template,
    url_for,
    redirect,
    request,
    session as flask_session,
    jsonify,
)
import whisper
from datetime import datetime

from climbs.ner import transcribe, parse_climb, ClimbsModel
from climbs.models import Area, Climb, Crux, Grade, RockType, Route, Session, Sector
from climbs.forms import ClimbForm, SessionForm
from climbs import db


ASR_MODEL = whisper.load_model("base")
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

        if "AREA" in entities:
            return redirect("/add_session")
        else:
            return redirect("/add_climb")
    return render_template(
        "index.html",
        title="Home",
        session_started=flask_session.get("session_id", -1) > 0,
        error=flask_session.pop("error", None),
    )


@home.route("/stop_session", methods=["GET", "POST"])
def stop_session() -> str:
    flask_session["session_id"] = -1
    flask_session["area_id"] = -1
    return redirect("/")


@home.route("/add_session", methods=["GET", "POST"])
def add_session() -> str:
    # POST: a session form was submitted => create session or return error
    if request.method == "POST":
        session_form = SessionForm(request.form)
        if not session_form.validate():
            return render_template(
                "session_form.html",
                session_form=session_form,
                error=session_form.errors,
            )
        # if new_area, create new area; otherwise, get existing area
        if session_form.new_area.data:
            area = Area(name=session_form.new_area.data.strip())
            if session_form.rock_type.data != "":
                rock_type = RockType.query.get(session_form.rock_type.data)
                area.rock_type = rock_type
            db.session.add(area)
            db.session.commit()
        else:
            area = Area.query.get(session_form.existing_area.data)

        # create session
        session = Session(
            **{
                "area_id": area.id,
                "conditions": session_form.conditions.data,
                "date": session_form.date.data,
            }
        )
        db.session.add(session)
        db.session.commit()
        flask_session["session_id"] = session.id
        flask_session["area_id"] = area.id
        return redirect("/")

    # GET: a recording was uploaded => create session form
    entities = flask_session["entities"]
    area = get_area(entities)
    entities["AREA_ID"] = area.id
    del entities["AREA"]
    entities = {k.lower(): v for k, v in entities.items()}

    session = Session(**{k: v for k, v in entities.items() if k != "rock"})
    session_form = SessionForm(obj=session)
    session_form.rock_type.choices = [(r.id, r.name) for r in RockType.query.all()]
    session_form.existing_area.choices = [(a.id, a.name) for a in Area.query.all()]
    session_form.existing_area.choices.insert(0, (0, ""))
    session_form.rock_type.choices.insert(0, (0, ""))

    if area.id is None:
        session_form.new_area.data = area.name
        session_form.existing_area.data = 0
        if "rock" in entities:
            rock_id = RockType.query.filter_by(name=entities["rock"]).first().id
            session_form.rock_type.data = str(rock_id)
    else:
        session_form.existing_area.data = str(area.id)
        session_form.rock_type.data = "0"

    return render_template("session_form.html", session_form=session_form)


@home.route("/add_climb", methods=["GET", "POST"])
def add_climb() -> str:
    # POST: a climb form was submitted => create climb or return error
    if request.method == "POST":
        climb_form = ClimbForm(request.form)
        if not climb_form.validate():
            return render_template(
                "climb_form.html", climb_form=climb_form, error=climb_form.errors
            )

        # create new sector and new route if necessary
        new_sector_data = climb_form.new_sector.data.strip()
        existing_sector_data = climb_form.existing_sector.data
        sector = None
        if new_sector_data:
            sector = Sector(
                name=new_sector_data,
                area_id=flask_session["area_id"],
            )
            db.session.add(sector)
            db.session.commit()
        elif existing_sector_data:
            sector = Sector.query.get(existing_sector_data)

        if climb_form.new_route.data:
            route = Route(name=climb_form.new_route.data.strip(), sector=sector)
            for field in [
                "grade_id",
                "grade_felt_id",
                "height",
                "inclination",
                "landing",
                "sit_start",
                "send",
            ]:
                setattr(route, field, getattr(climb_form, field).data)
            for crux_id in climb_form.cruxes.data:
                crux = Crux.query.get(crux_id)
                route.cruxes.append(crux)
            db.session.add(route)
            db.session.commit()
        else:
            route = Route.query.get(climb_form.existing_route.data)

        # create climb
        session = Climb(
            **{
                "n_attempts": climb_form.n_attempts.data,
                "sent": climb_form.sent.data,
                "route_id": route.id,
                "session_id": flask_session["session_id"],
            }
        )
        db.session.add(session)
        db.session.commit()
        return redirect("/")

    # GET: a recording was uploaded => create climb form
    entities = flask_session["entities"]
    route = get_route(entities)
    entities["ROUTE_ID"] = route.id
    del entities["NAME"]

    climb = Climb(route_id=route.id, session_id=flask_session["session_id"])
    if "N_TRIES" in entities:
        climb.n_attempts = entities["N_TRIES"]
        del entities["N_TRIES"]
    climb_form = ClimbForm(obj=route)

    # add existing routes and sectors
    area_id = flask_session["area_id"]
    routes = Route.query.filter_by(area_id=area_id).order_by(Route.name).all()
    climb_form.existing_route.choices = [(r.id, r.name) for r in routes]
    sectors = Sector.query.filter_by(area_id=area_id).order_by(Sector.name).all()
    climb_form.existing_sector.choices = [(s.id, s.name) for s in sectors]

    # add grade options
    grades = Grade.query.order_by(Grade.level).all()
    for field in ["grade", "grade_felt"]:
        getattr(climb_form, field).choices = [(g.id, g.level) for g in grades]
        getattr(climb_form, field).choices.insert(0, (0, ""))

    # if new_route, fill in all route fields when found in entities
    # lowercase all keys in entities
    entities = {k.lower(): v for k, v in entities.items()}
    if route.id is None:
        climb_form.new_route.data = route.name
        for field in ["grade", "grade_felt"]:
            value = entities.get(field, None)
            if value is not None:
                grade = Grade.query.filter_by(level=value).first()
                getattr(climb_form, field).data = grade.id
            else:
                getattr(climb_form, field).data = 0
        for field in ["height", "inclination", "landing", "sit_start", "send"]:
            if field is not entities:
                setattr(climb_form, field, entities[field])

    return render_template("climb_form.html", climb_form=climb_form)


def get_area(entities: dict) -> Area:
    area = Area.query.filter_by(name=entities["AREA"]).first()
    if area is None:
        if "ROCK" in entities:
            rock_type = RockType.query.filter_by(name=entities["ROCK"]).first()
            area = Area(name=entities["AREA"], rock_type=rock_type)
        else:
            area = Area(name=entities["AREA"])
    return area


def get_route(entities: dict) -> Route:
    route = Route.query.filter_by(name=entities["NAME"]).first()
    if route is None:
        sector = None
        if "SECTOR" in entities:
            sector = Sector.query.filter_by(name=entities["SECTOR"]).first()
        cruxes = list()
        if "CRUX" in entities:
            for crux_name in entities["CRUX"]:
                cruxes.append(Crux.query.filter_by(name=crux_name).first())
        route = Route(name=entities["NAME"], sector=sector)
    return route
