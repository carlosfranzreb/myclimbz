from multiprocessing import Process
from time import sleep

import pytest
from flask.testing import FlaskClient
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By


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
    # start the app
    app_process = Process(target=run_app)
    app_process.start()
    sleep(10)

    # start the driver
    driver_options = webdriver.ChromeOptions()
    # driver_options.add_argument("--headless=new")
    driver = webdriver.Chrome(options=driver_options)
    try:

        # login
        login_url = "http://localhost:5000/login"
        driver.get(login_url)
        WebDriverWait(driver, 10).until(lambda driver: driver.current_url == login_url)
        driver.find_element(By.XPATH, "//input[@id='email']").send_keys("c1@climbz.com")
        driver.find_element(By.XPATH, "//input[@id='password']").send_keys("123")
        driver.find_element(By.XPATH, "//input[@value='Submit']").click()
        WebDriverWait(driver, 10).until(
            lambda driver: driver.current_url == "http://localhost:5000/"
        )
    except Exception as e:
        driver.quit()
        app_process.terminate()
        raise e

    # yield the driver and then quit it
    try:
        yield driver
    finally:
        driver.quit()
        app_process.terminate()
