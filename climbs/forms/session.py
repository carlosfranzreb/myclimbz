from __future__ import annotations

from flask_wtf import FlaskForm
from wtforms import IntegerField, DateField, StringField, SelectField
from wtforms.validators import Optional

from climbs.models import Area, RockType
from climbs.ner.entities_to_objects import get_area_from_entities


class SessionForm(FlaskForm):
    date = DateField("Date", validators=[Optional()])
    conditions = IntegerField("Conditions", validators=[Optional()])
    area = StringField("Area name", validators=[Optional()])
    rock_type = SelectField("Rock Type of new area", validators=[Optional()])

    def add_choices(self):
        """Add choices to select fields: rock types."""
        self.rock_type.choices = [(0, "")] + [
            (r.id, r.name) for r in RockType.query.all()
        ]

    @classmethod
    def create_empty(cls) -> SessionForm:
        """
        Create the form and add choices to the select fields.
        """
        form = cls()
        form.add_choices()
        return form

    @classmethod
    def create_from_entities(cls, entities: dict) -> SessionForm:
        """
        Create the form with data from the entities.
        """
        form = cls()
        form.add_choices()
        entities = {k.lower(): v for k, v in entities.items()}
        for field in ["date", "conditions", "area"]:
            if field in entities:
                getattr(form, field).data = entities[field]

        area = get_area_from_entities(entities)
        if area.id is None and "rock" in entities:
            rock_id = RockType.query.filter_by(name=entities["rock"]).first().id
            form.rock_type.data = str(rock_id)
        else:
            form.rock_type.data = "0"

        return form

    def get_area(self) -> Area:
        """
        - If the area field is empty, return None.
        - If the area is new, create it and return it, without adding it to the DB.
        - If the area exists, return it.
        """
        area = None
        if len(self.area.data) > 0:
            area_name = self.area.data.strip()
            area = Area.query.filter_by(name=area_name).first()
            if area is None:
                if self.rock_type.data != "":
                    rock_type = RockType.query.get(self.rock_type.data)
                    area = Area(name=area_name, rock_type=rock_type)
                else:
                    area = Area(name=area_name)
        return area
