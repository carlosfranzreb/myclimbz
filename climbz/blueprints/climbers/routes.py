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
from climbz.models import Climber, Route
from climbz.forms import LoginForm, ClimberForm, ChangePwForm
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
            return render_template(
                "login.html",
                title="Login",
                form=form,
            )
        else:
            flask_session["error"] = None
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
def edit_climber(climber_id: int):
    """Edit profile."""
    form = ClimberForm()
    climber = Climber.query.get(climber_id)

    # POST: a profile form was submitted => edit profile or return error
    if request.method == "POST":
        if not form.validate():
            flask_session["error"] = form.errors
            return render("form.html", title="Edit profile", forms=[form])
        # form is valid; commit changes and return to profile page
        obj = form.get_edited_obj(climber)
        db.session.add(obj)
        db.session.commit()
        return redirect(flask_session.pop("call_from_url"))

    # GET: the user wants to edit their profile
    form = ClimberForm.create_from_obj(climber)
    return render("form.html", title="Edit profile", forms=[form])


@climbers.route("/climber/<int:climber_id>", methods=["GET", "POST"])
def view_climber(climber_id: int):
    """View climber."""
    climber = Climber.query.get(climber_id)
    return render(
        "climber.html",
        title=climber.name,
        climber=climber,
    )


@climbers.route("/edit_password/<int:climber_id>", methods=["GET", "POST"])
def edit_password(climber_id: int):
    """Edit profile."""
    form = ChangePwForm()
    climber = Climber.query.get(climber_id)

    # POST: a profile form was submitted => edit profile or return error
    if request.method == "POST":
        if not form.validate(climber):
            flask_session["error"] = form.errors
            return render("form.html", title="Edit profile", forms=[form])
        # form is valid; commit changes and return to last page
        climber.change_password(form.new_pw.data)
        db.session.commit()
        return redirect(flask_session.pop("call_from_url"))

    # GET: the user wants to edit their profile
    return render("form.html", title="Change password", forms=[form])


@climbers.route("/add_project/<int:route_id>")
def add_project(route_id: int):
    """Add route as project."""
    climber = Climber.query.get(current_user.id)
    route = Route.query.get(route_id)
    climber.projects.append(route)
    db.session.commit()
    return redirect(flask_session.pop("call_from_url"))


@climbers.route("/delete_project/<int:route_id>")
def delete_project(route_id: int):
    """Remove route from projects."""
    climber = Climber.query.get(current_user.id)
    route = Route.query.get(route_id)
    climber.projects.remove(route)
    db.session.commit()
    return redirect(flask_session.pop("call_from_url"))


@climbers.route("/climbers")
def table_climbers() -> str:
    return render("climbers.html", title="Climbers", climbers=Climber.query.all())
