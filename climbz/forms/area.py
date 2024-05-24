from __future__ import annotations

from flask_wtf import FlaskForm
from wtforms import SelectField, StringField
from wtforms.validators import Optional

from climbz.models import RockType, Area


class AreaForm(FlaskForm):
    """
    Form used to edit areas.
    """

    name = StringField("Area name", validators=[Optional()])
    rock_type = SelectField("Rock Type", validators=[Optional()])

    @classmethod
    def create_empty(cls) -> AreaForm:
        """Add choices to select fields: rock types."""
        form = cls()
        form.rock_type.choices = [(0, "")] + [
            (r.id, r.name) for r in RockType.query.all()
        ]
        form.name.datalist = [
            area.name for area in Area.query.order_by(Area.name).all()
        ]
        return form

    @classmethod
    def create_from_obj(cls, obj: Area) -> AreaForm:
        """Create a form with the data from an area."""
        form = cls.create_empty()
        form.name.data = obj.name
        form.rock_type.data = str(obj.rock_type.id) if obj.rock_type is not None else 0
        return form

    def validate(self, old_name: str = None) -> bool:
        """Check that the area name is unique."""
        is_valid = True
        if not super().validate():
            is_valid = False

        # if the name has changed, check if it already exists
        if self.name.data != old_name:
            if Area.query.filter_by(name=self.name.data).first() is not None:
                self.name.errors.append("An area with that name already exists.")
                is_valid = False

        return is_valid
