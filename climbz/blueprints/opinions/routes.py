from flask import Blueprint, request, redirect, session as flask_session

from climbz.models import Opinion, Route
from climbz.forms import OpinionForm
from climbz import db
from climbz.blueprints.utils import render

opinions = Blueprint("opinions", __name__)


@opinions.route("/add_opinion/<int:climber_id>/<int:route_id>", methods=["GET", "POST"])
def add_opinion(climber_id: int, route_id: int) -> str:
    route_name = Route.query.get(route_id).name
    opinion_form = OpinionForm.create_empty()
    title = f"Add opinion for {route_name}"

    # POST: an opinion form was submitted => create opinion or return error
    if request.method == "POST":
        if not opinion_form.validate():
            return render("form.html", title=title, forms=[opinion_form])

        opinion = opinion_form.get_object(climber_id, route_id)
        db.session.add(opinion)
        db.session.commit()
        return redirect(flask_session.pop("call_from_url"))

    # GET: return the add opinion page
    return render("form.html", title=title, forms=[opinion_form])


@opinions.route("/edit_opinion/<int:opinion_id>", methods=["GET", "POST"])
def edit_opinion(opinion_id: int) -> str:
    opinion = Opinion.query.get(opinion_id)
    title = f"Edit opinion for {opinion.route.name}"

    # POST: an opinion form was submitted => edit opinion or return error
    opinion_form = OpinionForm.create_empty()
    if request.method == "POST":
        if not opinion_form.validate():
            return render("form.html", title=title, forms=[opinion_form])

        opinion = opinion_form.get_edited_opinion(opinion_id)
        db.session.add(opinion)
        db.session.commit()
        return redirect(flask_session.pop("call_from_url"))

    # GET: return the edit opinion page
    opinion_form = OpinionForm.create_from_obj(opinion)
    return render("form.html", title=title, forms=[opinion_form])


@opinions.route("/delete_opinion/<int:opinion_id>", methods=["GET", "POST"])
def delete_opinion(opinion_id: int) -> str:
    opinion = Opinion.query.get(opinion_id)
    db.session.delete(opinion)
    db.session.commit()
    return redirect(flask_session.pop("call_from_url"))
