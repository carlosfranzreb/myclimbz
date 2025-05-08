"""
Tests the forms used to create sessions, in either existing areas or creating new ones.
"""

from time import sleep
from datetime import datetime

from sqlalchemy import text
from selenium.webdriver.common.by import By

from .conftest import CLIMBER_ID, SLEEP_TIME, start_session, stop_session


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


def test_create_invalid_session(driver) -> None:
    """
    Attempt to start an invalid session. A session is invalid if:
    - the area field is empty
    - the date field is empty
    - the combination of climber, date and area already exists
    """

    for data in [
        {"area": "", "date": EXISTING_OBJECTS["session_date"]},
        {"area": EXISTING_OBJECTS["area"], "date": None},
        {
            "area": EXISTING_OBJECTS["area"],
            "date": EXISTING_OBJECTS["session_date"],
        },
    ]:
        try:
            form_accepted = start_session(
                driver, data["area"], data["date"], expect_success=False
            )
        except Exception as e:
            print(e)
            form_accepted = True
        assert not form_accepted, data

    # cancel form
    driver.find_element(By.LINK_TEXT, "Cancel").click()


def test_create_session_on_new_area(driver, db_session) -> None:
    """
    Start a session on a new area.
    """

    # get the current number of areas in the database
    n_areas_query = text("SELECT COUNT(*) FROM area")
    n_areas_before = db_session.execute(n_areas_query).fetchall()[0][0]

    # start a session on a new area
    date = EXISTING_OBJECTS["session_date"]
    area = NEW_OBJECTS["area"]
    form_accepted = start_session(driver, area, date)
    assert form_accepted
    sleep(SLEEP_TIME)

    # check that the area and the session were created
    sql_query = text(f"SELECT id FROM area WHERE name = '{area}'")
    results = db_session.execute(sql_query).fetchall()
    assert len(results) == 1
    area_id = results[0][0]

    sql_query = text(
        f"""
        SELECT id FROM climbing_session
        WHERE date = '{date.strftime("%Y-%m-%d")}'
        AND climber_id = {CLIMBER_ID}
        AND area_id = {area_id};
        """
    )
    results = db_session.execute(sql_query).fetchall()
    assert len(results) == 1

    # check that the number of areas in the database increased by 1
    n_areas_after = db_session.execute(n_areas_query).fetchall()[0][0]
    assert n_areas_after == n_areas_before + 1
    stop_session(driver)


def test_create_session_on_existing_area(db_session, started_session_id) -> None:
    """
    Start a session on an existing area.
    """

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
    # i.e. 2 if this test is run alone, 3 if the previous test is run before
    n_areas_after = db_session.execute(text("SELECT COUNT(*) FROM area")).fetchall()[0][
        0
    ]
    assert n_areas_after in [2, 3]
