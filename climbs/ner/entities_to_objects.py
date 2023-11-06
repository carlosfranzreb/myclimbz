"""Functions to get objects from entities."""


from climbs.models import Area, Route, Sector, Crux, RockType


def get_area_from_entities(entities: dict) -> Area:
    area = Area.query.filter_by(name=entities["AREA"]).first()
    if area is None:
        if "ROCK" in entities:
            rock_type = RockType.query.filter_by(name=entities["ROCK"]).first()
            area = Area(name=entities["AREA"], rock_type=rock_type)
        else:
            area = Area(name=entities["AREA"])
    return area


def get_route_from_entities(entities: dict, area_id: int) -> Route:
    route = Route.query.filter_by(name=entities["NAME"]).first()
    if route is None:
        sector = None
        if "SECTOR" in entities:
            sector = Sector.query.filter_by(name=entities["SECTOR"]).first()
            if sector is None:
                sector = Sector(name=entities["SECTOR"], area_id=area_id)
        cruxes = list()
        if "CRUX" in entities:
            for crux_name in entities["CRUX"]:
                cruxes.append(Crux.query.filter_by(name=crux_name).first())
        route = Route(name=entities["NAME"], sector=sector)
    return route
