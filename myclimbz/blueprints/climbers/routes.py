""" Pages related to the administration of users. """

import os
import secrets
import string

import requests
from flask import (
    render_template,
    url_for,
    redirect,
    Blueprint,
    request,
    session as flask_session,
    abort,
)
from flask_login import login_user, current_user, logout_user
from flask_bcrypt import generate_password_hash
from flask_mail import Message

from myclimbz import db, mail
from myclimbz.models import Climber, Route
from myclimbz.forms import LoginForm, ClimberForm, ChangePwForm, NewPwForm, ForgotPwForm
from myclimbz.blueprints.utils import render


GOOGLE_RECAPTCHA_VERIFY_URL = "https://www.google.com/recaptcha/api/siteverify"
RECAPTCHA_PUBLIC_KEY = os.environ["RECAPTCHA_PUBLIC_KEY"]
RECAPTCHA_PRIVATE_KEY = os.environ["RECAPTCHA_PRIVATE_KEY"]

climbers = Blueprint("climbers", __name__)


@climbers.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home.page_home"))
    form = LoginForm()

    # POST: a login form was submitted => log in or return error
    if request.method == "POST":
        if not form.validate():
            flask_session["error"] = "An error occurred. Fix it and resubmit."
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
        if not form.validate(climber_id):
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


@climbers.route("/register", methods=["GET", "POST"])
def register():
    """Create new user."""
    form = ClimberForm()
    pw_form = NewPwForm()

    # POST: a profile form was submitted => edit profile or return error
    if request.method == "POST":

        # validate the recaptcha
        secret_response = request.form["g-recaptcha-response"]
        verify_response = requests.post(
            url=f"{GOOGLE_RECAPTCHA_VERIFY_URL}?secret={RECAPTCHA_PRIVATE_KEY}&response={secret_response}"
        ).json()
        if not verify_response["success"] or verify_response["score"] < 0.5:
            abort(403)

        if not form.validate() or not pw_form.validate():
            return render_template(
                "register.html",
                title="Register",
                form=form,
                pw_form=pw_form,
                recaptcha=RECAPTCHA_PUBLIC_KEY,
            )

        # form is valid; commit changes and return
        climber = form.get_edited_obj(Climber())
        climber.password = generate_password_hash(pw_form.new_pw.data)
        db.session.add(climber)
        db.session.commit()

        login_user(climber)
        return redirect(url_for("home.page_home"))

    # GET: the guest wants to register as a user
    return render_template(
        "register.html",
        title="Register",
        form=form,
        pw_form=pw_form,
        recaptcha=RECAPTCHA_PUBLIC_KEY,
    )


@climbers.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    """Form to get a new password by e-mail."""
    form = ForgotPwForm()
    title = "Forgot password"

    # POST: a profile form was submitted => edit profile or return error
    if request.method == "POST":

        # validate the recaptcha
        secret_response = request.form["g-recaptcha-response"]
        verify_response = requests.post(
            url=f"{GOOGLE_RECAPTCHA_VERIFY_URL}?secret={RECAPTCHA_PRIVATE_KEY}&response={secret_response}"
        ).json()
        if not verify_response["success"] or verify_response["score"] < 0.5:
            abort(403)

        if not form.validate():
            return render_template(
                "forgot_pw.html", title=title, form=form, recaptcha=RECAPTCHA_PUBLIC_KEY
            )

        # # check if the e-mail is in the database
        climber = Climber.query.filter_by(email=form.email.data).first()
        if climber is None:
            form.email.errors.append("E-mail not found.")
            return render_template(
                "forgot_pw.html", title=title, form=form, recaptcha=RECAPTCHA_PUBLIC_KEY
            )

        # form is valid; change password and send e-mail
        alphabet = string.ascii_letters + string.digits
        new_pw = "".join(secrets.choice(alphabet) for _ in range(20))
        climber.change_password(new_pw)
        db.session.commit()

        msg = Message(
            subject="myclimbz - new password",
            sender="myclimbz@outlook.de",
            recipients=[climber.email],
        )
        msg.body = f"""
        You requested a new password for your myclimbz account.

        Your new password is: {new_pw}.

        You can login with this password and change it in your profile.
        Here is the link to the login page: https://myclimbz.com/login
        """
        mail.send(msg)

        return redirect(url_for("climbers.login"))

    # GET: the user wants to edit their profile
    return render_template(
        "forgot_pw.html", title=title, form=form, recaptcha=RECAPTCHA_PUBLIC_KEY
    )


@climbers.route("/climber/<int:climber_id>", methods=["GET", "POST"])
def view_climber(climber_id: int):
    """View climber."""
    climber = Climber.query.get(climber_id)
    return render("climber.html", title=climber.name, climber=climber)


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
