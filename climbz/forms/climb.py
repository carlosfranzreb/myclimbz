from __future__ import annotations

from flask import session as flask_session
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import IntegerField, BooleanField, StringField
from wtforms.validators import Optional
from wtforms.widgets import TextArea

from climbz.models import Route, Climb, Session


FIELDS = [
    "n_attempts",
    "sent",
    "flashed",
    "climb_comment",
    "climb_link",
]


class ClimbForm(FlaskForm):
    # the route is determined in the route form
    is_project = BooleanField("Project (not tried yet)", validators=[Optional()])
    n_attempts = IntegerField("Number of attempts", validators=[Optional()])
    climb_comment = StringField("Comment", validators=[Optional()], widget=TextArea())
    climb_link = StringField("Link", validators=[Optional()])
    sent = BooleanField("Sent", validators=[Optional()])
    flashed = BooleanField("Flashed", validators=[Optional()])
    add_opinion = BooleanField(
        "Add opinion after submitting this form", validators=[Optional()]
    )

    @classmethod
    def create_empty(cls) -> ClimbForm:
        form = cls()
        form.is_project.toggle_ids = "n_attempts,climb_comment,climb_link,sent,flashed"
        return form

    @classmethod
    def create_from_object(cls, obj: Climb) -> ClimbForm:
        form = cls.create_empty()
        for field in FIELDS:
            getattr(form, field).data = getattr(obj, field.replace("climb_", ""))
        return form

    def validate(self, route: Route, session_id: int = None) -> bool:
        """If the climb has already been tried before, `flashed` must be false."""
        is_valid = True
        if not super().validate():
            is_valid = False

        if route is not None and self.flashed.data is True:
            if self.n_attempts.data is not None and self.n_attempts.data > 1:
                self.flashed.errors.append("A flashed climb must have 1 attempt.")
                return False

            if session_id is None:
                session_id = flask_session["session_id"]

            session = Session.query.get(session_id)
            climbs = Climb.query.filter_by(
                route_id=route.id, climber_id=current_user.id
            ).all()
            if len(climbs) > 0:
                first_date = min([climb.session.date for climb in climbs])
                if session.date > first_date:
                    print(session.date, first_date)
                    self.flashed.errors.append(
                        "This is not your first session. A flash is not possible."
                    )
                    is_valid = False

        return is_valid

    def validate_from_name(self, route_name: str) -> bool:
        """If the climb has already been tried before, `flashed` must be false."""
        route = Route.query.filter_by(name=route_name).first()
        return self.validate(route)

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
