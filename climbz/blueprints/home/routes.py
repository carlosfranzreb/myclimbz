import os
from time import time

from flask import (
    Blueprint,
    redirect,
    request,
    session as flask_session,
)
from flask_login import current_user
import whisper
import pandas as pd

from climbz.ner import transcribe, parse_climb, ClimbsModel
from climbz.models import Grade, Climber
from climbz.blueprints.utils import render
from climbz.blueprints.climbs import routes as climbs_route
from climbz.blueprints.sessions import routes as sessions_route
from climbz.forms.session import SessionForm
from climbz import db


ASR_MODEL = whisper.load_model("tiny")
NER_MODEL = ClimbsModel.load_from_checkpoint(
    "climbz/ner/checkpoints/ner-0.ckpt", map_location="cpu"
)

home = Blueprint("home", __name__)


@home.route("/", methods=["GET", "POST"])
def page_home() -> str:
    current_session_id = flask_session.get("session_id", -1)

    # POST: an audio file was uploaded
    if request.method == "POST":
        try:
            data_type = request.form["data_type"]
        except KeyError:
            flask_session["error"] = "No file was uploaded."
            return redirect("/")
        if data_type == "audio":
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

            if current_session_id > 0:
                return redirect("/add_climb")
            else:
                return redirect("/add_session")

        elif data_type == "csv":
            csv_json = request.form["csv_data"]
            # group climbs by date and area
            climbs = pd.read_json(csv_json)
            climbs_by_date = climbs.groupby("dates")
            for date, climbs in climbs_by_date:
                climbs_by_area = climbs.groupby("area")
                for area, climbs in climbs_by_area:
                    # TODO:create a session
                    session_form = SessionForm.create_empty()
                    session_form.area.data = area
                    area_obj = session_form.get_area()
                    session_form.date.data = date
                    sessions_route.add_session()
                    # TODO: What to do about conditions in sessions

                    for climb in climbs.itertuples():
                        # TODO: add necessary info to entities.
                        climbs_route.add_climb()

    # GET: no audio file was uploaded => show home page
    return render(
        "data.html",
        title="Routes",
        routes=Climber.query.get(current_user.id).all_routes_as_dict(),
        grades=[grade.as_dict() for grade in Grade.query.all()],
    )


@home.route("/cancel_form")
def cancel_form() -> None:
    """Cancel the addition of a session."""
    flask_session.pop("entities", None)
    flask_session.pop("predictions", None)
    return redirect(flask_session.pop("call_from_url"))
