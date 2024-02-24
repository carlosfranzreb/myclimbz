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

from climbz.ner import transcribe, parse_climb, ClimbsModel
from climbz.models import Route, Grade
from climbz.blueprints.utils import render


ASR_MODEL = whisper.load_model("medium")
NER_MODEL = ClimbsModel.load_from_checkpoint(
    "climbz/ner/checkpoints/ner-0.ckpt", map_location="cpu"
)

home = Blueprint("home", __name__)


@home.route("/", methods=["GET", "POST"])
def page_home() -> str:
    current_session_id = flask_session.get("session_id", -1)
    routes_dict = [route.as_dict(current_user.id) for route in Route.query.all()]
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

        if current_session_id > 0:
            return redirect("/add_climb")
        else:
            return redirect("/add_session")

    # GET: no audio file was uploaded => show home page
    return render(
        "data.html",
        title="Routes",
        routes=routes_dict,
        grades=grades_dict,
    )


@home.route("/cancel_form")
def cancel_form() -> None:
    """Cancel the addition of a session."""
    flask_session.pop("entities", None)
    flask_session.pop("predictions", None)
    return redirect(flask_session.pop("call_from_url"))
