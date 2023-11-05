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
from climbs.forms import ClimbForm, SessionForm, RouteForm
from climbs import db


ASR_MODEL = whisper.load_model("tiny")
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
    area_names = [area.name for area in Area.query.order_by(Area.name).all()]
    session_form = SessionForm()
    session_form.add_choices()

    # POST: a session form was submitted => create session or return error
    if request.method == "POST":
        if not session_form.validate():
            return render_template(
                "add_session.html",
                session_form=session_form,
                error=session_form.errors,
            )
        # if new_area, create new area; otherwise, get existing area
        area = None
        if len(session_form.area.data) > 0:
            area_name = session_form.area.data.strip()
            area = Area.query.filter_by(name=area_name).first()
            if area is None:
                if session_form.rock_type.data != "":
                    rock_type = RockType.query.get(session_form.rock_type.data)
                    area = Area(name=area_name, rock_type=rock_type)
                else:
                    area = Area(name=area_name)
                db.session.add(area)
                db.session.commit()

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
    session_form.add_choices()
    session_form.area.data = area.name

    if area.id is None and "rock" in entities:
        rock_id = RockType.query.filter_by(name=entities["rock"]).first().id
        session_form.rock_type.data = str(rock_id)
    else:
        session_form.rock_type.data = "0"

    return render_template(
        "add_session.html",
        session_form=session_form,
        area_names=area_names,
    )


@home.route("/add_climb", methods=["GET", "POST"])
def add_climb() -> str:
    # create form and add choices
    entities = flask_session["entities"]
    route = get_route(entities)
    climb_form = ClimbForm()
    route_form = RouteForm()
    grade_scale = "font"
    for field in ["GRADE", "GRADE_FELT"]:
        if field in entities:
            grade_scale = "hueco" if entities[field][0] == "V" else "font"
    route_form.add_choices(grade_scale)

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
        sector = None
        if len(route_form.sector.data) > 0:
            sector_name = route_form.sector.data.strip()
            sector = Sector.query.filter_by(name=sector_name).first()
            if sector is None:
                sector = Sector(name=sector_name, area_id=flask_session["area_id"])
                db.session.add(sector)
                db.session.commit()

        route = Route.query.filter_by(name=route_form.name.data.strip()).first()
        if route is None:
            route = Route(name=route_form.name.data.strip(), sector=sector)
            for field in [
                "height",
                "inclination",
                "landing",
                "sit_start",
                "grade",
                "grade_felt",
            ]:
                setattr(route, field, getattr(route_form, field).data)

            for crux_id in route_form.cruxes.data:
                crux = Crux.query.get(crux_id)
                route.cruxes.append(crux)

            db.session.add(route)
            db.session.commit()

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
    climb_form = ClimbForm(n_attempts=entities["N_ATTEMPTS"], sent=entities["SENT"])
    if route.id is None:
        route_form = RouteForm()
        route_form.add_choices(grade_scale)
        route_form.populate_from_entities(entities, grade_scale)
    else:
        route_form = RouteForm()
        route_form.name.data = route.name
        route_form.add_choices(grade_scale)

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
            if sector is None:
                sector = Sector(
                    name=entities["SECTOR"], area_id=flask_session["area_id"]
                )
        cruxes = list()
        if "CRUX" in entities:
            for crux_name in entities["CRUX"]:
                cruxes.append(Crux.query.filter_by(name=crux_name).first())
        route = Route(name=entities["NAME"], sector=sector)
    return route
