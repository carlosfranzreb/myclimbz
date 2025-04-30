from __future__ import annotations

from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import (
    SubmitField,
    StringField,
    SelectField,
    SelectMultipleField,
    widgets,
    IntegerRangeField,
)
from wtforms.validators import NumberRange, Optional
from wtforms.widgets import TextArea

from myclimbz.models import Grade, Crux, Opinion


class OpinionForm(FlaskForm):
    # the route is determined in the route form
    grade = SelectField("Grade", validators=[Optional()])
    rating = IntegerRangeField(
        "Rating",
        validators=[
            NumberRange(min=1, max=5, message="Please enter a rating between 1 and 5.")
        ],
        default=3,
    )
    landing = IntegerRangeField(
        "Landing",
        validators=[
            NumberRange(
                min=1, max=5, message="Please enter a landing score between 1 and 5."
            )
        ],
        default=3,
    )
    cruxes = SelectMultipleField(
        "Cruxes",
        validators=[Optional()],
        widget=widgets.ListWidget(prefix_label=False),
        option_widget=widgets.CheckboxInput(),
    )
    opinion_comment = StringField("Comment", validators=[Optional()], widget=TextArea())
    submit = SubmitField("Submit")

    @classmethod
    def create_empty(cls) -> OpinionForm:
        """
        Create the form and add choices to the select fields.
        """
        form = cls()
        cruxes = Crux.query.order_by(Crux.name).all()
        form.cruxes.choices = [(str(c.id), c.name) for c in cruxes]

        grades = Grade.query.order_by(Grade.level).all()
        form.grade.choices = [(0, "")] + [
            (g.id, getattr(g, current_user.grade_scale)) for g in grades
        ]

        form.rating.unit = "/ 5"
        form.landing.unit = "/ 5"

        return form

    @classmethod
    def create_from_obj(cls, obj: Opinion) -> OpinionForm:
        """Create the form with data from the Opinion object."""
        form = cls.create_empty()
        form.rating.default = obj.rating
        form.landing.default = obj.landing
        form.opinion_comment.data = obj.comment
        for field in ["landing", "rating"]:
            getattr(form, field).data = getattr(obj, field)

        if obj.grade is not None:
            form.grade.data = str(obj.grade.id)

        form.cruxes.data = list()
        for crux in obj.cruxes:
            form.cruxes.data.append(str(crux.id))

        return form

    def get_edited_opinion(self, opinion_id: int) -> Opinion:
        """Edit the opinion with the data from the form and return it."""
        opinion = Opinion.query.get(opinion_id)
        opinion = self._add_fields_to_object(opinion)
        return opinion

    def get_object(self, climber_id: int, route_id: int) -> Opinion:
        """
        Create an opinion object from the form data.
        If the climber has already given an opinion for this route, edit it.
        """
        opinion = Opinion.query.filter_by(
            climber_id=climber_id, route_id=route_id
        ).first()
        if opinion is None:
            opinion = Opinion()
            opinion.climber_id = climber_id
            opinion.route_id = route_id

        opinion = self._add_fields_to_object(opinion)
        return opinion

    def _add_fields_to_object(self, opinion: Opinion) -> Opinion:
        opinion.grade = Grade.query.get(int(self.grade.data))
        opinion.cruxes = [Crux.query.get(crux_id) for crux_id in self.cruxes.data]
        opinion.comment = self.opinion_comment.data

        for field in ["landing", "rating"]:
            setattr(opinion, field, getattr(self, field).data)

        return opinion
