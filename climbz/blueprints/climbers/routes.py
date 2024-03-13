""" Pages related to the administration of users. """

from flask import (
    render_template,
    url_for,
    redirect,
    Blueprint,
    request,
    session as flask_session,
)
from flask_login import login_user, current_user, logout_user

from climbz import db
from climbz.models import Climber
from climbz.forms import LoginForm, ClimberForm
from climbz.blueprints.utils import render


climbers = Blueprint("climbers", __name__)


@climbers.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home.page_home"))
    form = LoginForm()

    # POST: a login form was submitted => log in or return error
    if request.method == "POST":
        if not form.validate():
            flask_session["error"] = form.errors
            return render(
                "login.html",
                title="Login",
                form=form,
            )
        else:
            climber = Climber.query.filter_by(email=form.email.data).first()
            login_user(climber, remember=form.remember.data)
            if "call_from_url" in flask_session:
                return redirect(flask_session.pop("call_from_url"))
            else:
                return redirect(url_for("home.page_home"))

    # GET: render the login page
    return render_template(
        "login.html",
        title="Login",
        form=form,
    )


@climbers.route("/logout")
def logout():
    """Logout and return to previous page. If the page requires a login,
    a 404 error will be thrown."""
    logout_user()
    return redirect(flask_session.pop("call_from_url"))


@climbers.route("/edit_climber/<int:climber_id>", methods=["GET", "POST"])
def edit_profile(climber_id: int):
    """Edit profile."""
    form = ClimberForm()
    climber = Climber.query.get(climber_id)

    # POST: a profile form was submitted => edit profile or return error
    if request.method == "POST":
        if not form.validate():
            flask_session["error"] = form.errors
            return render("edit_form.html", title="Edit profile", form=form)
        # form is valid; commit changes and return to profile page
        obj = form.get_edited_obj(climber)
        db.session.add(obj)
        db.session.commit()
        return redirect(flask_session.pop("call_from_url"))

    # GET: the user wants to edit their profile
    return render_template(
        "edit_form.html",
        title="Edit profile",
        form=ClimberForm.create_from_obj(climber),
    )


@climbers.route("/view_climber/<int:climber_id>", methods=["GET", "POST"])
def view_climber(climber_id: int):
    """View climber."""
    climber = Climber.query.get(climber_id)
    return render(
        "climber.html",
        title=climber.name,
        climber=climber,
    )
