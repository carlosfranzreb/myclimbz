import os
from time import time

from flask import (
    Blueprint,
    render_template,
    redirect,
    request,
    session as flask_session,
)
import whisper
from datetime import datetime

from climbs.ner import transcribe, parse_climb, ClimbsModel
from climbs.models import Area, Climb, RockType, Route, Session
from climbs.forms import SessionForm
from climbs import db


# ASR_MODEL = whisper.load_model("base")
# NER_MODEL = ClimbsModel.load_from_checkpoint(
#     "climbs/ner/checkpoints/ner-0.ckpt", map_location="cpu"
# )

home = Blueprint("home", __name__)


@home.route("/")
def page_home() -> str:
    return render_template("index.html", title="Home")


@home.route("/upload", methods=["GET", "POST"])
def upload_audio():
    # audio_file = request.files["audioFile"]
    # os.makedirs("audios", exist_ok=True)

    return process_audio("audios/1698660651.webm")  # TODO

    # if audio_file:
    #     # Create a unique filename using Unix timestamp
    #     timestamp = str(int(time()))
    #     filename = os.path.join("audios", f"{timestamp}.webm")
    #     audio_file.save(filename)
    #     return process_audio(filename)


def process_audio(filename: str) -> str:
    # transcript = transcribe(ASR_MODEL, filename)
    transcript = "On January 18th I climbed in La Faka, where there is granite, the conditions were a 7."
    # entities = parse_climb(NER_MODEL, transcript)
    entities = {
        "AREA": "La Faka",
        "ROCK": "granite",
        "CONDITIONS": 7,
        "DATE": "January 18th 2023",
    }
    entities["DATE"] = datetime.strptime(entities["DATE"], "%B %dth %Y")
    flask_session["entities"] = entities

    if "AREA" in entities:
        # redirect to add_session
        return redirect("/add_session")
    else:
        return redirect("/add_climb")


@home.route("/add_session", methods=["GET", "POST"])
def add_session() -> str:
    # if POST, i.e. a session form was submitted
    if request.method == "POST":
        session_form = SessionForm(request.form)

        # TODO: these error catches are not working
        # new_area and existing_area are mutually exclusive
        if not session_form.existing_area.data and not session_form.new_area.data:
            return render_template(
                "session_form.html",
                session_form=session_form,
                error="Please enter an area",
            )
        if session_form.existing_area.data and session_form.new_area.data:
            return render_template(
                "session_form.html",
                session_form=session_form,
                error="Please enter only one area",
            )

        # if new_area, create new area; otherwise, get existing area
        if session_form.new_area.data != "":
            area = Area(name=session_form.new_area.data)
            if session_form.rock_type.data != "":
                rock_type = RockType.query.get(session_form.rock_type.data)
                area.rock_type = rock_type
            db.session.add(area)
            db.session.commit()
        else:
            area = Area.query.get(session_form.existing_area.data)

        session_form.area = area
        session = Session(**session_form.data)
        db.session.add(session)
        db.session.commit()
        return redirect("/")

    # if GET, i.e. a recording was uploaded
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


def add_climb() -> str:
    pass


def get_area(entities: dict) -> Area:
    area = Area.query.filter_by(name=entities["AREA"]).first()
    if area is None:
        if "ROCK" in entities:
            rock_type = RockType.query.filter_by(name=entities["ROCK"]).first()
            area = Area(name=entities["AREA"], rock_type=rock_type)
        else:
            area = Area(name=entities["AREA"])
    return area
