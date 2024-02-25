from flask import request, redirect, url_for
from flask_login import current_user

from climbz import create_app


app = create_app("test_100")


@app.before_request
def check_valid_login():
    """Ensure that the user is logged in before accessing any non-static page"""
    if not request.endpoint:
        return

    if request.endpoint == "climbers.login" or "static" in request.endpoint:
        return

    elif not current_user.is_authenticated:
        return redirect(url_for("climbers.login"))


if __name__ == "__main__":
    app.run(debug=True)
