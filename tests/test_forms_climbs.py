"""
Tests the forms used to start a session and add climbs to it, while using either existing
areas and routes or creating new ones.

Running the tests together provides more thorough testing, because previous climbs affect
how the form behaves.
"""

from sqlalchemy import text

from .conftest import CLIMBER_ID, NEW_OBJECTS, EXISTING_OBJECTS
from .form_utils import get_existing_route, fill_form, started_session_id


def test_add_climb_of_existing_route(driver, db_session, started_session_id):
    """
    Add a climb of an existing route to a session. Only the route name is required to
    add a climb.
    - The sector is inferred from the route name, as it already exists in the database.
    - The number of attempts is 1 by default, so the climb is created.
    - The opinion should be added with grade and comment null and the sliders in their
        default position because the user did not click on "skip opinion".
    """

    # get the current number of routes in the database and the route ID
    route_name, route_id = get_existing_route(db_session, EXISTING_OBJECTS["sector"])
    n_routes_query = text("SELECT COUNT(*) FROM route")
    n_routes_before = db_session.execute(n_routes_query).fetchall()[0][0]

    # fill the form to add a climb of an existing route
    form_accepted = fill_form(driver, "add_climb", {"name": route_name})
    assert form_accepted

    # check that the climb was created
    sql_query = text(
        f"""
        SELECT id FROM climb
        WHERE session_id = {started_session_id}
        AND route_id = {route_id};
        """
    )
    results = db_session.execute(sql_query).fetchall()
    assert len(results) == 1

    # check that the number of routes in the database did not change
    n_routes_after = db_session.execute(n_routes_query).fetchall()[0][0]
    assert n_routes_after == n_routes_before

    # check that an opinion for the route was created
    sql_query = text(
        f"""
        SELECT grade_id,comment,landing,rating FROM opinion
        WHERE climber_id = {CLIMBER_ID}
        AND route_id = {route_id};
        """
    )
    results = db_session.execute(sql_query).fetchall()
    assert len(results) == 1
    grade_id, comment, landing, rating = results[0]
    assert grade_id is None
    assert comment is None
    assert landing == 3
    assert rating == 3


def test_add_climb_of_new_route_and_new_sector(driver, db_session, started_session_id):
    """
    Add a climb of a new route to a session.

    - The new routes and sectors should be created.
    - A climb should not be created because the route is added as a project.
    - An opinion should not be created because the user wants to skip it.
    """

    # get the current number of sectors, routes and climbs in the database
    tables = ["sector", "route", "climb", "opinion", "crux_opinions"]
    n_before = dict()
    for table in tables:
        query = text(f"SELECT COUNT(*) FROM {table}")
        n_before[table] = db_session.execute(query).fetchall()[0][0]

    # fill the form to add a new route
    sector = NEW_OBJECTS["sector"]
    route = NEW_OBJECTS["route"]
    form_accepted = fill_form(
        driver,
        "add_climb",
        {"name": route, "sector": sector, "is_project": True, "skip_opinion": True},
    )
    assert form_accepted

    # check that the sector and route were created
    results = db_session.execute(
        text(f"SELECT id FROM sector WHERE name = '{sector}';")
    ).fetchall()
    assert len(results) == 1
    sector_id = results[0][0]

    results = db_session.execute(
        text(
            f"SELECT id FROM route WHERE name = '{route}' AND sector_id = {sector_id};"
        )
    ).fetchall()
    assert len(results) == 1
    route_id = results[0][0]

    # check that a climb was not created
    results = db_session.execute(
        text(
            f"""
            SELECT id FROM climb
            WHERE session_id = {started_session_id} AND route_id = {route_id};
            """
        )
    ).fetchall()
    assert len(results) == 0

    # check that an opinion was not created
    results = db_session.execute(
        text(
            f"""
            SELECT id FROM opinion
            WHERE climber_id = {CLIMBER_ID} AND route_id = {route_id};
            """
        )
    ).fetchall()
    assert len(results) == 0

    # check that the number of rows in the tables are correct
    for table in tables:
        query = text(f"SELECT COUNT(*) FROM {table}")
        n_after = db_session.execute(query).fetchall()[0][0]
        if table in ["climb", "opinion", "crux_opinions"]:
            assert n_after == n_before[table], table
        else:
            assert n_after == n_before[table] + 1, table


def test_add_climb_of_new_route_and_existing_sector(
    driver, db_session, started_session_id
):
    """
    Add a climb of a new route in an existing sector to a session.

    - The route's height and inclination should be set to 3m and 0°.
    - The climb is set to "sent" in 5 attempts.
    - The opinion is set to "grade": 7A, "rating": 5, "landing": 2 and cruxes
        "Coordination".

    After this first test, we add a climb on the same route again. When the
    route name is input, the climb and opinion forms should be filled with the
    existing values for that route in the sesssion.

    - The climb was set to "sent" in 5 attempts in the previous function. We append
    a 7 to the number of attempts, which should now be 57.
    - The opinion is set to "grade": 7A, "rating": 5, "landing": 2 and cruxes
        "Coordination". We add the crux "Mantel".
    """

    # get the current number of sectors, routes and climbs in the database
    tables = ["sector", "route", "climb", "opinion", "crux_opinions"]
    n_before = dict()
    for table in tables:
        query = text(f"SELECT COUNT(*) FROM {table}")
        n_before[table] = db_session.execute(query).fetchall()[0][0]

    # fill the form to add a climb of a new route
    sector = EXISTING_OBJECTS["sector"]
    route = NEW_OBJECTS["route"] + "1"
    form_accepted = fill_form(
        driver,
        "add_climb",
        {
            "name": route,
            "sector": sector,
            "height": 4.0,
            "inclination": 25,
            "n_attempts": 5,
            "sent": True,
            "grade": "13",
            "rating": 5,
            "landing": 2,
            "cruxes-2": True,
        },
    )
    assert form_accepted

    # check that the route was created
    sector_id = db_session.execute(
        text(f"SELECT id FROM sector WHERE name = '{sector}';")
    ).fetchall()[0][0]
    results = db_session.execute(
        text(
            f"SELECT id, height, inclination FROM route WHERE name = '{route}' AND sector_id = {sector_id};"
        )
    ).fetchall()
    assert len(results) == 1
    route_id, height, inclination = results[0]
    assert height == 4.0
    assert inclination == 25

    # check that the climb was created
    results = db_session.execute(
        text(
            f"""
            SELECT n_attempts, sent
            FROM climb
            WHERE session_id = {started_session_id} AND route_id = {route_id};
            """
        )
    ).fetchall()
    assert len(results) == 1
    n_attempts, sent = results[0]
    assert n_attempts == 5
    assert sent

    # check that the opinion was created
    results = db_session.execute(
        text(
            f"""
            SELECT id,grade_id,rating,landing
            FROM opinion
            WHERE climber_id = {CLIMBER_ID} AND route_id = {route_id};
            """
        )
    ).fetchall()
    assert len(results) == 1
    opinion_id, grade_id, rating, landing = results[0]
    assert grade_id == 13
    assert rating == 5
    assert landing == 2

    # check that the crux was created
    results = db_session.execute(
        text(
            f"""
            SELECT crux_id
            FROM crux_opinions
            WHERE opinion_id = {opinion_id};
            """
        )
    ).fetchall()
    assert len(results) == 1
    assert results[0][0] == 23  # ID of crux "Coordination"

    # check that the number of rows in the tables are correct
    for table in tables:
        query = text(f"SELECT COUNT(*) FROM {table}")
        n_after = db_session.execute(query).fetchall()[0][0]
        if table == "sector":
            assert n_after == n_before[table]
        else:
            assert n_after == n_before[table] + 1, table

    # fill the form to add a climb of the same route (i.e. update it)
    form_accepted = fill_form(
        driver,
        "add_climb",
        {
            "name": route,
            "n_attempts": 7,
            "cruxes-14": True,
        },
    )
    assert form_accepted

    # check that the climb was updated
    results = db_session.execute(
        text(
            f"""
            SELECT n_attempts, sent 
            FROM climb
            WHERE session_id = {started_session_id} AND route_id = {route_id};
            """
        )
    ).fetchall()
    assert len(results) == 1
    n_attempts, sent = results[0]
    assert n_attempts == 57
    assert sent

    # check that the opinion has not changed
    results = db_session.execute(
        text(
            f"""
            SELECT id,grade_id,rating,landing
            FROM opinion
            WHERE climber_id = {CLIMBER_ID} AND route_id = {route_id};
            """
        )
    ).fetchall()
    assert len(results) == 1
    opinion_id, grade_id, rating, landing = results[0]
    assert grade_id == 13
    assert rating == 5
    assert landing == 2

    # check that the new crux was created
    results = db_session.execute(
        text(
            f"""
            SELECT crux_id
            FROM crux_opinions
            WHERE opinion_id = {opinion_id};
            """
        )
    ).fetchall()
    assert len(results) == 2
    assert results[0][0] == 23  # ID of crux "Coordination"
    assert results[1][0] == 18  # ID of crux "Mantel"

    # check that the number of rows in the tables are correct
    for table in tables:
        query = text(f"SELECT COUNT(*) FROM {table}")
        n_after = db_session.execute(query).fetchall()[0][0]
        if table == "sector":
            assert n_after == n_before[table]
        elif table == "crux_opinions":
            assert n_after == n_before[table] + 2
        else:
            assert n_after == n_before[table] + 1, table
