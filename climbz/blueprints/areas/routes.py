from flask import (
    Blueprint,
    redirect,
    request,
    session as flask_session,
)
from climbz.models import Area
from climbz.forms import AreaForm
from climbz import db
from climbz.blueprints.utils import render


areas = Blueprint("areas", __name__)


@areas.route("/areas")
def table_areas() -> str:
    return render("areas.html", title="Areas", areas=Area.query.all())


@areas.route
@areas.route("/area/<int:area_id>")
def page_area(area_id: int) -> str:
    area = Area.query.get(area_id)
    return render("area.html", area=area)


@areas.route("/edit_area/<int:area_id>", methods=["GET", "POST"])
def edit_area(area_id: int) -> str:
    area = Area.query.get(area_id)

    # POST: an area form was submitted => edit area or return error
    if request.method == "POST":
        area_form = AreaForm.create_empty()
        if not area_form.validate(area.name):
            flask_session["error"] = area_form.errors
            return render("form.html", title="Edit area", forms=[area_form])

        area.name = area_form.name.data
        area.rock_type_id = int(area_form.rock_type.data)
        db.session.commit()
        return redirect(flask_session.pop("call_from_url"))

    # GET: the user wants to edit an area
    area_form = AreaForm.create_from_obj(area)
    return render("form.html", title="Edit area", forms=[area_form])


@areas.route("/delete_area/<int:area_id>", methods=["GET", "POST"])
def delete_area(area_id: int) -> str:
    area = Area.query.get(area_id)
    db.session.delete(area)
    db.session.commit()
    return redirect(flask_session.pop("call_from_url"))
