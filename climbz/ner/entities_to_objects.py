"""Functions to get objects from entities."""

from climbz.models import Area, Route, Sector, RockType


def get_area_from_entities(entities: dict) -> Area:
    area = Area.query.filter_by(name=entities["area"]).first()
    if area is None:
        if "rock" in entities:
            rock_type = RockType.query.filter_by(name=entities["rock"]).first()
            area = Area(name=entities["area"], rock_type=rock_type)
        else:
            area = Area(name=entities["area"])
    return area


def get_route_from_entities(entities: dict, area_id: int) -> Route:
    if "name" in entities:
        route = Route.query.filter_by(name=entities["name"]).first()
    else:
        entities["name"] = ""
        route = None
    if route is None:
        sector = None
        if "sector" in entities:
            sector = Sector.query.filter_by(name=entities["sector"]).first()
            if sector is None:
                sector = Sector(name=entities["sector"], area_id=area_id)
        route = Route(name=entities["name"], sector=sector)
    return route
