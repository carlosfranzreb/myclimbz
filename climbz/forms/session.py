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
            NumberRange(min=1, max=5, message="Rate the conditions from 1 to 5.")
        ],
        default=3,
    )
    comment = StringField("Comment", validators=[Optional()], widget=TextArea())

    def validate(self) -> bool:
        """
        Check if the form is valid. Besides the field validators, the session must be
        unique, i.e. the climber-area-date combination must be unique.
        """
        if not super().validate():
            return False

        area = self.get_area()
        if area.id is None:
            return True

        session = Session.query.filter_by(
            climber_id=current_user.id, area_id=area.id, date=self.date.data
        ).first()
        if session is not None:
            self.date.errors.append("You already have a session on that date and area.")
            return False

        return True

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
            form.is_project_search.toggle_ids = "date,conditions,comment"
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
        - If the area is new, create it and return it, without adding it to the DB.
        - If the area exists, return it.
        """
        area = None
        area_name = self.area.data.strip().lower().title()
        area = Area.query.filter_by(name=area_name).first()
        if area is None:
            area = Area(name=area_name, created_by=current_user.id)
            if self.rock_type.data != "":
                area.rock_type = RockType.query.get(self.rock_type.data)

        return area

    def get_object(self, area_id: int) -> Session:
        """
        Create an object out of the form data.
        """
        obj = Session()
        obj.climber_id = current_user.id
        obj.area_id = area_id
        return self.edit_object(obj)

    def edit_object(self, obj: Session) -> Session:
        """
        Update the session object with the form fields that can be edited.
        """
        date_obj = datetime.strptime(self.date.data, "%d/%m/%Y")
        obj.date = date_obj.strftime("%Y-%m-%d")
        for attr in ["conditions", "comment"]:
            setattr(obj, attr, getattr(self, attr).data)
        return obj
