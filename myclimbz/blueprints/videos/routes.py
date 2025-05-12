import os
from time import time

from flask import (
    Blueprint,
    redirect,
    request,
    session as flask_session,
    current_app,
    send_from_directory,
    abort,
    url_for,
    jsonify,
    make_response,
)
from flask_login import current_user
from werkzeug.utils import secure_filename

from myclimbz.models import Video, VideoAttempt, Session
from myclimbz.forms import (
    VideosUploadForm,
    VideoAttemptForm,
    VideoAnnotationForm,
    RouteForm,
    ClimbForm,
    OpinionForm,
)
from myclimbz import db
from myclimbz.blueprints.utils import render, delete_video_info
from myclimbz.blueprints.videos.utils import (
    check_access_to_file,
    get_video_frames,
    trim_video,
)

videos = Blueprint("videos", __name__)


@videos.route(
    "/annotate_video",
    methods=["GET", "POST"],
)
def annotate_video() -> str:
    """
    The user is shown a video and is asked to mark the portions of each video where
    there is climbing. Only the marked will be saved. The number of attempts is inferred
    from the marked portions.

    Afterwards, the user is sent to `add_climb` to fill in route information. And after
    that, if there are more videos, the user is sent back here to annotate the next video.

    TODO: section values cannot exceed video duration
    TODO: add "sent" field to each section
    """

    # create video annotation form
    title = "Annotate"
    video_form = VideoAnnotationForm()

    # create other forms
    session_id = flask_session["session_id"]
    area_id = Session.query.get(session_id).area_id
    route_form = RouteForm.create_empty(area_id)
    climb_form = ClimbForm.create_empty()
    del climb_form.is_project
    opinion_form = OpinionForm.create_empty()

    # POST: user submitted forms
    if request.method == "POST":

        # validate forms
        flask_session["error"] = None
        flask_session["all_forms_valid"] = True
        for form in [video_form, route_form, opinion_form]:
            flask_session["all_forms_valid"] &= form.validate()

        if not climb_form.validate_from_name(
            route_form.name.data, route_form.sector.data
        ):
            flask_session["all_forms_valid"] &= climb_form.validate()

        # store info if forms are valid
        if flask_session["all_forms_valid"]:

            # store video annotations
            video = Video(base_fname=f"{current_user.id}_{session_id}_{int(time())}")
            for section_idx, section in enumerate(video_form.sections.data):
                video.attempts.append(
                    VideoAttempt(
                        start=section["start"],
                        end=section["end"],
                        attempt_number=section_idx,
                        sent=False,
                    )
                )
            db.session.add(video)

            # store route, climb and opinion (TODO: use code from climbs.add_climb?)
            sector = route_form.get_sector(area_id)
            route = route_form.get_object(sector)
            for obj in [sector, route]:
                if obj.id is None:
                    db.session.add(obj)
            opinion = opinion_form.get_object(current_user.id, route.id)
            if opinion.id is None:
                db.session.add(opinion)
            db.session.flush()

            # add video to climb
            climb = climb_form.get_object(route)
            climb.videos.append(video)
            db.session.add(climb)
            db.session.commit()

            # go to video upload page
            return redirect(url_for("videos.upload_videos", video_id=video.id))

    return render(
        "form_videos.html",
        title=title,
        video_form=video_form,
        other_forms=[route_form, climb_form, opinion_form],
    )


@videos.route("/upload_videos/<int:video_id>", methods=["GET", "POST"])
def upload_videos(video_id: int) -> str:
    """
    Endpoint for uploading video files
    """
    title = "Upload videos"
    video = Video.query.get(video_id)
    form = VideosUploadForm()

    # populate the start and end fields of the video attempts
    sorted_video_attempts = sorted(
        video.attempts, key=lambda attempt: attempt.attempt_number
    )
    for attempt_number, video_attempt in enumerate(sorted_video_attempts):
        if len(form.videos.data) <= attempt_number:
            form.videos.append_entry()

        form.videos[-1].start.data = video_attempt.start
        form.videos[-1].end.data = video_attempt.end

    if request.method == "POST":
        if not form.validate():
            flask_session["all_forms_valid"] = False
        elif len(form.videos) != len(video.attempts):
            flask_session["all_forms_valid"] = False
            flask_session["error"] = "The number of attempts is incorrect"

        else:
            for attempt_number, form_attempt in enumerate(form.videos):

                # check that the start and end were not changed
                for field in ["start", "end"]:
                    if getattr(form_attempt, field).data != getattr(
                        sorted_video_attempts[attempt_number], field
                    ):
                        abort(500)

                # save the file
                file = form_attempt.file
                f_ext = os.path.splitext(file.filename)[1]
                attempt_number = form_attempt.attempt_number.data
                file.save(
                    os.path.join(
                        current_app.config["VIDEOS_FOLDER"],
                        f"{video.base_fname}_{attempt_number}{f_ext}",
                    )
                )

            return redirect(flask_session["call_from_url"])

    return render("form.html", title=title, forms=[form], enctype="multipart/form-data")


@videos.route("/files/<filetype>/<filename>")
def serve_file(filetype: str, filename: str):
    """
    Serves files from the UPLOAD_FOLDER.
    """

    if filetype == "videos":
        folder = current_app.config["VIDEOS_FOLDER"]
    elif filetype == "frames":
        folder = current_app.config["FRAMES_FOLDER"]
    else:
        abort(404)

    try:
        return send_from_directory(folder, filename)
    except FileNotFoundError:
        abort(404)
