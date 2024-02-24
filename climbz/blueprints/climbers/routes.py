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

from climbz.models import Climber
from climbz.forms import LoginForm, ProfileForm
from climbz.blueprints.utils import render


climbers = Blueprint("climbers", __name__)


@climbers.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.get_home"))

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


@climbers.route("/edit_profile", methods=["GET", "POST"])
def edit_profile():
    """Edit profile."""
    form = ProfileForm()

    # POST: a profile form was submitted => edit profile or return error
    if request.method == "POST":
        if not form.validate():
            flask_session["error"] = form.errors
            return render("edit_profile.html", title="Edit profile", form=form)
        # form is valid; commit changes and return to profile page
        # TODO

    # GET: the user wants to edit their profile
    return render_template(
        "edit_profile.html",
        title="Edit profile",
        form=form,
    )


@climbers.route("/view_profile", methods=["GET", "POST"])
def view_profile():
    """View profile."""
    climber = Climber.query.get(current_user.id)
    return render(
        "view_profile.html",
        title="View profile",
        climber=climber,
    )
