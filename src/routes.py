from flask import render_template, url_for, redirect, send_from_directory

from src import app
from src.forms import FileForm
from src.utils import format_file


FILE = "src/static/data/boulders.csv"


@app.route("/", methods=["GET", "POST"])
def home():
    form = FileForm()
    if form.validate_on_submit():
        f = form.file.data
        f.save(FILE)
        return redirect(url_for("analysis"))
    return render_template("home.html", title="Home", form=form)


@app.route("/analysis")
def analysis():
    format_file(FILE)
    return render_template("analysis.html", title="Analysis")


@app.route("/data/<file>")
def send_file(file):
    return send_from_directory("static", f"data/{file}")
