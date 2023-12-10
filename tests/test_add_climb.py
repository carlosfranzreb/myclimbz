import pytest
from climbs import create_app
from flask import session
from flask.testing import FlaskClient
from flask import Flask
from climbs.forms import RouteForm


@pytest.fixture()
def app():
    app = create_app(True)
    app.config["WTF_CSRF_ENABLED"] = False
    app.config.update(
        {
            "TESTING": True,
        }
    )

    # other setup can go here

    yield app

    # clean up / reset resources here


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()
