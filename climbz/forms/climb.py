from __future__ import annotations

from flask import session as flask_session
from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField, BooleanField
from wtforms.validators import Optional

from climbz.models import Route, Climb


class ClimbForm(FlaskForm):
    # the route is determined in the route form
    is_project = BooleanField("Project (not tried yet)", validators=[Optional()])
    n_attempts = IntegerField("Number of attempts", validators=[Optional()])
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
        )

    def validate(self, route_name: str) -> bool:
        """If the climb has already been tried before, `flashed` must be false."""
        is_valid = True
        if not super().validate():
            is_valid = False

        route = Route.query.filter_by(name=route_name).first()
        if route is not None:
            if route.tried and self.flashed.data is True:
                self.flashed.errors.append("This route has already been tried.")
                is_valid = False

        return is_valid

    def get_object(self, route: Route) -> Climb:
        """Create a new climb object from the form data."""
        return Climb(
            **{
                "n_attempts": self.n_attempts.data,
                "sent": self.sent.data,
                "route_id": route.id if route is not None else None,
                "session_id": flask_session["session_id"],
                "flashed": self.flashed.data,
            }
        )
