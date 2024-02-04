from flask import Blueprint, render_template, request, session as flask_session
from climbz.models import Area, Sector


areas = Blueprint("areas", __name__)


@areas.route("/areas")
def table_areas() -> str:
    page = request.args.get("page", 1, type=int)
    sort_column = request.args.get("sort_column", None, type=str)

    if sort_column is not None:
        attribute = getattr(Area, sort_column)
        if flask_session.pop("last_sort_column", None) == sort_column:
            attribute = attribute.desc()
        else:
            flask_session["last_sort_column"] = sort_column
        page_areas = Area.query.order_by(attribute).paginate(page=1, per_page=20)
    else:
        page_areas = Area.query.paginate(page=page, per_page=20)
    return render_template("areas.html", title="Areas", areas=page_areas)


@areas.route
@areas.route("/area/<int:area_id>")
def page_area(area_id: int) -> str:
    area = Area.query.get(area_id)
    return render_template("area.html", area=area)


@areas.route("/sector/<int:sector_id>")
def page_sector(sector_id: int) -> str:
    sector = Sector.query.get(sector_id)
    return render_template("sector.html", sector=sector, routes=sector.routes)
