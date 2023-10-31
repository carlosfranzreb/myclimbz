import os
from time import time

from flask import Blueprint, render_template, request
import whisper
from parsedatetime import Calendar
from datetime import datetime

from climbs.ner import transcribe, parse_climb, ClimbsModel
from climbs.models import Area, Climb, RockType, Route, Session
from climbs.forms import SessionForm
from climbs import db


# ASR_MODEL = whisper.load_model("base")
NER_MODEL = ClimbsModel.load_from_checkpoint(
    "climbs/ner/checkpoints/ner-0.ckpt", map_location="cpu"
)

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
    transcript = "On January 18th I climbed in La Pedriza, where there is granite, the conditions were a 7."
    entities = parse_climb(NER_MODEL, transcript)

    if "AREA" in entities:
        return add_session(entities)
    else:
        return add_climb(entities)


@home.route("/add_session", methods=["GET", "POST"])
def add_session(entities: dict) -> str:
    if request.method == "POST":
        session_form = SessionForm(request.form)
        if session_form.new_area.data != "":
            # create new area and set as area attribute in form
            pass
        else:
            # set existing area as area attribute in form
            pass
        session = Session(**session_form.data)
        db.session.add(session)
        db.session.commit()
        return render_template("index.html", title="Home")

    area = Area.query.filter_by(name=entities["AREA"]).first()
    if area is None:
        if "ROCK" in entities:
            rock_type = RockType.query.filter_by(name=entities["ROCK"]).first()
            if rock_type is None:
                rock_type = RockType(name=entities["ROCK"])
                db.session.add(rock_type)
            area = Area(name=entities["AREA"], rock_type=rock_type)
        else:
            area = Area(name=entities["AREA"])
        db.session.add(area)
        db.session.commit()
        entities["AREA"] = area

    if "DATE" in entities:
        cal = Calendar()
        parsed_date = cal.parse(entities["DATE"])
        date = datetime(*parsed_date[0][:6])
        entities["DATE"] = date

    entities["AREA_ID"] = area.id
    del entities["AREA"]
    if "ROCK" in entities:
        del entities["ROCK"]

    entities = {k.lower(): v for k, v in entities.items()}
    session = Session(**entities)
    session_form = SessionForm(obj=session)
    session_form.existing_area.choices = [(a.id, a.name) for a in Area.query.all()]
    return render_template("session_form.html", session_form=session_form)


def add_climb(entities: dict) -> str:
    pass
