from multiprocessing import Process
from time import sleep

import pytest
from flask.testing import FlaskClient
from selenium import webdriver

from climbs import create_app


@pytest.fixture()
def app():
    app = create_app(db_name="test_100")
    app.config.update({"TESTING": True})
    yield app


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
