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
from climbs.models import Area, Climb, RockType, Route, Session
from climbs.forms import SessionForm
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
    return redirect("/")


@home.route("/add_session", methods=["GET", "POST"])
def add_session() -> str:
    # POST: a session form was submitted
    if request.method == "POST":
        session_form = SessionForm(request.form)

        # new_area and existing_area are mutually exclusive
        existing_area = session_form.existing_area.data != "0"
        new_area = len(session_form.new_area.data) > 0
        if not (existing_area or new_area):
            return render_template(
                "session_form.html",
                session_form=session_form,
                error="Please enter an area",
            )
        elif existing_area and new_area:
            return render_template(
                "session_form.html",
                session_form=session_form,
                error="Please enter only one area",
            )
        # new_area name must be unique
        elif new_area and not existing_area:
            area = Area.query.filter_by(name=session_form.new_area.data.strip()).first()
            if area is not None:
                return render_template(
                    "session_form.html",
                    session_form=session_form,
                    error="Area name already exists",
                )

        # if new_area, create new area; otherwise, get existing area
        if new_area:
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
        return redirect("/")

    # GET: a recording was uploaded
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
    # POST: a climb form was submitted
    if request.method == "POST":
        session_form = ClimbForm(request.form)

        # new_area and existing_area are mutually exclusive
        existing_area = session_form.existing_area.data != "0"
        new_area = len(session_form.new_area.data) > 0
        if not (existing_area or new_area):
            return render_template(
                "session_form.html",
                session_form=session_form,
                error="Please enter an area",
            )
        elif existing_area and new_area:
            return render_template(
                "session_form.html",
                session_form=session_form,
                error="Please enter only one area",
            )
        # new_area name must be unique
        elif new_area and not existing_area:
            area = Area.query.filter_by(name=session_form.new_area.data.strip()).first()
            if area is not None:
                return render_template(
                    "session_form.html",
                    session_form=session_form,
                    error="Area name already exists",
                )

        # if new_area, create new area; otherwise, get existing area
        if new_area:
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
        return redirect("/")

    # GET: a recording was uploaded
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


def get_area(entities: dict) -> Area:
    area = Area.query.filter_by(name=entities["AREA"]).first()
    if area is None:
        if "ROCK" in entities:
            rock_type = RockType.query.filter_by(name=entities["ROCK"]).first()
            area = Area(name=entities["AREA"], rock_type=rock_type)
        else:
            area = Area(name=entities["AREA"])
    return area
