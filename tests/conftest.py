import os
from typing import Generator
import sys
import locale

import pytest
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sqlalchemy import create_engine
from sqlalchemy.orm import Session


HOME_TITLE = "myclimbz - Home"
HOME_URL = "http://127.0.0.1:5000"
CLIMBER_ID = 1
SLEEP_TIME = 2

# Set the locale to en_US to avoid issues with date formatting
locale.setlocale(locale.LC_TIME, "en_US.UTF-8")
locale.setlocale(locale.LC_ALL, "en_US.UTF-8")


@pytest.fixture(scope="module")
def db_session() -> Session:
    return Session(create_engine("sqlite:///instance/test_100.db"))


@pytest.fixture(scope="module", autouse=True)
def driver() -> Generator[webdriver.Chrome, None, None]:
    """
    If env=dev:
        Starts the Docker container with docker compose.
    Elif env=ci:
        GitHub Actions will run the web app as a service.
    """

    is_ci = os.environ.get("CI", False)
    try:
        if not is_ci:
            os.system("git checkout instance/test_100.db")
            assert os.environ["DISABLE_LOGIN"] == "1", "DISABLE_LOGIN must be set to 1"
            assert (
                os.environ["CLIMBZ_DB_URI"] == "sqlite:///test_100.db"
            ), "The DB URI is not set to the test DB"
            assert os.environ["PROD"] == "0", "PROD must be set to 0"
            os.system("docker compose up --build -d")

        driver_options = webdriver.ChromeOptions()
        driver_options.add_argument("--window-size=2560,1440")
        if "debugpy" not in sys.modules:
            driver_options.add_argument("--headless")
        driver = webdriver.Chrome(options=driver_options)
        driver.get("http://127.0.0.1:5000")
        WebDriverWait(driver, 30).until(EC.title_is("myclimbz - Home"))
        yield driver

    finally:
        if not is_ci:
            os.system("docker compose down")
            os.system("git checkout instance/test_100.db")
        driver.quit()
