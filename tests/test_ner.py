import pytest
from climbz import create_app
from flask import session
from flask.testing import FlaskClient
from flask import Flask
from climbz.forms import RouteForm


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


def test_form_opens_when_ner_finds_no_name(client: FlaskClient, app: Flask):
    with client.session_transaction() as sess:
        sess["entities"] = {}
        sess["project_search"] = True
        sess["area_id"] = 1

    r = client.get("/add_climb")
    assert r.status_code == 200
