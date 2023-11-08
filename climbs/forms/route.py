from __future__ import annotations

from flask_wtf import FlaskForm
from wtforms import (
    IntegerField,
    StringField,
    SelectField,
    FloatField,
    BooleanField,
    SelectMultipleField,
    widgets,
)
from wtforms.validators import Optional

from climbs.models import Grade, Route, Sector, Crux


class RouteForm(FlaskForm):
    name = StringField("Route name", validators=[Optional()])
    sector = StringField("Sector", validators=[Optional()])
    grade = SelectField("Grade", validators=[Optional()])
    grade_felt = SelectField("Grade felt", validators=[Optional()])
    height = FloatField("Height", validators=[Optional()])
    inclination = IntegerField("Inclination", validators=[Optional()])
    landing = IntegerField("Landing", validators=[Optional()])
    sit_start = BooleanField("Sit Start", validators=[Optional()])
    cruxes = SelectMultipleField(
        "Cruxes",
        validators=[Optional()],
        widget=widgets.ListWidget(prefix_label=False),
        option_widget=widgets.CheckboxInput(),
    )

    def validate(self):
        """
        Check that only one of the new and existing fields is filled. Sector is only
        checked if a new route is given. If the form is valid, change the grades to
        their objects.

        Args:
            is_edit: Whether the form is used for editing a route. If so, the route
                name is allowed to be the same as the name of an existing route.
        """
        self.cruxes.data = [int(c) for c in self.cruxes.data]
        is_valid = True
        if not super().validate():
            is_valid = False

        if is_valid:
            for field in ["grade", "grade_felt"]:
                getattr(self, field).data = Grade.query.get(getattr(self, field).data)

        return is_valid

    def add_choices(self, grade_scale: str):
        """
        Add choices to select fields: grades and cruxes.
        """
        cruxes = Crux.query.order_by(Crux.name).all()
        self.cruxes.choices = [(c.id, c.name) for c in cruxes]

        grades = Grade.query.order_by(Grade.level).all()
        for field in ["grade", "grade_felt"]:
            getattr(self, field).choices = [(0, "")] + [
                (g.id, getattr(g, grade_scale)) for g in grades
            ]

    @classmethod
    def create_empty(cls, grade_scale: str = "font") -> RouteForm:
        """
        Create the form and add choices to the select fields.
        """
        form = cls()
        form.add_choices(grade_scale)
        return form

    @classmethod
    def create_from_obj(cls, obj: Route, grade_scale: str = "font") -> RouteForm:
        """
        Create the form with data from the route object.
        """
        form = cls()
        form.add_choices(grade_scale)
        for field in ["name", "height", "inclination", "landing", "sit_start"]:
            getattr(form, field).data = getattr(obj, field)

        if obj.sector is not None:
            form.sector.data = obj.sector.name

        if obj.grade is not None:
            form.grade.data = str(obj.grade.id)
        if obj.grade_felt is not None:
            form.grade_felt.data = str(obj.grade_felt.id)

        form.cruxes.data = list()
        for crux in obj.cruxes:
            form.cruxes.data.append(str(crux.id))

        return form

    @classmethod
    def create_from_entities(cls, entities: dict, grade_scale: str) -> RouteForm:
        """
        Create the form with the given entities.

        Args:
            entities: Dictionary of entities to select options from.
            grade_scale: The grade scale to use.
        """

        form = cls()
        form.add_choices(grade_scale)

        for field in ["name", "name", "height", "inclination", "landing", "sit_start"]:
            if field in entities:
                getattr(form, field).data = entities[field]

        for field in ["grade", "grade_felt"]:
            value = entities.get(field, None)
            if value is not None:
                if grade_scale == "hueco":
                    grade = Grade.query.filter_by(hueco=value).first()
                else:
                    grade = Grade.query.filter_by(font=value).first()
                getattr(form, field).data = str(grade.id)
            else:
                getattr(form, field).data = 0

        for field in ["height", "inclination", "landing", "sit_start"]:
            if field in entities:
                getattr(form, field).data = entities[field]

        if "crux" in entities:
            form.cruxes.data = list()
            for crux in entities["crux"]:
                form.cruxes.data.append(str(Crux.query.filter_by(name=crux).first().id))

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
            sector = Sector(name=sector_name, area_id=area_id)
        return sector

    def get_route(self, sector: Sector = None) -> Route:
        """
        If the route field is empty, return None.
        If the route is new, create it and return it, without adding it to the DB.
        If the route exists, return it.
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
                "landing",
                "sit_start",
                "grade",
                "grade_felt",
            ]:
                setattr(route, field, getattr(self, field).data)

            for crux_id in self.cruxes.data:
                crux = Crux.query.get(crux_id)
                route.cruxes.append(crux)

        return route
