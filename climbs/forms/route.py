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

    def populate_from_obj(self, obj: Route):
        """
        Select options of select fields with the values of the given object.
        """

        for field in ["name", "height", "inclination", "landing", "sit_start"]:
            getattr(self, field).data = getattr(obj, field)

        if obj.sector is not None:
            self.sector.data = obj.sector.name

        if obj.grade is not None:
            self.grade.data = obj.grade.id
        if obj.grade_felt is not None:
            self.grade_felt.data = obj.grade_felt.id

        self.cruxes.data = list()
        for crux in obj.cruxes:
            self.cruxes.data.append(str(crux.id))

    def populate_from_entities(self, entities: dict, grade_scale: str):
        """
        Select options of select fields with the given entities.

        Args:
            entities: Dictionary of entities to select options from.
            grade_scale: The grade scale to use.
        """
        entities = {k.lower(): v for k, v in entities.items()}

        for field in ["name", "name", "height", "inclination", "landing", "sit_start"]:
            if field in entities:
                getattr(self, field).data = entities[field]

        for field in ["grade", "grade_felt"]:
            value = entities.get(field, None)
            if value is not None:
                if grade_scale == "hueco":
                    grade = Grade.query.filter_by(hueco=value).first()
                else:
                    grade = Grade.query.filter_by(font=value).first()
                getattr(self, field).data = str(grade.id)
            else:
                getattr(self, field).data = 0

        for field in ["height", "inclination", "landing", "sit_start"]:
            if field in entities:
                getattr(self, field).data = entities[field]

        if "crux" in entities:
            self.cruxes.data = list()
            for crux in entities["crux"]:
                self.cruxes.data.append(str(Crux.query.filter_by(name=crux).first().id))
