from __future__ import annotations
from datetime import datetime

from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import IntegerField, DateField, StringField, SelectField, BooleanField
from wtforms.validators import Optional

from climbz.models import Area, RockType, Session


class SessionForm(FlaskForm):
    area = StringField("Area name")
    date = DateField("Date", validators=[Optional()])
    conditions = IntegerField("Conditions", validators=[Optional()])
    rock_type = SelectField("Rock Type of new area", validators=[Optional()])
    is_project_search = BooleanField(
        "Only adding projects (not climbing)", validators=[Optional()]
    )
    comment = StringField("Comment", validators=[Optional()])

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
        for field in ["date", "conditions", "area", "is_project_search", "comment"]:
            if field in entities:
                getattr(form, field).data = entities[field]

        # ! This is commented out until the NER is implemented
        # if "area" in entities:
        #     area = get_area_from_entities(entities)
        #     if area.id is None and "rock" in entities:
        #         rock = RockType.query.filter_by(name=entities["rock"]).first()
        #         if rock is not None:
        #             form.rock_type.data = str(rock.id)
        #     else:
        #         form.rock_type.data = "0"

        # if date is null, set it to today
        if form.date.data is None:
            form.date.data = datetime.today()

        return form

    @classmethod
    def create_from_object(cls, session: Session) -> SessionForm:
        """
        Create an "entities" dictionary from the session object and call
        create_from_entities.
        """
        entities = {
            "date": session.date,
            "conditions": session.conditions,
            "area": session.area.name if session.area is not None else None,
            "is_project_search": session.is_project_search,
            "comment": session.comment,
        }
        if session.area is not None and session.area.rock_type is not None:
            entities["rock"] = session.area.rock_type.name
        return cls.create_from_entities(entities)

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

    def get_object(self, area_id: int, obj: Session = None) -> Session:
        """
        Return a Session object from the form data. If an object is passed, update it.
        If not, create a new one.
        """
        if obj is None:
            obj = Session()
        obj.climber_id = current_user.id
        obj.area_id = area_id

        for attr in ["date", "conditions", "is_project_search", "comment"]:
            setattr(obj, attr, getattr(self, attr).data)

        return obj
