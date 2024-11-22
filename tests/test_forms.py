"""
Tests the forms used to start a session and add climbs to it, while using either existing
areas and routes or creating new ones.

Running the tests together provides more thorough testing, because previous climbs affect
how the form behaves.
"""

from typing import Generator
from time import sleep
from datetime import datetime

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from sqlalchemy import text

from .conftest import HOME_TITLE, HOME_URL, CLIMBER_ID, SLEEP_TIME


EXISTING_OBJECTS = {
    "area": "A1",
    "sector": "A1 S1",
    "session_date": datetime(year=2023, month=1, day=1),
}
NEW_OBJECTS = {
    "area": "A3",
    "sector": "A3 S1",
    "route": "Terranova 2",
    "session_date": datetime(year=2023, month=1, day=2),
}


def get_existing_route(db_session, sector: str) -> tuple[str, int]:
    """
    Get the name and ID of a route in the given sector.
    """
    sql_query = text(
        f"""
        SELECT name, id FROM route
        WHERE sector_id = (SELECT id FROM sector WHERE name = '{sector}')
        LIMIT 1;
        """
    )
    results = db_session.execute(sql_query).fetchall()
    return results[0][0], results[0][1]


@pytest.fixture(scope="module")
def started_session_id(driver, db_session) -> Generator:
    """
    Start a session on an existing area and return its ID. The session will be
    deleted after the test is done.

    `test_create_session_on_existing_area` checks that the session was properly created.
    """

    # create the session
    stop_session(driver, db_session)
    date_obj = NEW_OBJECTS["session_date"]
    print(f"Date (day): {date_obj.day}")
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
    stop_session(driver, db_session)


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
    form_accepted = fill_form(
        driver,
        "start_session",
        {"area": area, "date": date.strftime("%d.%m.%Y") if date else ""},
        expect_success=expect_success,
    )
    return form_accepted


def stop_session(driver: webdriver.Chrome, db_session) -> None:
    """
    Stop and delete the current session.
    """
    try:
        driver.find_element(By.ID, "stop_session").click()
    except NoSuchElementException:
        driver.get(HOME_URL)
    WebDriverWait(driver, 10).until(EC.title_is(HOME_TITLE))


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
    if driver.current_url not in [HOME_URL, HOME_URL + "/"]:
        driver.get(HOME_URL)
        WebDriverWait(driver, 30).until(EC.title_is(HOME_TITLE))

    # open and fill the form
    driver.find_element(By.ID, button_id).click()
    WebDriverWait(driver, 30).until_not(EC.title_is(HOME_TITLE))
    driver.save_screenshot("empty_form.png")
    for field_id, value in field_data.items():
        field = driver.find_element(By.ID, field_id)
        field.clear()
        field.send_keys(value)
        driver.find_element(By.TAG_NAME, "h2").click()

    driver.save_screenshot("filled_form.png")

    # submit the form and check if it was accepted
    driver.find_element(By.XPATH, "//input[@type='submit']").click()
    if expect_success:
        WebDriverWait(driver, 10).until(EC.title_is(HOME_TITLE))
    else:
        WebDriverWait(driver, 10).until_not(EC.title_is(HOME_TITLE))

    return driver.current_url in [HOME_URL, HOME_URL + "/"]


# def test_create_invalid_session(driver) -> None:
#     """
#     Attempt to start an invalid session. A session is invalid if:
#     - the area field is empty
#     - the date field is empty
#     - the combination of climber, date and area already exists
#     """

#     for data in [
#         {"area": "", "date": EXISTING_OBJECTS["session_date"]},
#         {"area": EXISTING_OBJECTS["area"], "date": None},
#         {
#             "area": EXISTING_OBJECTS["area"],
#             "date": EXISTING_OBJECTS["session_date"],
#         },
#     ]:
#         form_accepted = start_session(
#             driver, data["area"], data["date"], expect_success=False
#         )
#         assert not form_accepted


def test_create_session_on_existing_area(db_session, started_session_id) -> None:
    """
    Start a session on an existing area.
    """

    # get the current number of areas in the database
    n_areas_query = text("SELECT COUNT(*) FROM area")
    n_areas_before = db_session.execute(n_areas_query).fetchall()[0][0]

    # check that the session was created
    sql_query = text(
        f"""
        SELECT id FROM climbing_session
        WHERE date = '{NEW_OBJECTS["session_date"].strftime("%Y-%m-%d")}'
        AND climber_id = {CLIMBER_ID}
        AND area_id = (SELECT id FROM area WHERE name = '{EXISTING_OBJECTS["area"]}');
        """
    )
    results = db_session.execute(sql_query).fetchall()
    assert len(results) == 1

    # check that the number of areas in the database did not change
    n_areas_after = db_session.execute(n_areas_query).fetchall()[0][0]
    assert n_areas_after == n_areas_before


# def test_add_climb_of_existing_route(driver, db_session, started_session_id) -> None:
#     """
#     Add a climb of an existing route to a session. Only the route name is required to
#     add a climb. The sector is inferred from the route name, as it already exists in
#     the database.
#     """

#     # get the current number of routes in the database and the route ID
#     route_name, route_id = get_existing_route(db_session, EXISTING_OBJECTS["sector"])
#     n_routes_query = text("SELECT COUNT(*) FROM route")
#     n_routes_before = db_session.execute(n_routes_query).fetchall()[0][0]

#     # fill the form to add a climb of an existing route
#     form_accepted = fill_form(driver, "add_climb", {"name": route_name})
#     assert form_accepted

#     # check that the climb was created
#     sql_query = text(
#         f"""
#         SELECT id FROM climb
#         WHERE session_id = {started_session_id}
#         AND route_id = {route_id};
#         """
#     )
#     results = db_session.execute(sql_query).fetchall()
#     assert len(results) == 1

#     # check that the number of routes in the database did not change
#     n_routes_after = db_session.execute(n_routes_query).fetchall()[0][0]
#     assert n_routes_after == n_routes_before


# def test_add_climb_of_new_route_and_new_sector(
#     driver, db_session, started_session_id
# ) -> None:
#     """
#     Add a climb of a new route to a session.
#     """

#     # get the current number of sectors, routes and climbs in the database
#     tables = ["sector", "route", "climb"]
#     n_before = dict()
#     for table in tables:
#         query = text(f"SELECT COUNT(*) FROM {table}")
#         n_before[table] = db_session.execute(query).fetchall()[0][0]

#     # fill the form to add a climb of a new route
#     sector = NEW_OBJECTS["sector"]
#     route = NEW_OBJECTS["route"]
#     form_accepted = fill_form(
#         driver,
#         "add_climb",
#         {"name": route, "sector": sector},
#     )
#     assert form_accepted

#     # check that the sector, route and climb were created
#     results = db_session.execute(
#         text(f"SELECT id FROM sector WHERE name = '{sector}';")
#     ).fetchall()
#     assert len(results) == 1
#     sector_id = results[0][0]

#     results = db_session.execute(
#         text(
#             f"SELECT id FROM route WHERE name = '{route}' AND sector_id = {sector_id};"
#         )
#     ).fetchall()
#     assert len(results) == 1
#     route_id = results[0][0]

#     results = db_session.execute(
#         text(
#             f"""
#             SELECT id FROM climb
#             WHERE session_id = {started_session_id} AND route_id = {route_id};
#             """
#         )
#     ).fetchall()
#     assert len(results) == 1

#     # check that the number of routes, sectors and climbs increased by 1
#     for table in tables:
#         query = text(f"SELECT COUNT(*) FROM {table}")
#         n_after = db_session.execute(query).fetchall()[0][0]
#         assert n_after == n_before[table] + 1


# def test_add_climb_of_new_route_and_existing_sector(
#     driver, db_session, started_session_id
# ) -> None:
#     """
#     Add a climb of a new route to a session.
#     """

#     # get the current number of sectors, routes and climbs in the database
#     tables = ["sector", "route", "climb"]
#     n_before = dict()
#     for table in tables:
#         query = text(f"SELECT COUNT(*) FROM {table}")
#         n_before[table] = db_session.execute(query).fetchall()[0][0]

#     # fill the form to add a climb of a new route
#     sector = EXISTING_OBJECTS["sector"]
#     route = NEW_OBJECTS["route"] + "1"
#     form_accepted = fill_form(
#         driver,
#         "add_climb",
#         {"name": route, "sector": sector},
#     )
#     assert form_accepted

#     # check that the route and climb were created
#     sector_id = db_session.execute(
#         text(f"SELECT id FROM sector WHERE name = '{sector}';")
#     ).fetchall()[0][0]
#     results = db_session.execute(
#         text(
#             f"SELECT id FROM route WHERE name = '{route}' AND sector_id = {sector_id};"
#         )
#     ).fetchall()
#     assert len(results) == 1
#     route_id = results[0][0]

#     results = db_session.execute(
#         text(
#             f"""
#             SELECT id FROM climb
#             WHERE session_id = {started_session_id} AND route_id = {route_id};
#             """
#         )
#     ).fetchall()
#     assert len(results) == 1

#     # check that the number of routes, sectors and climbs increased by 1
#     for table in tables:
#         query = text(f"SELECT COUNT(*) FROM {table}")
#         n_after = db_session.execute(query).fetchall()[0][0]
#         if table == "sector":
#             assert n_after == n_before[table]
#         else:
#             assert n_after == n_before[table] + 1, table


# def test_create_session_on_new_area(driver, db_session) -> None:
#     """
#     Start a session on a new area.
#     """
#     stop_session(driver, db_session)

#     # get the current number of areas in the database
#     n_areas_query = text("SELECT COUNT(*) FROM area")
#     n_areas_before = db_session.execute(n_areas_query).fetchall()[0][0]

#     # start a session on a new area
#     date = EXISTING_OBJECTS["session_date"]
#     area = NEW_OBJECTS["area"]
#     form_accepted = start_session(driver, area, date)
#     assert form_accepted
#     sleep(SLEEP_TIME)

#     # check that the area and the session were created
#     sql_query = text(f"SELECT id FROM area WHERE name = '{area}'")
#     results = db_session.execute(sql_query).fetchall()
#     assert len(results) == 1
#     area_id = results[0][0]

#     sql_query = text(
#         f"""
#         SELECT id FROM climbing_session
#         WHERE date = '{date.strftime("%Y-%m-%d")}'
#         AND climber_id = {CLIMBER_ID}
#         AND area_id = {area_id};
#         """
#     )
#     results = db_session.execute(sql_query).fetchall()
#     assert len(results) == 1

#     # check that the number of areas in the database increased by 1
#     n_areas_after = db_session.execute(n_areas_query).fetchall()[0][0]
#     assert n_areas_after == n_areas_before + 1
#     stop_session(driver, db_session)
