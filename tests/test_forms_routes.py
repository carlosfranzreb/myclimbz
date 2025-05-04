"""
Tests the forms used to start a session and add climbs to it, while using either existing
areas and routes or creating new ones.

Running the tests together provides more thorough testing, because previous climbs affect
how the form behaves.
"""

from datetime import datetime

from sqlalchemy import text

from .form_utils import get_existing_route, fill_form, started_session_id


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


def test_add_climb_of_existing_route(driver, db_session, started_session_id) -> None:
    """
    Add a climb of an existing route to a session. Only the route name is required to
    add a climb.
    - The sector is inferred from the route name, as it already exists in the database.
    - The number of attempts is 1 by default.
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


def test_add_climb_of_new_route_and_new_sector(
    driver, db_session, started_session_id
) -> None:
    """
    Add a climb of a new route to a session.
    """

    # get the current number of sectors, routes and climbs in the database
    tables = ["sector", "route", "climb"]
    n_before = dict()
    for table in tables:
        query = text(f"SELECT COUNT(*) FROM {table}")
        n_before[table] = db_session.execute(query).fetchall()[0][0]

    # fill the form to add a climb of a new route
    sector = NEW_OBJECTS["sector"]
    route = NEW_OBJECTS["route"]
    form_accepted = fill_form(
        driver,
        "add_climb",
        {"name": route, "sector": sector},
    )
    assert form_accepted

    # check that the sector, route and climb were created
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

    results = db_session.execute(
        text(
            f"""
            SELECT id FROM climb
            WHERE session_id = {started_session_id} AND route_id = {route_id};
            """
        )
    ).fetchall()
    assert len(results) == 1

    # check that the number of routes, sectors and climbs increased by 1
    for table in tables:
        query = text(f"SELECT COUNT(*) FROM {table}")
        n_after = db_session.execute(query).fetchall()[0][0]
        assert n_after == n_before[table] + 1


def test_add_climb_of_new_route_and_existing_sector(
    driver, db_session, started_session_id
) -> None:
    """
    Add a climb of a new route to a session.
    """

    # get the current number of sectors, routes and climbs in the database
    tables = ["sector", "route", "climb"]
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
        {"name": route, "sector": sector},
    )
    assert form_accepted

    # check that the route and climb were created
    sector_id = db_session.execute(
        text(f"SELECT id FROM sector WHERE name = '{sector}';")
    ).fetchall()[0][0]
    results = db_session.execute(
        text(
            f"SELECT id FROM route WHERE name = '{route}' AND sector_id = {sector_id};"
        )
    ).fetchall()
    assert len(results) == 1
    route_id = results[0][0]

    results = db_session.execute(
        text(
            f"""
            SELECT id FROM climb
            WHERE session_id = {started_session_id} AND route_id = {route_id};
            """
        )
    ).fetchall()
    assert len(results) == 1

    # check that the number of routes, sectors and climbs increased by 1
    for table in tables:
        query = text(f"SELECT COUNT(*) FROM {table}")
        n_after = db_session.execute(query).fetchall()[0][0]
        if table == "sector":
            assert n_after == n_before[table]
        else:
            assert n_after == n_before[table] + 1, table
