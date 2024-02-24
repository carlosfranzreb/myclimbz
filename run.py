from flask import request, redirect, url_for, session as flask_session
from flask_login import current_user

from climbz import create_app


app = create_app("test_100")


@app.before_request
def check_valid_login():
    """
    Ensure that the user is logged in before accessing any page that is not static.
    """
    if request.endpoint == "climbers.login":
        return

    login_valid = current_user.is_authenticated
    if request.endpoint and "static" not in request.endpoint and not login_valid:
        flask_session["call_from_url"] = request.endpoint
        return redirect(url_for("climbers.login"))


if __name__ == "__main__":
    app.run(debug=True)
