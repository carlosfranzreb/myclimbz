from multiprocessing import Process
from time import sleep

import pytest
from flask.testing import FlaskClient
from selenium import webdriver

from climbz import create_app, db


@pytest.fixture()
def app():
    app = create_app(db_name="test_100")
    app.config.update({"TESTING": True})
    yield app


@pytest.fixture
def test_client_db():
    """Returns a test client for the app"""
    app = create_app(db_name="test_100")
    app.testing = True
    with app.test_client() as test_client:
        with app.app_context():
            db.create_all()
            yield test_client


@pytest.fixture()
def test_client() -> FlaskClient:
    """Returns a test client for the app, closing it after the test."""
    app = create_app(db_name="test_100")
    app.testing = True
    return app.test_client()


def run_app() -> None:
    app = create_app(db_name="test_100")
    app.run()


@pytest.fixture()
def driver() -> webdriver.Chrome:
    """Starts the Chrome webdriver and terminates it after the test."""
    app_process = Process(target=run_app)
    app_process.start()
    sleep(10)

    driver = webdriver.Chrome()
    yield driver
    driver.quit()
    app_process.terminate()
