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
)
from flask_login import current_user

from myclimbz.models import Video, VideoAttempt, Session
from myclimbz.forms import (
    VideoAnnotationForm,
    RouteForm,
    ClimbForm,
    OpinionForm,
)
from myclimbz import db
from myclimbz.blueprints.utils import render

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
    title = "Annotate video"
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

                # store section in database
                video.attempts.append(
                    VideoAttempt(
                        start=section["start"],
                        end=section["end"],
                        attempt_number=section_idx,
                        sent=False,
                    )
                )

                # store video file
                file = section["file"]
                f_ext = os.path.splitext(file.filename)[1]
                file.save(
                    os.path.join(
                        current_app.config["VIDEOS_FOLDER"],
                        f"{video.base_fname}_{section_idx}{f_ext}",
                    )
                )

            db.session.add(video)

            # store route, climb and opinion (TODO: use code from climbs.add_climb?)
            sector = route_form.get_sector(area_id)
            db.session.add(sector)
            db.session.flush()

            route = route_form.get_object(sector)
            db.session.add(route)
            db.session.flush()

            opinion = opinion_form.get_object(current_user.id, route.id)
            db.session.add(opinion)
            db.session.flush()

            # add video to climb
            climb = climb_form.get_object(route)
            climb.videos.append(video)
            db.session.add(climb)
            db.session.commit()

            # go to video upload page
            return redirect(flask_session["call_from_url"])

    return render(
        "form_videos.html",
        title=title,
        video_form=video_form,
        other_forms=[route_form, climb_form, opinion_form],
    )


@videos.route("/videos/<filename>")
def serve_video(filename: str):
    """Serves video from the VIDEOS_FOLDER."""
    try:
        return send_from_directory(current_app.config["VIDEOS_FOLDER"], filename)
    except FileNotFoundError:
        abort(404)
