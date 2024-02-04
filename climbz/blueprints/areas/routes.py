from flask import Blueprint, render_template
from climbz.models import Area, Sector


areas = Blueprint("areas", __name__)


@areas.route("/areas")
def table_areas() -> str:
    return render_template("areas.html", title="Areas", areas=Area.query.all())


@areas.route
@areas.route("/area/<int:area_id>")
def page_area(area_id: int) -> str:
    area = Area.query.get(area_id)
    return render_template("area.html", area=area)


@areas.route("/sector/<int:sector_id>")
def page_sector(sector_id: int) -> str:
    sector = Sector.query.get(sector_id)
    return render_template("sector.html", sector=sector, routes=sector.routes)
