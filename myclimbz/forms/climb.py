"""
Form for the climb model.

This form can be used together with a RouteForm object. Because RouteForm also has
the fields "comment" and "link", here they are prepended with "climb_" to avoid
conflicts. Otherwise, Flask-WTF overrides these fields with the values from the
RouteForm object.
"""

from __future__ import annotations

from flask import session as flask_session, abort
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import IntegerField, BooleanField, StringField
from wtforms.validators import Optional
from wtforms.widgets import TextArea

from myclimbz.models import Route, Climb, Session, Sector
from myclimbz.forms.utils import format_name

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
        """
        - If the climb has already been tried before, `flashed` must be false.
        """
        is_valid = True
        if not super().validate():
            is_valid = False

        if route is None:
            return is_valid

        if session_id is None:
            session_id = flask_session["session_id"]

        # check whether a flash is valid
        if self.flashed.data is True:
            if not self.sent.data:
                self.flashed.errors.append("A flashed climb must be sent.")
                is_valid = False
            if self.n_attempts.data is not None and self.n_attempts.data > 1:
                self.flashed.errors.append("A flashed climb must have 1 attempt.")
                is_valid = False
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

    def validate_from_name(self, route_name: str, sector_name: str) -> bool:
        route_name = format_name(route_name)
        sector_name = format_name(sector_name)
        sector = Sector.query.filter_by(name=sector_name).first()
        route = (
            Route.query.filter_by(name=route_name, sector_id=sector.id).first()
            if sector is not None
            else None
        )
        return self.validate(route)

    def get_object(self, route: Route) -> Climb:
        """
        - If this route has already been climbed in this session, update the
            corresponding climb and return it.
        - Otherwise, create a new climb object from the form data.
        """

        # check whether the route has already been tried in this session
        climbs = Climb.query.filter_by(
            route_id=route.id, session_id=flask_session["session_id"]
        ).all()
        if len(climbs) > 1:
            abort(500)  # there shouldn't be more than one climb per route per session
        elif len(climbs) == 1:
            climb = climbs[0]

            # update the existing values with the new ones
            climb.sent = climb.sent or self.sent.data
            climb.flashed = climb.flashed or self.flashed.data
            climb.n_attempts += self.n_attempts.data
            if len(self.climb_comment.data) > 0:
                if climb.comment:
                    climb.comment += "\n" + self.climb_comment.data
                else:
                    climb.comment = self.climb_comment.data
            if len(self.climb_link.data) > 0 and not len(climb.link):
                climb.link = self.climb_link.data

        else:
            climb = Climb(
                **{
                    "route_id": route.id,
                    "session_id": flask_session["session_id"],
                }
            )
            climb = self.add_form_data_to_object(climb)

        return climb

    def get_edited_climb(self, climb_id: int) -> Climb:
        """Fetch the object, update it and return it."""
        climb = Climb.query.get(climb_id)
        return self.add_form_data_to_object(climb)

    def add_form_data_to_object(self, obj: Climb) -> Climb:
        """Add the form data to the object."""
        for field in FIELDS:
            setattr(obj, field.replace("climb_", ""), getattr(self, field).data)
        return obj
