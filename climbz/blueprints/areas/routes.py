from flask import Blueprint, render_template, redirect, url_for, request
from climbz.models import Area
from climbz.forms import AreaForm
from climbz import db


areas = Blueprint("areas", __name__)


@areas.route("/areas")
def table_areas() -> str:
    return render_template("areas.html", title="Areas", areas=Area.query.all())


@areas.route
@areas.route("/area/<int:area_id>")
def page_area(area_id: int) -> str:
    area = Area.query.get(area_id)
    return render_template("area.html", area=area)


@areas.route("/edit_area/<int:area_id>", methods=["GET", "POST"])
def edit_area(area_id: int) -> str:
    area = Area.query.get(area_id)
    area_form = AreaForm()
    area_form.add_choices()

    # POST: an area form was submitted => edit area or return error
    if request.method == "POST":
        if not area_form.validate():
            return render_template(
                "edit_area.html",
                area_form=area_form,
                error=area_form.errors,
            )

        # if the name has changed, check if it already exists
        if area_form.name.data != area.name:
            if Area.query.filter_by(name=area_form.name.data).first() is not None:
                return render_template(
                    "edit_area.html",
                    area_form=area_form,
                    error="An area with that name already exists.",
                )

        area.name = area_form.name.data
        area.rock_type_id = int(area_form.rock_type.data)
        db.session.commit()
        return redirect(url_for("areas.page_area", area_id=area_id))

    # GET: the user wants to edit an area
    area_form.name.data = area.name
    area_form.rock_type.data = (
        str(area.rock_type.id) if area.rock_type is not None else 0
    )
    return render_template(
        "edit_area.html",
        area_form=area_form,
        area_names=[area.name for area in Area.query.order_by(Area.name).all()],
    )


@areas.route("/edit_area/<int:area_id>", methods=["GET", "POST"])
def delete_area(area_id: int) -> str:
    return redirect(url_for("areas.page_area", area_id=area_id))
