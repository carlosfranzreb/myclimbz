import os
from time import time

from flask import Blueprint, render_template, request


home = Blueprint("home", __name__)


@home.route("/")
def page_home() -> str:
    return render_template("index.html", title="Home")


@home.route("/upload", methods=["POST"])
def upload_audio():
    audio_file = request.files["audioFile"]
    os.makedirs("audios", exist_ok=True)

    if audio_file:
        # Create a unique filename using Unix timestamp
        timestamp = str(int(time()))
        filename = os.path.join("audios", f"{timestamp}.webm")
        audio_file.save(filename)

        return f"Audio saved as: {filename}"
    else:
        return "No audio file uploaded"
