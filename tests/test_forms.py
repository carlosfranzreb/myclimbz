"""
Tests the forms used to start a session and add climbs to it, while using either existing
areas and routes or creating new ones.
"""

import json
from time import sleep
from collections import Counter
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sqlalchemy import text

from .conftest import HOME_TITLE


CLIMBER_ID = 1
EXISTING_OBJECTS = {
    "area": "A1",
    "sector": "A1_S1",
    "route": "Terranova",
    "session_date": datetime(2023, 1, 1),
}
NEW_OBJECTS = {
    "area": "A3",
    "sector": "A3_S1",
    "route": "Terranova 2",
    "session_date": datetime(2023, 1, 2),
}


def fill_form(
    driver: webdriver.Chrome,
    button_id: str,
    field_data: dict,
    expect_success: bool = True,
) -> bool:
    """
    Fill the form with the given data and submit it.

    Args:
        driver: The browser driver.
        button_id: The ID of the button to open the form.
        field_data: The data to be filled in the form. The keys must be the
            IDs of the form fields.
        expect_success: whether the form is expected to be accepted.

    Returns:
        bool: True if the form was accepted.
    """

    # check that we are in the home page
    home_url = "http://127.0.0.1:5000"
    if driver.current_url not in [home_url, home_url + "/"]:
        driver.get(home_url)
        WebDriverWait(driver, 30).until(EC.title_is(HOME_TITLE))

    # open and fill the form
    driver.find_element(By.ID, button_id).click()
    WebDriverWait(driver, 30).until_not(EC.title_is(HOME_TITLE))
    for field_id, value in field_data.items():
        field = driver.find_element(By.ID, field_id)
        field.clear()
        field.send_keys(value)

    # submit the form and check if it was accepted
    driver.find_element(By.XPATH, "//input[@type='submit']").click()
    if expect_success:
        WebDriverWait(driver, 10).until(EC.title_is(HOME_TITLE))
    else:
        WebDriverWait(driver, 10).until_not(EC.title_is(HOME_TITLE))

    return driver.current_url in [home_url, home_url + "/"]


def test_create_invalid_session(driver) -> None:
    """
    Attempt to start an invalid session. A session is invalid if:
    - the area field is empty
    - the date field is empty
    - the combination of climber, date and area already exists
    """

    data_dicts = [
        {"area": "", "date": EXISTING_OBJECTS["session_date"].strftime("%d.%m.%Y")},
        {"area": EXISTING_OBJECTS["area"], "date": ""},
        {
            "area": EXISTING_OBJECTS["area"],
            "date": EXISTING_OBJECTS["session_date"].strftime("%d.%m.%Y"),
        },
    ]

    for data in data_dicts:
        form_accepted = fill_form(driver, "start_session", data, expect_success=False)
        assert not form_accepted


def test_create_session_on_existing_area(driver, db_session) -> None:
    """
    Start a session on an existing area.
    """

    # get the current number of areas in the database
    n_areas_query = text("SELECT COUNT(*) FROM area")
    n_areas_before = db_session.execute(n_areas_query).fetchall()[0][0]

    date = NEW_OBJECTS["session_date"].strftime("%d.%m.%Y")
    area = EXISTING_OBJECTS["area"]

    # fill the form to start a session on an existing area
    form_accepted = fill_form(driver, "start_session", {"area": area, "date": date})
    assert form_accepted
    sleep(2)

    # check that the session was created
    sql_query = text(
        f"""
        SELECT * FROM climbing_session
        WHERE date = '{NEW_OBJECTS["session_date"].strftime("%Y-%m-%d")}'
        AND climber_id = {CLIMBER_ID}
        AND area_id = (SELECT id FROM area WHERE name = '{area}');
        """
    )
    results = db_session.execute(sql_query).fetchall()
    assert len(results) == 1

    # check that the number of areas in the database did not change
    n_areas_after = db_session.execute(n_areas_query).fetchall()[0][0]
    assert n_areas_after == n_areas_before
