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


BASE_URL = None  # set by the driver fixture


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
        GitHub Actions will run the web app as a service.
    """
    http = "http" if env == "dev" else "https"
    BASE_URL = f"{http}://127.0.0.1:5000"
    if env == "dev":
        try:
            if env == "dev":
                os.system("docker compose up -d")
            driver_options = webdriver.ChromeOptions()
            driver_options.add_argument("--headless=new")
            driver = webdriver.Chrome(options=driver_options)
            driver.get(BASE_URL)
            WebDriverWait(driver, 10).until(EC.title_is("Routes"))
            yield driver
        finally:
            driver.quit()
            if env == "dev":
                os.system("docker compose down")


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
