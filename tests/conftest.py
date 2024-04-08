import os
from typing import Generator
from time import sleep
from multiprocessing import Process

import pytest
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from climbz import create_app


@pytest.fixture(scope="session")
def db_session() -> Session:
    """Load the test database and create a session."""
    engine = create_engine("sqlite:///instance/test_100.db")
    session = Session(engine)
    return session


@pytest.fixture(scope="session", autouse=True)
def driver(env: str) -> Generator[webdriver.Chrome, None, None]:
    """
    If env=dev:
        Starts the Docker container with docker compose.
    Elif env=ci:
        Starts the server locally in a different process.
    """
    if env == "dev":
        try:
            os.system("docker compose up -d")
            driver_options = webdriver.ChromeOptions()
            driver_options.add_argument("--headless=new")
            driver = webdriver.Chrome(options=driver_options)
            driver.get("http://localhost:5000")
            WebDriverWait(driver, 10).until(EC.title_is("Routes"))
            yield driver
        finally:
            driver.quit()
            os.system("docker compose down")
    elif env == "ci":
        os.environ["CLIMBZ_DB_URI"] = "sqlite:///test_100.db"
        os.environ["DISABLE_LOGIN"] = "1"
        os.environ["FLASK_DEBUG"] = "0"
        os.environ["FLASK_APP"] = "climbz"
        app_process = Process(target=run_app)
        app_process.start()
        sleep(5)

        try:
            driver_options = webdriver.ChromeOptions()
            driver_options.add_argument("--headless=new")
            driver = webdriver.Chrome(options=driver_options)
            driver.get("http://127.0.0.1:5000")
            WebDriverWait(driver, 10).until(EC.title_is("Routes"))
            yield driver
        except Exception as e:
            driver.quit()
            app_process.terminate()
            raise e
        finally:
            driver.quit()
            app_process.terminate()


def run_app() -> None:
    app = create_app()
    app.run()


def pytest_addoption(parser):
    parser.addoption(
        "--env", default="dev", help="testing environment", choices=("dev", "ci")
    )


@pytest.fixture(scope="session")
def env(request):
    return request.config.getoption("--env")
