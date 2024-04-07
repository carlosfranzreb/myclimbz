"""
Tests the analysis page. The steps performed when plotting data are defined in the
docstring of the plot_data() function in `main.js`. Given that the x- and y-axes are
processed independently, we don't need to test all possible combinations of axes. We
therefore test all possible y-axes for the x-axis "Area", and then all possible x-axes
for the y-axis "# of climbs".

Useful commands when implementing tests:

- Command to run these tests: pytest --driver -s tests/test_analysis.py
- Command to see open ports: lsof -i -P | grep -i "listen"
- Command to kill process on port: kill $(lsof -t -i:5000)
"""

from time import sleep
from collections import Counter

from datetime import datetime

import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from sqlalchemy import text


def test_request():
    response = requests.get("http://localhost:5000")
    assert response.status_code == 200


def get_plotted_data(
    driver: webdriver.Chrome,
    x_axis: str,
    y_axis: str,
    grade_scale: str = "font",
) -> list:
    """
    Returns the plotted data for the given x- and y-axes.

    Args:
        x_axis: the x-axis value
        y_axis: the y-axis value
        toggle_grade_scale: whether to toggle the scale switch, i.e. change to V-scale

    Returns:
        the plotted data as a list of tuples, where each tuple is of the form
        (key, value).
    """

    # toggle to show plot
    btn = driver.find_element(By.XPATH, "//input[@id='display-form-toggle']")
    if not btn.is_selected():
        btn.find_element(By.XPATH, "..").click()

    if grade_scale == "hueco":
        grade_btn = driver.find_element(By.XPATH, "//input[@id='grade-scale-toggle']")
        grade_btn.find_element(By.XPATH, "..").click()

    x_axis_select = driver.find_element(By.XPATH, "//select[@id='x-axis-select']")
    x_axis_select.click()
    x_axis_select.find_element(By.XPATH, f"//option[. = '{x_axis}']").click()

    y_axis_select = driver.find_element(By.XPATH, "//select[@id='y-axis-select']")
    y_axis_select.click()
    y_axis_select.find_element(By.XPATH, f"//option[. = '{y_axis}']").click()

    # get the content of the PLOTTED_DATA global variable of JavaScript
    plotted_data = dict()
    while len(plotted_data) == 0:
        sleep(0.5)
        plotted_data = driver.execute_script("return Array.from(PLOTTED_DATA);")

    # set the grade scale back to "font" if it was changed
    if grade_scale == "hueco":
        grade_btn.find_element(By.XPATH, "..").click()

    return plotted_data


def test_climbs_per_area(driver, db_session) -> None:
    """
    Ensures that the correct data is plotted for the 'Climbs per Area' and 'Success
    rate per Area' graphs. The areas are sorted alphabetically by name. Check also
    the 'Climbs per Area' numbers when the "Include unsent boulders" checkbox is
    checked.
    """

    sql_query = text(
        """
        SELECT area.name, route.id, climb.sent
        FROM area 
        JOIN sector ON area.id = sector.area_id 
        JOIN route ON sector.id = route.sector_id 
        JOIN climb ON route.id = climb.route_id AND climb.climber_id = :climber_id
        """
    )
    results = db_session.execute(sql_query, {"climber_id": 1}).fetchall()

    unique_areas = set(result[0] for result in results)
    area_data = {area: list() for area in unique_areas}
    for area in unique_areas:
        n_routes = len(set(result[1] for result in results if result[0] == area))
        n_sent_routes = len(
            set(result[1] for result in results if result[0] == area and result[2])
        )

        area_data[area] = {
            "n_routes": n_routes,
            "n_sent_routes": n_sent_routes,
            "success_rate": n_sent_routes / n_routes if n_routes > 0 else 0,
        }

    plotted_data = get_plotted_data(driver, "Area", "Climbs: total sent")
    assert len(plotted_data) == len(area_data)
    for area, n_sent_routes_plotted in plotted_data:
        assert n_sent_routes_plotted == area_data[area]["n_sent_routes"]
    area_names = [area for area, _ in plotted_data]
    assert [area for area, _ in plotted_data] == sorted(area_names)

    plotted_data = get_plotted_data(driver, "Area", "Climbs: total tried")
    assert len(plotted_data) == len(area_data)
    for area, n_routes_plotted in plotted_data:
        assert n_routes_plotted == area_data[area]["n_routes"]

    plotted_data = get_plotted_data(driver, "Area", "Climbs: success rate")
    assert len(plotted_data) == len(area_data)
    for area, success_rate_plotted in plotted_data:
        assert success_rate_plotted == area_data[area]["success_rate"]


def test_attempts_per_area(driver, db_session) -> None:
    """
    Ensures that the correct data is plotted for all four 'Attempts per Area' graphs: with
    total, avg. min. and max. values. Here we want to know how many attempts it took to send
    a route. Routes that have not been sent are not included in the graph.
    """
    sql_query = text(
        """
        SELECT 
            area.name,
            route.id,
            climb.id,
            climb.n_attempts,
            climb.sent,
            session.date
        FROM area 
        JOIN sector ON area.id = sector.area_id 
        JOIN route ON sector.id = route.sector_id 
        LEFT JOIN climb ON route.id = climb.route_id AND climb.climber_id = :climber_id
        LEFT JOIN session ON climb.session_id = session.id
        WHERE climb.id IS NOT NULL
        """
    )
    results = db_session.execute(sql_query, {"climber_id": 1}).fetchall()

    unique_areas = set(result[0] for result in results)
    area_data = {area: list() for area in unique_areas}

    for area_name in unique_areas:
        for route_id in set(result[1] for result in results if result[0] == area_name):
            area_data[area_name].append(0)
            climbs = [result for result in results if result[1] == route_id]

            # get the earliest date at which the route was sent
            min_send_date = datetime.max
            for climb in climbs:
                date = datetime.strptime(climb[5], "%Y-%m-%d")
                if climb[4] and date < min_send_date:
                    min_send_date = date

            # add the attempts of the climbs that took place before the route was sent (incl.)
            for climb in climbs:
                date = datetime.strptime(climb[5], "%Y-%m-%d")
                if date <= min_send_date:
                    area_data[area_name][-1] += climb[3]

    plotted_data = get_plotted_data(driver, "Area", "Attempts: total")
    assert len(plotted_data) == len(area_data)
    for area, n_sent_routes_plotted in plotted_data:
        assert n_sent_routes_plotted == sum(area_data[area])

    plotted_data = get_plotted_data(driver, "Area", "Attempts: avg.")
    assert len(plotted_data) == len(area_data)
    for area, avg_attempts_plotted in plotted_data:
        assert avg_attempts_plotted == sum(area_data[area]) / len(area_data[area])

    plotted_data = get_plotted_data(driver, "Area", "Attempts: min.")
    assert len(plotted_data) == len(area_data)
    for area, min_attempts_plotted in plotted_data:
        assert min_attempts_plotted == min(area_data[area])

    plotted_data = get_plotted_data(driver, "Area", "Attempts: max.")
    assert len(plotted_data) == len(area_data)
    for area, max_attempts_plotted in plotted_data:
        assert max_attempts_plotted == max(area_data[area])


def test_grade_per_area(driver, db_session) -> None:
    """
    Ensures that the correct data is plotted for the 'Avg. Grade per Area' and
    'Max. Grade per Area' graphs.
    """

    sql_query = text(
        """
        SELECT area.name, grade.level
        FROM area 
        JOIN sector ON area.id = sector.area_id 
        JOIN route ON sector.id = route.sector_id 
        JOIN opinion ON opinion.route_id = route.id
        JOIN grade ON opinion.grade_id = grade.id
        WHERE opinion.grade_id NOT NULL AND opinion.climber_id=:climber_id
        """
    )
    results = db_session.execute(sql_query, {"climber_id": 1}).fetchall()

    unique_areas = set(result[0] for result in results)
    area_data = {area: list() for area in unique_areas}
    for result in results:
        area_data[result[0]].append(result[1])

    area_grades_avg, area_grades_max = dict(), dict()
    for area in area_data:
        area_grades_avg[area] = sum(area_data[area]) / len(area_data[area])
        area_grades_max[area] = max(area_data[area])

    plotted_data = get_plotted_data(driver, "Area", "Grade: avg.")
    assert len(plotted_data) == len(area_data)
    for area, avg_grade_plotted in plotted_data:
        assert avg_grade_plotted == area_grades_avg[area]

    plotted_data = get_plotted_data(driver, "Area", "Grade: max.")
    assert len(plotted_data) == len(area_data)
    for area, max_grade_plotted in plotted_data:
        assert max_grade_plotted == area_grades_max[area]


def test_climbs_per_sector(driver, db_session) -> None:
    """
    Ensures that the correct data is plotted for the 'Climbs per Sector' graph. The
    sectors are sorted alphabetically by name.
    """
    sql_query = text(
        """
        SELECT sector.name, route.id, climb.sent
        FROM sector 
        JOIN route ON sector.id = route.sector_id 
        JOIN climb ON route.id = climb.route_id AND climb.climber_id = :climber_id
        """
    )
    results = db_session.execute(sql_query, {"climber_id": 1}).fetchall()

    unique_sectors = set(result[0] for result in results)
    sector_data = dict()
    for sector in unique_sectors:
        n_routes = len(set(result[1] for result in results if result[0] == sector))
        sector_data[sector] = n_routes

    plotted_data = get_plotted_data(driver, "Sector", "Climbs: total tried")
    assert len(plotted_data) == len(sector_data)
    for sector, n_sent_routes_plotted in plotted_data:
        assert n_sent_routes_plotted == sector_data[sector]

    sector_names = [sector for sector, _ in plotted_data]
    assert [sector for sector, _ in plotted_data] == sorted(sector_names)


def test_climbs_per_grade(driver, db_session):
    """
    Ensures that the correct data is plotted for the 'Climbs per Grade' graph. The
    grades are sorted by level. The number of columns in the graph is equal to the
    number of grades between the lowest and highest level that have climbs, inclusive.
    Check also the 'Climbs per Grade' numbers when the "Grade scale" switch is toggled,
    i.e. change to V-scale,
    """

    for grade_scale in ["font", "hueco"]:
        sql_query = text(
            f"""
            SELECT grade.{grade_scale}, COUNT(opinion.id)
            FROM grade 
            LEFT JOIN opinion
                ON opinion.grade_id = grade.id AND opinion.climber_id=:climber_id
            GROUP BY grade.{grade_scale}
            ORDER BY grade.id
            """
        )
        results = db_session.execute(sql_query, {"climber_id": 1}).fetchall()
        grade_data = {result[0]: result[1] for result in results}
        grade_data = remove_trailing(grade_data)

        plotted_data = get_plotted_data(
            driver, "Grade", "Climbs: total tried", grade_scale=grade_scale
        )
        assert len(plotted_data) == len(grade_data)
        for grade, n_sent_routes_plotted in plotted_data:
            assert grade in grade_data
            assert n_sent_routes_plotted == grade_data[grade]

        # check that the plotted grades are sorted correctly
        assert [grade for grade, _ in plotted_data] == list(grade_data.keys())


def test_climbs_per_route_chars(driver, db_session) -> None:
    """
    Ensures that the correct data is plotted for the 'Climbs per Inclination' and
    'Climbs per Height'graphs. The characteristics are sorted alphabetically by name.
    """
    sql_query = text(
        """
        SELECT DISTINCT(route.name), route.height, route.inclination, sit_start
        FROM route
        JOIN climb ON climb.route_id = route.id
        WHERE climb.climber_id = :climber_id
        """
    )
    results = db_session.execute(sql_query, {"climber_id": 1}).fetchall()

    keys = {
        "height": list(range(1, 10)),
        "inclination": list(range(-10, 91, 5)),
        "sit_start": [False, True],
    }
    climbs_per_chars = {char: {key: 0 for key in keys[char]} for char in keys}
    for result in results:
        for char_idx, char in enumerate(keys):
            value = result[char_idx + 1]
            climbs_per_chars[char][value] += 1

    for char in keys:
        climbs_per_chars[char] = remove_trailing(climbs_per_chars[char])

    for char in climbs_per_chars:
        plotted_data = get_plotted_data(
            driver, char.capitalize().replace("_", " "), "Climbs: total tried"
        )
        assert len(plotted_data) == len(climbs_per_chars[char])
        for char_value, n_sent_routes_plotted in plotted_data:
            assert n_sent_routes_plotted == climbs_per_chars[char][char_value]
        assert [char_value for char_value, _ in plotted_data] == list(
            climbs_per_chars[char].keys()
        )


def test_climbs_per_ratings(driver, db_session) -> None:
    """
    Ensures that the correct data is plotted for the 'Climbs per Inclination' and
    'Climbs per Height'graphs. The characteristics are sorted alphabetically by name.
    """
    sql_query = text(
        """
        SELECT rating, landing
        FROM opinion
        WHERE climber_id = :climber_id
        """
    )
    results = db_session.execute(sql_query, {"climber_id": 1}).fetchall()

    keys = list(range(1, 6))
    ratings = ["rating", "landing"]
    climbs_per_ratings = {rating: {key: 0 for key in keys} for rating in ratings}
    for result in results:
        for rat_idx, rat in enumerate(["rating", "landing"]):
            value = result[rat_idx]
            climbs_per_ratings[rat][value] += 1

    for rat in ratings:
        climbs_per_ratings[rat] = remove_trailing(climbs_per_ratings[rat])

    for rat in climbs_per_ratings:
        plotted_data = get_plotted_data(driver, rat.capitalize(), "Climbs: total tried")
        assert len(plotted_data) == len(climbs_per_ratings[rat])
        for rat_value, n_sent_routes_plotted in plotted_data:
            assert n_sent_routes_plotted == climbs_per_ratings[rat][rat_value]
        assert [rat_value for rat_value, _ in plotted_data] == list(
            climbs_per_ratings[rat].keys()
        )


def test_climbs_per_crux(driver, db_session) -> None:
    """
    Ensures that the correct data is plotted for the 'Climbs per Crux' graph.
    """
    sql_query = text(
        """
        SELECT crux.name, COUNT(opinion.id)
        FROM opinion
        JOIN crux_opinions ON crux_opinions.opinion_id = opinion.id
        JOIN crux ON crux.id = crux_opinions.crux_id
        WHERE opinion.climber_id=:climber_id
        GROUP BY crux.id
        ORDER BY crux.name
        """
    )
    results = db_session.execute(sql_query, {"climber_id": 1}).fetchall()
    crux_data = {result[0]: result[1] for result in results}

    plotted_data = get_plotted_data(driver, "Crux", "Climbs: total tried")
    assert len(plotted_data) == len(crux_data)
    for crux, n_sent_routes_plotted in plotted_data:
        assert n_sent_routes_plotted == crux_data[crux]

    # check that the plotted cruxes are sorted correctly
    assert [crux for crux, _ in plotted_data] == list(crux_data.keys())


def test_climbs_per_date(driver, db_session) -> None:
    """
    Ensures that the correct data is plotted for the 'Climbs per Month' graph.
    Dates are aggregated by month and year, and sorted chronologically. Here,
    contrary to most plots, routes can appear more than once.
    """
    sql_query = text(
        """
        SELECT session.date
        FROM session
        JOIN climb ON climb.session_id = session.id
        WHERE session.climber_id = :climber_id
        """
    )
    results = db_session.execute(sql_query, {"climber_id": 1}).fetchall()
    dates = sorted([datetime.strptime(result[0], "%Y-%m-%d") for result in results])

    # count the number of climbs per day, month and year
    climbs_per_day = dict()
    climbs_per_month = dict()
    climbs_per_year = dict()
    for date in dates:
        date_str = date.strftime("%d/%m/%Y")
        for data in [climbs_per_day, climbs_per_month, climbs_per_year]:
            if date_str not in data:
                data[date_str] = 0
            data[date_str] += 1
            date_str = date_str[3:]

    for x_axis, data in zip(
        ["day", "month", "year"],
        [climbs_per_day, climbs_per_month, climbs_per_year],
    ):
        plotted_data = get_plotted_data(
            driver, f"Date: {x_axis}", "Climbs: total tried"
        )
        assert len(plotted_data) == len(data)
        for date, n_sent_routes_plotted in plotted_data:
            assert n_sent_routes_plotted == data[date]
        assert [date for date, _ in plotted_data] == list(data.keys())


def test_climbs_per_conditions(driver, db_session) -> None:
    """
    Ensures that the correct data is plotted for the 'Climbs per Conditions' graph.
    """
    sql_query = text(
        """
        SELECT session.conditions
        FROM session
        JOIN climb ON climb.session_id = session.id
        WHERE climb.climber_id = 1
        """
    )
    results = db_session.execute(sql_query, {"climber_id": 1}).fetchall()
    conditions = [int(result[0]) for result in results if result[0] is not None]

    keys = list(range(1, 6))
    climbs_per_conditions = {key: 0 for key in keys}
    for condition in conditions:
        climbs_per_conditions[condition] += 1
    climbs_per_conditions = remove_trailing(climbs_per_conditions)

    plotted_data = get_plotted_data(driver, "Conditions", "Climbs: total tried")
    assert len(plotted_data) == len(climbs_per_conditions)
    for conditions, n_sent_routes_plotted in plotted_data:
        assert n_sent_routes_plotted == climbs_per_conditions[conditions]
    conditions = [conditions for conditions, _ in plotted_data]
    assert [conditions for conditions, _ in plotted_data] == sorted(conditions)


def test_tries_until_send(driver, db_session) -> None:
    """
    Ensures that the correct data is plotted for the 'Climbs per # sessions' graph.
    """
    sql_query = text(
        """
        SELECT route.id, climb.n_attempts, climb.sent, session.date
        FROM route 
        LEFT JOIN climb ON route.id = climb.route_id AND climb.climber_id = :climber_id
        LEFT JOIN session ON climb.session_id = session.id
        WHERE climb.id IS NOT NULL
        """
    )
    results = db_session.execute(sql_query, {"climber_id": 1}).fetchall()
    route_ids = set(result[0] for result in results)

    n_attempts, n_sessions = list(), list()
    for route_id in route_ids:
        climbs = [result for result in results if result[0] == route_id]
        n_attempts.append(0)
        n_sessions.append(0)

        # get the earliest date at which the route was sent
        min_send_date = datetime.max
        for climb in climbs:
            date = datetime.strptime(climb[3], "%Y-%m-%d")
            if climb[2] and date < min_send_date:
                min_send_date = date

        # add the attempts of the climbs that took place before the route was sent (incl.)
        for climb in climbs:
            date = datetime.strptime(climb[3], "%Y-%m-%d")
            if date <= min_send_date:
                n_attempts[-1] += climb[1]
                n_sessions[-1] += 1

    # count the number of routes per number of attempts/sessions
    tries_until_send = Counter(n_attempts)
    sessions_until_send = Counter(n_sessions)

    # run the tests
    for data_dict, y_axis in zip(
        [tries_until_send, sessions_until_send], ["No. of attempts", "No. of sessions"]
    ):
        plotted_data = get_plotted_data(driver, y_axis, "Climbs: total tried")
        assert len(plotted_data) == max(data_dict.keys())
        for n_tries, n_sent_routes_plotted in plotted_data:
            assert n_sent_routes_plotted == data_dict[n_tries]
        n_tries = [n for n, _ in plotted_data]
        assert [n for n, _ in plotted_data] == sorted(n_tries)


def remove_trailing(data: dict) -> dict:
    """
    Remove the trailing keys that have no climbs.
    """
    for idx in range(2):
        keys = list(data.keys())
        if idx == 1:
            keys = list(reversed(keys))
        for key in keys:
            if data[key] > 0:
                break
            del data[key]
    return data
