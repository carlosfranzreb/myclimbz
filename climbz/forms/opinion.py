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

from climbz.models import Grade, Crux, Opinion


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
    comment = StringField("Comment", validators=[Optional()], widget=TextArea())
    submit = SubmitField("Submit")

    @classmethod
    def create_empty(cls, route_name: str) -> OpinionForm:
        """
        Create the form and add choices to the select fields.
        """
        form = cls()
        form.title = f"Opinion for {route_name}"
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
        route_name = obj.route.name
        form = cls.create_empty(route_name)
        form.rating.default = obj.rating
        form.landing.default = obj.landing
        for field in ["landing", "rating", "comment"]:
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
