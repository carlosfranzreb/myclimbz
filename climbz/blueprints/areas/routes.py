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
    flask_session["call_from_url"] = "/areas"
    return render("areas.html", title="Areas", areas=Area.query.all())


@areas.route
@areas.route("/area/<int:area_id>")
def page_area(area_id: int) -> str:
    area = Area.query.get(area_id)
    flask_session["call_from_url"] = f"/area/{area_id}"
    return render("area.html", area=area)


@areas.route("/edit_area/<int:area_id>", methods=["GET", "POST"])
def edit_area(area_id: int) -> str:
    area = Area.query.get(area_id)
    area_form = AreaForm()
    area_form.add_choices()

    # POST: an area form was submitted => edit area or return error
    if request.method == "POST":
        if not area_form.validate():
            flask_session["error"] = area_form.errors
            return render("edit_area.html", title="Edit area", area_form=area_form)

        # if the name has changed, check if it already exists
        if area_form.name.data != area.name:
            if Area.query.filter_by(name=area_form.name.data).first() is not None:
                flask_session["error"] = "An area with that name already exists."
                return render("edit_area.html", area_form=area_form)

        area.name = area_form.name.data
        area.rock_type_id = int(area_form.rock_type.data)
        db.session.commit()
        return redirect(flask_session.pop("call_from_url"))

    # GET: the user wants to edit an area
    area_form.name.data = area.name
    area_form.rock_type.data = (
        str(area.rock_type.id) if area.rock_type is not None else 0
    )
    return render(
        "edit_area.html",
        title="Edit area",
        area_form=area_form,
        area_names=[area.name for area in Area.query.order_by(Area.name).all()],
    )


@areas.route("/delete_area/<int:area_id>", methods=["GET", "POST"])
def delete_area(area_id: int) -> str:
    area = Area.query.get(area_id)
    db.session.delete(area)
    db.session.commit()
    return redirect(flask_session.pop("call_from_url"))
