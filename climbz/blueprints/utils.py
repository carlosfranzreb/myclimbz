from collections import namedtuple

from flask import render_template, session as flask_session, request
from flask_login import current_user, login_required

from climbz.models import Session, Area


@login_required
def render(*args, **kwargs) -> str:
    """
    Our own wrapper for the render_template function from Flask, adding arguments that are
    always required.

    - A title is required.
    - If an error is defined in the session, it is popped and added to the kwargs.
    - If an open session is defined in the session, it is added to the kwargs.
    - Add the current user's name and ID to the kwargs.
    - Save the URL in the session, unless it starts with "edit_".
    """
    kwargs["title"] = kwargs["title"]
    kwargs["error"] = flask_session.pop("error", None)
    kwargs["username"] = current_user.name
    kwargs["user_id"] = current_user.id
    kwargs["user_role"] = current_user.role
    kwargs["user_grade_scale"] = current_user.grade_scale

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

    path = request.path
    if not path.startswith("/edit_") and not path.startswith("/add_"):
        flask_session["call_from_url"] = path
    return render_template(
        *args,
        **kwargs,
    )
