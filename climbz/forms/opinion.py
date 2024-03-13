from __future__ import annotations

from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import (
    IntegerField,
    SubmitField,
    StringField,
    SelectField,
    SelectMultipleField,
    widgets,
)
from wtforms.validators import Optional

from climbz.models import Grade, Crux, Opinion


class OpinionForm(FlaskForm):
    # the route is determined in the route form
    grade = SelectField("Grade", validators=[Optional()])
    rating = IntegerField("Rating", validators=[Optional()])
    landing = IntegerField("Landing", validators=[Optional()])
    cruxes = SelectMultipleField(
        "Cruxes",
        validators=[Optional()],
        widget=widgets.ListWidget(prefix_label=False),
        option_widget=widgets.CheckboxInput(),
    )
    comment = StringField("Comment", validators=[Optional()])
    submit = SubmitField("Submit")

    def add_choices(self):
        """
        Add choices to select fields: grades and cruxes.
        """
        cruxes = Crux.query.order_by(Crux.name).all()
        self.cruxes.choices = [(str(c.id), c.name) for c in cruxes]

        grades = Grade.query.order_by(Grade.level).all()
        self.grade.choices = [(0, "")] + [
            (g.id, getattr(g, current_user.grade_scale)) for g in grades
        ]

    @classmethod
    def create_empty(cls) -> OpinionForm:
        """
        Create the form and add choices to the select fields.
        """
        form = cls()
        form.add_choices()
        return form

    @classmethod
    def create_from_obj(cls, obj: Opinion) -> OpinionForm:
        """Create the form with data from the Opinion object."""
        form = cls.create_empty()
        for field in ["landing", "rating", "comment"]:
            getattr(form, field).data = getattr(obj, field)

        if obj.grade is not None:
            form.grade.data = str(obj.grade.id)

        form.cruxes.data = list()
        for crux in obj.cruxes:
            form.cruxes.data.append(str(crux.id))

        return form

    @classmethod
    def create_from_entities(
        cls, entities: dict, grade_scale: str = "font"
    ) -> OpinionForm:
        """
        Create the form with the given entities.

        Args:
            entities: Dictionary of entities to select options from.
            grade_scale: The grade scale to use.
        """

        form = cls()
        form.add_choices(grade_scale)

        for field in ["landing", "rating", "comment"]:
            if field in entities:
                getattr(form, field).data = entities[field]

        if "grade" in entities:
            value = entities["grade"]
            if grade_scale == "hueco":
                grade = Grade.query.filter_by(hueco=value).first()
            else:
                grade = Grade.query.filter_by(font=value).first()
            if grade is not None:
                getattr(form, field).data = str(grade.id)
        else:
            getattr(form, field).data = 0

        if "cruxes" in entities:
            form.cruxes.data = list()
            if isinstance(entities["cruxes"], str):
                entities["cruxes"] = [entities["cruxes"]]
            for crux in entities["cruxes"]:
                crux_obj = Crux.query.filter_by(name=crux).first()
                if crux_obj is not None:
                    form.cruxes.data.append(str(crux_obj.id))

        return form

    def get_edited_opinion(self, opinion_id: int) -> Opinion:
        """Edit the opinion with the data from the form and return it."""
        opinion = Opinion.query.get(opinion_id)
        opinion.grade = Grade.query.get(int(self.grade.data))
        opinion.cruxes = [Crux.query.get(crux_id) for crux_id in self.cruxes.data]

        for field in [
            "landing",
            "rating",
            "comment",
        ]:
            setattr(opinion, field, getattr(self, field).data)

        return opinion

    def get_object(self, climber_id: int, route_id: int) -> Opinion:
        """Create an opinion object from the form data."""
        opinion = Opinion()
        opinion.climber_id = climber_id
        opinion.route_id = route_id
        opinion.grade = Grade.query.get(int(self.grade.data))
        opinion.cruxes = [Crux.query.get(crux_id) for crux_id in self.cruxes.data]

        for field in ["landing", "rating", "comment"]:
            setattr(opinion, field, getattr(self, field).data)

        return opinion
