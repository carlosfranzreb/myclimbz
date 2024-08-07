from __future__ import annotations
from datetime import datetime

from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import (
    DateField,
    StringField,
    SelectField,
    BooleanField,
    IntegerRangeField,
)
from wtforms.validators import Optional, DataRequired, NumberRange
from wtforms.widgets import TextArea

from climbz.models import Area, RockType, Session


class SessionForm(FlaskForm):
    area = StringField("Area name", validators=[DataRequired("You must enter an area")])
    rock_type = SelectField("Rock Type of new area", validators=[Optional()])
    is_project_search = BooleanField(
        "Only adding projects (not climbing)", validators=[Optional()]
    )
    date = DateField(
        "Date",
        validators=[DataRequired("You must enter a date")],
        default=datetime.today,
    )
    conditions = IntegerRangeField(
        "Conditions",
        validators=[
            NumberRange(
                min=1, max=5, message="Please enter a landing score between 1 and 5."
            )
        ],
        default=3,
    )
    comment = StringField("Comment", validators=[Optional()], widget=TextArea())

    @classmethod
    def create_empty(cls, is_edit: bool = False) -> SessionForm:
        """
        Create the form and add rock types, existing areas and toggle flows.
        """
        form = cls()
        if is_edit:
            del form.area
            del form.rock_type
            del form.is_project_search
        else:
            form.rock_type.choices = [(0, "")] + [
                (r.id, r.name) for r in RockType.query.all()
            ]
            form.area.datalist = [
                area.name for area in Area.query.order_by(Area.name).all()
            ]
            form.area.toggle_ids = "rock_type"
            form.is_project_search.toggle_ids = "date,conditions"
        return form

    @classmethod
    def create_from_object(cls, session: Session) -> SessionForm:
        """
        Create an session form from a session object. This form is used to edit the
        session, where changing the area and setting it as a project search are not
        allowed.
        """
        form = cls.create_empty(is_edit=True)
        form.conditions.default = session.conditions
        for field in ["date", "conditions", "comment"]:
            getattr(form, field).data = getattr(session, field)
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
                    area = Area(
                        name=area_name, rock_type=rock_type, created_by=current_user.id
                    )
                else:
                    area = Area(name=area_name, created_by=current_user.id)
        return area

    def get_object(self, area_id: int, obj: Session = None) -> Session:
        """
        Return a Session object from the form data. If an object is passed, update it.
        If not, create a new one.
        """
        new_obj = obj is None
        if obj is None:
            obj = Session()
        obj.climber_id = current_user.id
        obj.area_id = area_id

        for attr in ["date", "conditions", "comment"]:
            setattr(obj, attr, getattr(self, attr).data)
        if new_obj:
            obj.is_project_search = self.is_project_search.data

        return obj
