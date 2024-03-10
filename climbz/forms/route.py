from __future__ import annotations

from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, FloatField, BooleanField
from wtforms.validators import Optional

from climbz.models import Route, Sector


class RouteForm(FlaskForm):
    name = StringField("Route name", validators=[Optional()])
    sector = StringField("Sector", validators=[Optional()])
    height = FloatField("Height", validators=[Optional()])
    inclination = IntegerField(
        "Inclination", validators=[Optional()], render_kw={"step": "5"}
    )
    sit_start = BooleanField("Sit Start", validators=[Optional()])

    @classmethod
    def create_empty(cls) -> RouteForm:
        """
        Create the form and add choices to the select fields.
        """
        return cls()

    @classmethod
    def create_from_obj(cls, obj: Route) -> RouteForm:
        """
        Create the form with data from the route object.
        """
        form = cls()
        for field in ["name", "height", "inclination", "sit_start"]:
            getattr(form, field).data = getattr(obj, field)
        if obj.sector is not None:
            form.sector.data = obj.sector.name

        return form

    @classmethod
    def create_from_entities(cls, entities: dict) -> RouteForm:
        """
        Create the form with the given entities.

        Args:
            entities: Dictionary of entities to select options from.
            grade_scale: The grade scale to use.
        """
        form = cls()
        for field in ["name", "height", "inclination", "sit_start"]:
            if field in entities:
                getattr(form, field).data = entities[field]

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

        sector = Sector.query.filter_by(name=sector_name).first()
        if sector is None:
            sector = Sector(
                name=sector_name, area_id=area_id, created_by=current_user.id
            )
        return sector

    def get_route_from_climb_form(
        self, sector: Sector = None, route: Route = None
    ) -> Route:
        """
        This function is used when a new climb is added. It only checks the name field
        and returns a route object.

        - If the route field is empty, return None.
        - If the route is new, create it and return it, without adding it to the DB.
        - If the route exists, return it.
        """
        route = None
        if len(self.name.data) > 0:
            route_name = self.name.data.strip().title()
            route = Route.query.filter_by(name=route_name).first()
            if route is None:
                route = Route(name=route_name, sector=sector)
                for field in [
                    "height",
                    "inclination",
                    "sit_start",
                ]:
                    setattr(route, field, getattr(self, field).data)

        return route

    def get_edited_route(self, route_id: int) -> Route:
        """
        This function is used when a route is edited. It checks all fields and returns
        a route object.
        """
        route = Route.query.get(route_id)
        if len(self.name.data) > 0:
            route_name = self.name.data.strip().title()
            route.name = route_name

        sector_name = self.sector.data.strip().title()
        sector = Sector.query.filter_by(name=sector_name).first()
        if sector is None:
            sector = Sector(name=sector_name, area_id=route.sector.area_id)
        route.sector = sector

        for field in [
            "height",
            "inclination",
            "sit_start",
        ]:
            setattr(route, field, getattr(self, field).data)

        return route
