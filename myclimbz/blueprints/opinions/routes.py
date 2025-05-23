from flask import Blueprint, request, redirect, session as flask_session, jsonify, abort
from flask_login import current_user

from myclimbz.models import Opinion, Route
from myclimbz.forms import OpinionForm
from myclimbz import db
from myclimbz.blueprints.utils import render

opinions = Blueprint("opinions", __name__)


@opinions.route("/add_opinion/<int:climber_id>/<int:route_id>", methods=["GET", "POST"])
def add_opinion(climber_id: int, route_id: int) -> str:

    route_name = Route.query.get(route_id).name
    title = f"Add opinion for {route_name}"

    opinion_form = OpinionForm.create_empty(remove_title=True)
    del opinion_form.skip_opinion

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
    if request.method == "POST":
        opinion_form = OpinionForm.create_empty()
        if not opinion_form.validate():
            return render("form.html", title=title, forms=[opinion_form])

        opinion = opinion_form.get_edited_opinion(opinion_id)
        db.session.add(opinion)
        db.session.commit()
        return redirect(flask_session.pop("call_from_url"))

    # GET: return the edit opinion page
    elif request.method == "GET":
        opinion_form = OpinionForm.create_from_obj(opinion, remove_title=True)

    del opinion_form.skip_opinion
    return render("form.html", title=title, forms=[opinion_form])


@opinions.route(
    "/get_opinion_form/<int:climber_id>/<int:route_id>", methods=["GET", "POST"]
)
def get_opinion_form(climber_id: int, route_id: int) -> str:
    """
    Redirect the user to the `edit_opinion` page if the user already has an opinion of
    this route. If there is none, redirect the user to the `add_opinion` page, where a
    new opinion can be submitted.
    """
    opinion = Opinion.query.filter_by(climber_id=climber_id, route_id=route_id).first()
    if opinion is not None:
        return redirect(f"/edit_opinion/{opinion.id}")
    else:
        return redirect(f"/add_opinion/{climber_id}/{route_id}")


@opinions.route("/delete_opinion/<int:opinion_id>", methods=["GET", "POST"])
def delete_opinion(opinion_id: int) -> str:
    """
    Deleting an opinion is only possible if the user is the owner of the opinion, or an
    admin. This is checked in check_request_validity (./myclimbz/__init__.py)
    """
    opinion = Opinion.query.get(opinion_id)
    db.session.delete(opinion)
    db.session.commit()
    return redirect(flask_session.pop("call_from_url"))


@opinions.route("/get_opinion_from_route_name/<route_name>")
def get_opinion_from_route_name(route_name: str) -> str:
    """
    Given a route name by the frontend, return the opinion info required to populate
    the form, if there is an opinion. We assume that the user is the current user.
    """
    route = Route.query.filter_by(name=route_name).first()
    if route is None:
        abort(404)

    opinion = Opinion.query.filter_by(
        route_id=route.id, climber_id=current_user.id
    ).first()
    if opinion is None:
        return jsonify({})

    # return opinion information
    return jsonify(
        {
            "grade": str(opinion.grade.id) if opinion.grade else None,
            "rating": opinion.rating,
            "landing": opinion.landing,
            "cruxes": [crux.name for crux in opinion.cruxes],
            "opinion_comment": opinion.comment,
        }
    )
