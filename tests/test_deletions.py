"""
Test that the deletion of objects works as expected. This means that the object is
deleted from the database, as well as any orphaned objects that are no longer make
sense to exist. Also, some objects cannot be deleted because other climbers use them.
"""

from time import sleep

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from sqlalchemy import text

from .conftest import HOME_TITLE, HOME_URL, CLIMBER_ID


SLEEP_TIME = 2


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
    first_row.find_element(By.XPATH, "//a[contains(@href, 'delete_climb')]").click()
    WebDriverWait(driver, 10).until(EC.alert_is_present())
    driver.switch_to.alert.accept()

    # check that the climb is not shown anymore
    sleep(SLEEP_TIME)
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


# def test_delete_route(db_session, driver):
#     """
#     Deleting a route is possible if I am the creator and no one else is using it.
#     Climbs of that route should be deleted as well. And if any session is left empty,
#     it should be deleted too.
#     """
#     # find a route that it not shared
#     sql_query = text(
#         f"""
#         SELECT route.id, route.name
#         FROM route
#         WHERE route.created_by = {CLIMBER_ID}
#         AND route.id NOT IN (
#             SELECT route_id FROM climber_projects WHERE climber_id != {CLIMBER_ID}
#         )
#         AND route.id NOT IN (
#             SELECT climb.route_id
#             FROM climb
#             JOIN climbing_session ON climb.session_id = climbing_session.id
#             WHERE climbing_session.climber_id != {CLIMBER_ID}
#         )
#         LIMIT 1;
#         """
#     )
#     results = db_session.execute(sql_query).fetchall()
#     route_id, route_name = results[0]

#     # go the route's page
#     driver.get(f"{HOME_URL}/route/{route_id}")
#     WebDriverWait(driver, 10).until(EC.title_contains(route_name))

#     # try to delete the route
#     driver.find_element(By.XPATH, "//a[contains(@href, 'delete_route')]").click()
#     WebDriverWait(driver, 10).until(EC.alert_is_present())
#     driver.switch_to.alert.accept()

#     # check that the route, climbs and empty sessions were deleted from the database
#     sleep(SLEEP_TIME)
#     sql_query = text(f"SELECT * FROM route WHERE id = {route_id};")
#     results = db_session.execute(sql_query).fetchall()
#     assert len(results) == 0

#     sql_query = text(f"SELECT * FROM climb WHERE route_id = {route_id};")
#     results = db_session.execute(sql_query).fetchall()
#     assert len(results) == 0

#     sql_query = text(
#         """
#         SELECT climbing_session.id
#         FROM climbing_session
#         LEFT JOIN climb ON climbing_session.id = climb.session_id
#         WHERE climb.id IS NULL;
#         """
#     )
#     results = db_session.execute(sql_query).fetchall()
#     assert len(results) == 0


# def test_delete_shared_route(db_session, driver):
#     """
#     Test that deleting a shared route is not possible. A route is shared if another
#     climber has either climbed it or marked it as a project. Here, we try to delete
#     a route that was created by the current climber but has been climbed by another.
#     """

#     # find a shared route
#     sql_query = text(
#         f"""
#         SELECT route.id, route.name
#         FROM route
#         JOIN climb ON route.id = climb.route_id
#         JOIN climbing_session ON climb.session_id = climbing_session.id
#         WHERE climbing_session.climber_id != {CLIMBER_ID} AND route.created_by = {CLIMBER_ID}
#         LIMIT 1;
#         """
#     )
#     results = db_session.execute(sql_query).fetchall()
#     try_to_delete_route(db_session, driver, *results[0])


# def test_delete_shared_route_project(db_session, driver):
#     """
#     Same as above, but for a route that has been marked as a project by another climber.
#     """

#     # find a shared route
#     sql_query = text(
#         f"""
#         SELECT route.id, route.name
#         FROM route
#         JOIN climber_projects ON route.id = climber_projects.route_id
#         WHERE route.created_by = {CLIMBER_ID}
#         AND climber_projects.climber_id != {CLIMBER_ID}
#         LIMIT 1;
#         """
#     )
#     results = db_session.execute(sql_query).fetchall()
#     try_to_delete_route(db_session, driver, *results[0])


# def try_to_delete_route(db_session, driver, route_id: int, route_name: str):
#     # go the route's page
#     driver.get(f"{HOME_URL}/route/{route_id}")
#     WebDriverWait(driver, 10).until(EC.title_contains(route_name))

#     # try to delete the route
#     driver.find_element(By.XPATH, "//a[contains(@href, 'delete_route')]").click()
#     WebDriverWait(driver, 10).until(EC.alert_is_present())
#     driver.switch_to.alert.accept()

#     # check that the route was not deleted
#     sleep(SLEEP_TIME)
#     driver.refresh()
#     WebDriverWait(driver, 10).until(EC.title_contains(route_name))

#     # check that the route was not deleted from the database
#     sql_query = text(f"SELECT * FROM route WHERE id = {route_id};")
#     results = db_session.execute(sql_query).fetchall()
#     assert len(results) == 1


# def test_delete_session(db_session, driver):
#     """
#     Deleting my own session is always possible and cascades to all climbs in that session.
#     """

#     # find a shared session
#     sql_query = text(
#         f"""
#         SELECT climbing_session.id, climbing_session.date
#         FROM climbing_session
#         WHERE climbing_session.climber_id = {CLIMBER_ID}
#         LIMIT 1;
#         """
#     )
#     results = db_session.execute(sql_query).fetchall()

#     # go to the session's page
#     session_id, session_date = results[0]
#     driver.get(f"{HOME_URL}/session/{session_id}")
#     WebDriverWait(driver, 10).until(EC.title_contains("Session"))

#     # delete the session
#     card = driver.find_elements(By.CLASS_NAME, "card")[0]
#     card.find_element(By.XPATH, "//a[contains(@href, 'delete')]").click()
#     WebDriverWait(driver, 10).until(EC.alert_is_present())
#     driver.switch_to.alert.accept()

#     # check that the session and its climbs were deleted from the database
#     sleep(SLEEP_TIME)
#     sql_query = text(f"SELECT * FROM climbing_session WHERE id = {session_id};")
#     results = db_session.execute(sql_query).fetchall()
#     assert len(results) == 0

#     sql_query = text(f"SELECT * FROM climb WHERE session_id = {session_id};")
#     results = db_session.execute(sql_query).fetchall()
#     assert len(results) == 0


# def test_delete_opinion(db_session, driver):
#     """
#     Deleting an opinion is always possible and does not cascade to other objects.
#     """

#     # find a route with an opinion
#     sql_query = text(
#         f"""
#         SELECT opinion.id, route.id, route.name
#         FROM opinion
#         JOIN route ON opinion.route_id = route.id
#         WHERE opinion.climber_id = {CLIMBER_ID}
#         LIMIT 1;
#         """
#     )
#     results = db_session.execute(sql_query).fetchall()
#     opinion_id, route_id, route_name = results[0]

#     # go to the route's page
#     driver.get(f"{HOME_URL}/route/{route_id}")
#     WebDriverWait(driver, 10).until(EC.title_contains(route_name))

#     # delete the opinion
#     driver.find_element(By.XPATH, "//a[contains(@href, 'delete_opinion')]").click()
#     WebDriverWait(driver, 10).until(EC.alert_is_present())
#     driver.switch_to.alert.accept()

#     # check that the opinion is no longer displayed
#     sleep(SLEEP_TIME)
#     driver.refresh()
#     WebDriverWait(driver, 10).until(EC.title_contains(route_name))
#     try:
#         driver.find_element(By.XPATH, "//a[contains(@href, 'delete_opinion')]")
#     except NoSuchElementException:
#         pass

#     # check that the opinion was deleted from the database
#     sql_query = text(f"SELECT * FROM opinion WHERE id = {opinion_id};")
#     results = db_session.execute(sql_query).fetchall()
#     assert len(results) == 0


# def test_others_objects(db_session, driver):
#     """
#     Deleting the objects created by another climber is never possible.
#     """

#     def try_to_delete_others_object(sql_query: str, object: str):
#         object_id = db_session.execute(sql_query).fetchall()[0][0]
#         driver.get(f"{HOME_URL}/delete_{object.split('_')[-1]}/{object_id}")
#         sleep(SLEEP_TIME)
#         sql_query = text(f"SELECT * FROM {object} WHERE id = {object_id};")
#         results = db_session.execute(sql_query).fetchall()
#         assert len(results) == 1, f"Object {object} was deleted"

#     # find an object that was not created by me
#     for object, creator in {
#         "route": "created_by",
#         "climbing_session": "climber_id",
#         "opinion": "climber_id",
#     }.items():
#         sql_query = text(
#             f"""
#             SELECT {object}.id
#             FROM {object}
#             WHERE {object}.{creator} != {CLIMBER_ID}
#             LIMIT 1;
#             """
#         )
#         try_to_delete_others_object(sql_query, object)

#     # check that I cannot delete a climb of another climber
#     sql_query = text(
#         f"""
#         SELECT climb.id
#         FROM climb
#         JOIN climbing_session ON climb.session_id = climbing_session.id
#         WHERE climbing_session.climber_id != {CLIMBER_ID}
#         LIMIT 1;
#         """
#     )
#     try_to_delete_others_object(sql_query, "climb")
