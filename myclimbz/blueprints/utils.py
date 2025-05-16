from collections import namedtuple

from flask import (
    render_template,
    session as flask_session,
    request,
    redirect,
    url_for,
    abort,
)
from flask_login import current_user, login_required

from myclimbz.models import Session, Area


@login_required
def render(*args, **kwargs) -> str:
    """
    Our own wrapper for the render_template function from Flask, adding arguments that are
    always required.

    - A title is required.
    - If an error is defined in the session, it is popped and added to the kwargs.
    - If there is no error but flask_session["all_forms_valid"] is false, a default
        error message is added.
    - If an open session is defined in the session, it is added to the kwargs.
    - Add the current user's name and ID to the kwargs.
    - Save the URL in the session, unless it starts with "edit_".
    """

    # ensure title exists and add video info if neededs
    if "title" not in kwargs:
        abort(500)

    # Add a standard error if there aren't any but forms are not valid
    if not flask_session.pop("all_forms_valid", True):
        if "error" in flask_session and flask_session["error"] is not None:
            kwargs["error"] = flask_session.pop("error")
        else:
            flask_session["error"] = "An error occurred. Fix it and resubmit."

    # check if videos should be uploaded by the client to the server
    if "upload_videos_for_url" in flask_session:
        kwargs["upload_videos_for_url"] = flask_session.pop("upload_videos_for_url")

    # add other kwargs
    kwargs["error"] = flask_session.pop("error", None)
    kwargs["username"] = current_user.name
    kwargs["user_id"] = current_user.id
    kwargs["user_role"] = current_user.role
    kwargs["user_grade_scale"] = current_user.grade_scale

    # discern form pages from the rest
    path = request.path
    if (
        path.startswith("/edit_")
        or path.startswith("/add_")
        or path.startswith("/sort_")
        or path.startswith("/annotate_")
    ):
        kwargs["is_form"] = True
    else:
        kwargs["is_form"] = False
        flask_session["call_from_url"] = path

    session_id = flask_session.get("session_id", None)
    if session_id is not None:
        if session_id == "project_search":
            area = Area.query.get(flask_session["area_id"])
            session_obj = namedtuple("Session", ["is_project_search", "area"])(
                True, namedtuple("Area", ["name"])(area.name)
            )
            kwargs["open_session"] = session_obj
        else:
            kwargs["open_session"] = Session.query.get(session_id)

    return render_template(
        *args,
        **kwargs,
    )


def delete_video_info():
    """
    Delete video info from flask_session. The files are not deleted.
    """
    for session_key in ["video_id", "video_upload_status", "video_fnames"]:
        if session_key in flask_session:
            del flask_session[session_key]
