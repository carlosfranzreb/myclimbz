"""
Test that the deletion of objects works as expected. This means that the object is
deleted from the database, as well as any orphaned objects that are no longer make
sense to exist. Also, some objects cannot be deleted because other climbers use them.
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

from .conftest import HOME_TITLE, HOME_URL, CLIMBER_ID


def test_delete_climb(db_session, driver):
    """
    Deleting a climb is always possible and does not cascade to other objects.
    """

    # click on the first row of the table with ID `content_table`
    driver.get(HOME_URL)
    WebDriverWait(driver, 10).until(EC.title_is(HOME_TITLE))

    table = driver.find_element(By.ID, "content_table")
    first_row = table.find_elements(By.TAG_NAME, "tr")[1]
    route_name = first_row.find_elements(By.TAG_NAME, "td")[0].text
    first_row.click()
    WebDriverWait(driver, 10).until(EC.title_contains(route_name))

    # click on the delete button of the first climb
    table = driver.find_element(By.ID, "content_table")
    first_row = table.find_elements(By.TAG_NAME, "tr")[1]
    climb_date = first_row.find_elements(By.TAG_NAME, "td")[0].text
    first_row.find_element(By.XPATH, "//a[contains(@href, 'delete')]").click()
    WebDriverWait(driver, 10).until(EC.alert_is_present())
    driver.switch_to.alert.accept()

    # check that the climb is not shown anymore
    sleep(1)
    driver.refresh()
    try:
        table = driver.find_element(By.ID, "content_table")
        first_row = table.find_elements(By.TAG_NAME, "tr")[1]
        new_date = first_row.find_elements(By.TAG_NAME, "td")[0].text
        assert new_date != climb_date
    except NoSuchElementException:
        pass

    # check that the climb was deleted from the database
    sql_query = text(
        f"""
        SELECT climb.id
        FROM climb
        JOIN route ON climb.route_id = route.id
        JOIN climbing_session ON climb.session_id = climbing_session.id
        WHERE route.name = '{route_name}'
        AND climbing_session.date = '{climb_date}'
        AND climbing_session.climber_id = {CLIMBER_ID};
        """
    )
    results = db_session.execute(sql_query).fetchall()
    assert len(results) == 0


def test_delete_shared_route(db_session, driver):
    """
    Test that deleting a shared route is not possible. A route is shared if another
    climber has either climbed it or marked it as a project.
    """

    # find a shared route
    sql_query = text(
        f"""
        SELECT route.id, route.name
        FROM route
        JOIN climb ON route.id = climb.route_id
        JOIN climbing_session ON climb.session_id = climbing_session.id
        WHERE climbing_session.climber_id != {CLIMBER_ID} AND route.created_by = {CLIMBER_ID}
        LIMIT 1;
        """
    )
    results = db_session.execute(sql_query).fetchall()
    assert len(results) == 1

    # go the route's page
    route_id, route_name = results[0]
    driver.get(f"{HOME_URL}/route/{route_id}")
    WebDriverWait(driver, 10).until(EC.title_contains(route_name))

    # try to delete the route
    card = driver.find_elements(By.CLASS_NAME, "card")[0]
    card.find_element(By.XPATH, "//a[contains(@href, 'delete')]").click()
    WebDriverWait(driver, 10).until(EC.alert_is_present())
    driver.switch_to.alert.accept()

    # check that the route was not deleted
    sleep(1)
    driver.refresh()
    WebDriverWait(driver, 10).until(EC.title_contains(route_name))
