from flask import Blueprint, render_template


home = Blueprint("home", __name__)


@home.route("/")
def page_home() -> str:
    return render_template("index.html")
