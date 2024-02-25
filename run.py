from flask import request, redirect, url_for, session as flask_session
from flask_login import current_user

from climbz import create_app
from climbz.models import Climber, Route, Area, Session, Climb  # noqa


app = create_app("test_100")


@app.before_request
def check_request_validity():
    """
    - Ensure that the user is logged in before accessing any non-static page
    - If the page entails modifying an object, check that the user is allowed to do so
    """
    if not request.endpoint:
        return
    elif request.endpoint == "climbers.login" or "static" in request.endpoint:
        return
    elif not current_user.is_authenticated:
        return redirect(url_for("climbers.login"))

    # check if the user is allowed to access the page
    if "edit" in request.endpoint or "delete" in request.endpoint:
        path, obj_id = request.path[1:].split("/")
        obj_str = path.split("_")[1]
        obj = eval(obj_str.capitalize()).query.get(int(obj_id))
        if obj.created_by != current_user.id and current_user.role != 1:
            flask_session["error"] = "You are not allowed to access this page."
            return redirect(flask_session.pop("call_from_url"))


if __name__ == "__main__":
    app.run(debug=True)
