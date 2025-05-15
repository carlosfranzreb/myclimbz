from time import sleep
import os
from typing import Generator
import sys
from datetime import datetime

import pytest
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session


HOME_TITLE = "myclimbz - Home"
HOME_URL = "http://127.0.0.1:5000"
CLIMBER_ID = 1
SLEEP_TIME = 2
IS_CI = os.environ.get("CI", False)
EXISTING_OBJECTS = {
    "area": "A1",
    "sector": "A1 S1",
    "session_date": datetime(2023, 1, 13),
}
NEW_OBJECTS = {
    "area": "A3",
    "sector": "A3 S1",
    "route": "Terranova 2",
    "session_date": datetime(2023, 1, 2),
}


@pytest.fixture(scope="session")
def db_session() -> Session:
    return Session(create_engine("sqlite:///instance/test_100.db"))


@pytest.fixture(scope="session", autouse=True)
def driver() -> Generator[webdriver.Chrome, None, None]:
    """
    If env=dev:
        Starts the Docker container with docker compose.
    Elif env=ci:
        GitHub Actions will run the web app as a service.
    """

    try:
        if not IS_CI:
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
            driver_options.add_argument("--headless=new")

        driver = webdriver.Chrome(options=driver_options)
        driver.get("http://127.0.0.1:5000")
        WebDriverWait(driver, 30).until(EC.title_is("myclimbz - Home"))
        yield driver

    finally:
        if not IS_CI:
            os.system("docker compose down")
            os.system("git checkout instance/test_100.db")
        driver.quit()


@pytest.fixture(scope="session")
def started_session_id(driver, db_session) -> Generator:
    """
    Start a session on an existing area and return its ID. The session will be
    deleted after the test is done.

    `test_create_session_on_existing_area` checks that the session was properly created.
    """

    # create the session
    stop_session(driver)
    date_obj = NEW_OBJECTS["session_date"]
    print(f"Date: {date_obj.strftime('%d.%m.%Y')}")

    area = EXISTING_OBJECTS["area"]
    form_accepted = start_session(driver, area, date_obj)
    assert form_accepted
    sleep(SLEEP_TIME)

    sql_query = text("SELECT id, date, climber_id, area_id FROM climbing_session")
    results = db_session.execute(sql_query).fetchall()
    print(results)
    print("Expected ", date_obj.strftime("%Y-%m-%d"), CLIMBER_ID, area)

    # get and yield the ID of the created session
    sql_query = text(
        f"""
        SELECT id FROM climbing_session
        WHERE date = '{date_obj.strftime("%Y-%m-%d")}'
        AND climber_id = {CLIMBER_ID}
        AND area_id = (SELECT id FROM area WHERE name = '{area}');
        """
    )
    results = db_session.execute(sql_query).fetchall()
    print(results)
    yield results[0][0]
    stop_session(driver)


def start_session(
    driver, area: str, date: datetime, expect_success: bool = True
) -> bool:
    """
    Start a session on the given area and date.

    Args:
        driver: The browser driver.
        area: The name of the area.
        date: The date of the session.
        expect_success: whether the form is expected to be accepted.

    Returns:
        bool: True if the form was accepted.
    """
    if date is None:
        date_str = ""
    elif IS_CI:
        date_str = date.strftime("%m.%d.%Y")
    else:
        date_str = date.strftime("%d.%m.%Y")
    form_accepted = fill_form(
        driver,
        "start_session",
        {"area": area, "date": date_str},
        expect_success=expect_success,
    )
    return form_accepted


def stop_session(driver: webdriver.Chrome) -> None:
    """
    Stop and delete the current session.
    """

    # if a form is open, cancel it
    try:
        driver.find_element(By.LINK_TEXT, "Cancel").click()
    except NoSuchElementException:
        pass

    # stop the session if one is open
    try:
        driver.find_element(By.ID, "stop_session").click()
    except NoSuchElementException:
        pass

    # go to the home page
    driver.get(HOME_URL)
    WebDriverWait(driver, 5).until(EC.title_is(HOME_TITLE))


def get_existing_route(db_session, sector: str, idx: int = 0) -> tuple[str, int]:
    """
    Get the name and ID of a route in the given sector.
    The `idx` parameter can be used to ensure that different routes are used for
    different tests.
    """
    sql_query = text(
        f"""
        SELECT name, id FROM route
        WHERE sector_id = (SELECT id FROM sector WHERE name = '{sector}')
        LIMIT {idx + 1};
        """
    )
    results = db_session.execute(sql_query).fetchall()
    return results[idx]


def fill_form(
    driver: webdriver.Chrome,
    button_id: str,
    field_data: dict,
    expect_success: bool = True,
) -> bool:
    """
    Fill the form with the given data and submit it.

    - Inputs of type checkbox expect a boolean value: if true, the checkbox is clicked,
    regardles of its state. This script also tries to click the label first, and tries
    clicking the actual checkbox if there is no label.

    Args:
        driver: The browser driver.
        button_id: The ID of the button to open the form.
        field_data: The data to be filled in the form. The keys must be the
            IDs of the form fields.
        expect_success: whether the form is expected to be accepted.

    Returns:
        bool: True if the form was accepted.
    """

    # check that we are in the home page and click the button
    if button_id:
        if driver.current_url not in [HOME_URL, HOME_URL + "/"]:
            driver.get(HOME_URL)
            WebDriverWait(driver, 5).until(EC.title_is(HOME_TITLE))
        driver.find_element(By.ID, button_id).click()
        WebDriverWait(driver, 5).until_not(EC.title_is(HOME_TITLE))

    # fill the form
    for field_id, value in field_data.items():
        field = driver.find_element(By.ID, field_id)
        field_type = field.get_attribute("type")
        view_element(driver, field)

        if field_type == "checkbox" and value:
            try:
                label = driver.find_element(By.CSS_SELECTOR, f"label[for='{field_id}']")
                driver.execute_script("arguments[0].click();", label)
            except NoSuchElementException:
                driver.execute_script("arguments[0].click();", field)
        elif field_type == "range":
            driver.execute_script(
                "arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('input'))",
                field,
                value,
            )
        elif field_type == "select-one":
            select_elem = Select(field)
            select_elem.select_by_value(value)
        else:
            field.clear()
            field.send_keys(value)

        # trigger the field's onchange attribute if it has one
        if field.get_attribute("onchange"):
            try:
                driver.execute_script("arguments[0].onchange();", field)
            except Exception as exc:
                print(f"Exception for field with ID {field_id}: {exc}")

    # submit the form
    try:
        element = driver.find_element(By.XPATH, "//input[@type='submit']")
    except NoSuchElementException:
        element = driver.find_element(By.XPATH, "//input[@value='Submit']")
    view_element(driver, element)
    driver.execute_script("arguments[0].click();", element)

    # check if the outcome matches the expectation
    if expect_success:
        WebDriverWait(driver, 10).until(EC.title_is(HOME_TITLE))
    else:
        WebDriverWait(driver, 10).until_not(EC.title_is(HOME_TITLE))

    return expect_success


def view_element(driver: webdriver.Chrome, element):
    """Scrolls the element into view."""
    driver.execute_script("arguments[0].scrollIntoView(true);", element)
    WebDriverWait(driver, 3).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )
    WebDriverWait(driver, 3).until(EC.element_to_be_clickable(element))
