from __future__ import annotations

from flask import session as flask_session
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    FloatField,
    BooleanField,
    URLField,
    DecimalRangeField,
    IntegerRangeField,
)
from wtforms.validators import Optional, DataRequired, NumberRange
from wtforms.widgets import TextArea

from climbz.models import Route, Sector, Session


FIELDS = [
    "name",
    "height",
    "inclination",
    "sit_start",
    "latitude",
    "longitude",
    "comment",
    "link",
]


class RouteForm(FlaskForm):
    name = StringField(
        "Route name", validators=[DataRequired("Please enter the name of the route.")]
    )
    sector = StringField("Sector", validators=[Optional()])
    height = DecimalRangeField(
        "Height",
        validators=[
            NumberRange(
                min=0.5,
                max=10,
                message="Please enter a height between 0.5 and 10 meters.",
            )
        ],
        render_kw={"step": "0.5"},
        default=3.0,
    )
    inclination = IntegerRangeField(
        "Inclination",
        validators=[
            NumberRange(
                min=-50,
                max=90,
                message="Please enter an inclination between -50 and 90 degrees.",
            )
        ],
        default=0,
        render_kw={"step": "5"},
    )
    sit_start = BooleanField("Sit Start", default=False)
    latitude = FloatField("Latitude", validators=[Optional()])
    longitude = FloatField("Longitude", validators=[Optional()])
    comment = StringField("Comment", validators=[Optional()], widget=TextArea())
    link = URLField("Link", validators=[Optional()])
    add_opinion = BooleanField(
        "Add opinion after submitting this form", validators=[Optional()]
    )

    @classmethod
    def create_empty(cls, area_id: int) -> RouteForm:
        """
        Create the form and add choices to the select fields.

        - All sectors are added to the sector field's datalist.
        - All routes that have not been tried in this session are added to the name
            field's datalist.
        """
        form = cls()
        form.height.unit = "m"
        form.inclination.unit = "°"
        form.name.toggle_ids = (
            "sector,height,inclination,sit_start,latitude,longitude,comment,link"
        )

        session_id = flask_session["session_id"]
        if session_id != "project_search":
            session = Session.query.get(session_id)
            climbs = session.climbs
        else:
            climbs = list()

        # get existing sectors and routes that have already been tried in this session
        sectors = Sector.query.filter_by(area_id=area_id).order_by(Sector.name).all()
        sector_names = [sector.name for sector in sectors]
        form.sector.datalist = sector_names
        tried_route_ids = [climb.route.id for climb in climbs]
        routes = list()
        for sector in sectors:
            routes += [
                route for route in sector.routes if route.id not in tried_route_ids
            ]
        route_names = sorted([route.name for route in routes])
        form.name.datalist = route_names  # TODO: should change according to sector

        # add the last sector of the current session if possible
        sectors = [c.route.sector for c in climbs]
        if len(sectors) > 0:
            form.sector.data = sectors[-1].name

        return form

    @classmethod
    def create_from_obj(cls, obj: Route) -> RouteForm:
        """
        Create the form with data from the route object.
        """
        form = cls.create_empty(obj.sector.area_id)
        form.height.default = obj.height
        form.inclination.default = obj.inclination
        delattr(form.name, "toggle_ids")
        for field in FIELDS:
            getattr(form, field).data = getattr(obj, field)
        if obj.sector is not None:
            form.sector.data = obj.sector.name

        return form

    def get_sector(self, area_id: str) -> Sector:
        """
        - If the sector field is empty, return None.
        - If the sector is new, create it and return it, without adding it to the DB.
        - If the sector exists, return it.
        """
        sector = None
        if len(self.sector.data) > 0:
            sector_name = self.sector.data.strip().title()
        else:
            sector_name = "Unknown"

        sector = Sector.query.filter_by(name=sector_name, area_id=area_id).first()
        if sector is None:
            sector = Sector(
                name=sector_name, area_id=area_id, created_by=current_user.id
            )
        return sector

    def get_object(self, sector: Sector, route: Route = None) -> Route:
        """
        This function is used when a new climb is added. It only checks the name field
        and returns a route object.

        - If the route exists, return it.
        - If the route is new, create it and return it, without adding it to the DB.
        """
        route_name = get_formatted_name(self.name.data)
        route = Route.query.filter_by(name=route_name, sector_id=sector.id).first()
        if route is None:
            route = Route(name=route_name, sector=sector, created_by=current_user.id)
            for field in FIELDS:
                setattr(route, field, getattr(self, field).data)

        return route

    def get_edited_route(self, route_id: int) -> Route:
        """
        This function is used when a route is edited. It checks all fields and returns
        a route object.
        """
        route = Route.query.get(route_id)
        route.name = get_formatted_name(self.name.data)
        sector_name = get_formatted_name(self.sector.data)
        sector = Sector.query.filter_by(name=sector_name).first()
        if sector is None:
            sector = Sector(name=sector_name, area_id=route.sector.area_id)
        route.sector = sector

        for field in FIELDS:
            setattr(route, field, getattr(self, field).data)

        return route


def get_formatted_name(name: str) -> str:
    """
    Return the name of the route in the correct format. It is stripped of whitespace
    and capitalized.
    """
    return name.strip().lower().title()
