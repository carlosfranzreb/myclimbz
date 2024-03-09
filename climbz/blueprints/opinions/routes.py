from flask import (
    Blueprint,
    request,
    url_for,
    redirect,
    session as flask_session,
)

from climbz.models import Opinion
from climbz.forms import OpinionForm
from climbz import db
from climbz.blueprints.utils import render

opinions = Blueprint("opinions", __name__)


@opinions.route("/edit_opinion/<int:opinion_id>", methods=["GET", "POST"])
def edit_opinion(opinion_id: int) -> str:
    opinion = Opinion.query.get(opinion_id)
    # POST: a opinion form was submitted => edit opinion or return error
    opinion_form = OpinionForm.create_empty()
    if request.method == "POST":
        if not opinion_form.validate():
            return render("edit_form.html", title="Edit opinion", form=opinion_form)

        opinion = opinion_form.get_edited_opinion(opinion_id)
        db.session.add(opinion)
        db.session.commit()
        return redirect(flask_session.pop("call_from_url"))

    # GET: return the edit route page
    opinion_form = OpinionForm.create_from_obj(opinion)
    return render("edit_form.html", title="Edit opinion", form=opinion_form)


@opinions.route("/delete_opinion/<int:opinion_id>", methods=["GET", "POST"])
def delete_opinion(opinion_id: int) -> str:
    opinion = Opinion.query.get(opinion_id)
    db.session.delete(opinion)
    db.session.commit()
    return redirect(flask_session.pop("call_from_url"))
