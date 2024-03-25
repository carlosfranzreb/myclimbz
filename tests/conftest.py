import os

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sqlalchemy import create_engine
from sqlalchemy.orm import Session


@pytest.fixture(scope="session")
def db_session() -> Session:
    """Load the test database and create a session."""
    engine = create_engine("sqlite:///instance/test_100.db")
    session = Session(engine)
    return session


@pytest.fixture(scope="session", autouse=True)
def driver():
    """Starts the Docker container and terminates it after the test."""
    try:
        os.system("docker compose up -d")
        driver = login()
        yield driver
    finally:
        driver.quit()
        os.system("docker compose down")


def login():
    # start a headless Chrome browser
    driver_options = webdriver.ChromeOptions()
    driver_options.add_argument("--headless=new")
    driver = webdriver.Chrome(options=driver_options)
    driver.get("http://127.0.0.1:5000/login")
    WebDriverWait(driver, 10).until(EC.title_is("Login"))

    # log in
    driver.find_element(By.ID, "email").send_keys("c1@climbz.com")
    driver.find_element(By.ID, "password").send_keys("123")
    driver.find_element(By.XPATH, "//input[@type='submit']").click()
    WebDriverWait(driver, 10).until(EC.title_is("Routes"))

    return driver
