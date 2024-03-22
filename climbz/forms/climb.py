from __future__ import annotations

from flask import session as flask_session
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField, BooleanField, StringField
from wtforms.validators import Optional

from climbz.models import Route, Climb


FIELDS = [
    "n_attempts",
    "sent",
    "flashed",
    "comment",
    "link",
]


class ClimbForm(FlaskForm):
    # the route is determined in the route form
    is_project = BooleanField("Project (not tried yet)", validators=[Optional()])
    n_attempts = IntegerField("Number of attempts", validators=[Optional()])
    comment = StringField("Comment", validators=[Optional()])
    link = StringField("Link", validators=[Optional()])
    sent = BooleanField("Sent", validators=[Optional()])
    flashed = BooleanField("Flashed", validators=[Optional()])
    add_opinion = BooleanField("Add opinion to sent climb", validators=[Optional()])
    submit = SubmitField("Submit", validators=[Optional()])

    @classmethod
    def create_from_entities(cls, entities: dict) -> ClimbForm:
        return cls(
            n_attempts=entities.get("n_attempts", None),
            sent=entities.get("sent", False),
            flashed=entities.get("flashed", False),
            comment=entities.get("comment", ""),
        )

    @classmethod
    def create_from_object(cls, obj: Climb) -> ClimbForm:
        return cls(
            n_attempts=obj.n_attempts,
            sent=obj.sent,
            flashed=obj.flashed,
            comment=obj.comment,
            link=obj.link,
        )

    def validate(self, route: Route) -> bool:
        """If the climb has already been tried before, `flashed` must be false."""
        is_valid = True
        if not super().validate():
            is_valid = False

        if route is not None:
            if route.tried and self.flashed.data is True:
                self.flashed.errors.append("This route has already been tried.")
                is_valid = False

        return is_valid

    def get_object(self, route: Route) -> Climb:
        """Create a new climb object from the form data."""
        climb = Climb(
            **{
                "route_id": route.id if route is not None else None,
                "climber_id": current_user.id,
                "session_id": flask_session["session_id"],
            }
        )
        return self.add_form_data_to_object(climb)

    def get_edited_climb(self, climb_id: int) -> Climb:
        """Fetch the object, update it and return it."""
        climb = Climb.query.get(climb_id)
        return self.add_form_data_to_object(climb)

    def add_form_data_to_object(self, obj: Climb) -> Climb:
        """Add the form data to the object."""
        for field in FIELDS:
            setattr(obj, field, getattr(self, field).data)
        return obj
