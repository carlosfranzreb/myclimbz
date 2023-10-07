from flask import Blueprint, render_template, url_for, redirect, send_from_directory

from climbs.forms import FileForm
from climbs.utils import format_file


routes = Blueprint("routes", __name__)
FILE = "src/static/data/boulders.csv"


@routes.route("/", methods=["GET", "POST"])
def home():
    form = FileForm()
    if form.validate_on_submit():
        f = form.file.data
        f.save(FILE)
        return redirect(url_for("analysis"))
    return render_template("home.html", title="Home", form=form)


@routes.route("/analysis")
def analysis():
    format_file(FILE)
    return render_template("analysis.html", title="Analysis")


@routes.route("/data/<file>")
def send_file(file):
    return send_from_directory("static", f"data/{file}")
