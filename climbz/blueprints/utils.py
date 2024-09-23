"""
Our own wrapper for the render_template function from Flask, adding arguments that are
always required.
"""

from flask import render_template, session as flask_session, request
from flask_login import current_user, login_required

from climbz.models import Session


@login_required
def render(*args, **kwargs) -> str:
    """
    - A title is required.
    - If an error is defined in the session, it is popped and added to the kwargs.
    - If an open session is defined in the session, it is added to the kwargs.
    - Add the current user's name and ID to the kwargs.
    - Save the URL in the session, unless it starts with "edit_".
    """
    kwargs["title"] = kwargs["title"]
    kwargs["error"] = flask_session.pop("error", None)
    kwargs["open_session"] = Session.query.get(flask_session.get("session_id", -1))
    kwargs["username"] = current_user.name
    kwargs["user_id"] = current_user.id
    kwargs["user_role"] = current_user.role
    kwargs["user_grade_scale"] = current_user.grade_scale
    path = request.path
    if not path.startswith("/edit_") and not path.startswith("/add_"):
        flask_session["call_from_url"] = path
    return render_template(
        *args,
        **kwargs,
    )
