from flask import Blueprint, request, redirect, session as flask_session

from myclimbz.models import Opinion, Route
from myclimbz.forms import OpinionForm
from myclimbz import db
from myclimbz.blueprints.utils import render

opinions = Blueprint("opinions", __name__)


@opinions.route(
    "/add_opinion_from_video/<int:climber_id>/<int:route_id>/video<int:video_idx>from<int:n_videos>",
    methods=["GET", "POST"],
)
@opinions.route("/add_opinion/<int:climber_id>/<int:route_id>", methods=["GET", "POST"])
def add_opinion(
    climber_id: int, route_id: int, video_idx: int = None, n_videos: int = None
) -> str:
    route_name = Route.query.get(route_id).name
    opinion_form = OpinionForm.create_empty()

    title = f"Add opinion for {route_name}"
    if video_idx:
        title += f" from video ({video_idx+1}/{n_videos})"

    # POST: an opinion form was submitted => create opinion or return error
    if request.method == "POST":
        if not opinion_form.validate():
            return render("form.html", title=title, forms=[opinion_form])

        opinion = opinion_form.get_object(climber_id, route_id)
        db.session.add(opinion)
        db.session.commit()

        # if annotating videos, continue annotating. Otherwise done with forms.
        if video_idx and video_idx + 1 < n_videos:
            return redirect(f"/annotate_video/{n_videos}/{video_idx}")
        else:
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


@opinions.route(
    "/get_opinion_form/<int:climber_id>/<int:route_id>", methods=["GET", "POST"]
)
def get_opinion_form(climber_id: int, route_id: int) -> str:
    """
    TODO: handle videos and re-route to next video when done, if videos are being
    uploaded.
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
