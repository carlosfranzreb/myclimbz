from flask import Blueprint, render_template, request
from climbs.models import Area, Sector


areas = Blueprint("areas", __name__)


@areas.route("/areas")
def table_areas() -> str:
    page = request.args.get("page", 1, type=int)
    page_areas = Area.query.paginate(page=page, per_page=10)
    return render_template("areas.html", areas=page_areas)


@areas.route("/area/<int:area_id>")
def page_area(area_id: int) -> str:
    area = Area.query.get(area_id)
    return render_template("area.html", area=area)


@areas.route("/sector/<int:sector_id>")
def page_sector(sector_id: int) -> str:
    sector = Sector.query.get(sector_id)
    return render_template("sector.html", sector=sector, routes=sector.routes)
