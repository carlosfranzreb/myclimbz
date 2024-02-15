import json
from flask import session as flask_session
from climbz.models import Predictions
from climbz import db


def dump_predictions() -> None:
    predictions = Predictions(**flask_session["predictions"])
    predictions.entities = json.dumps(
        {k: v for k, v in flask_session["entities"].items() if k != "date"}
    )
    db.session.add(predictions)
    db.session.commit()
    flask_session.pop("predictions")
