"""
Tests the plots. The steps performed when plotting data are defined in the
docstring of the plot_data() function in `main.js`. Given that the x- and y-axes are
processed independently, we don't need to test all possible combinations of axes. We
therefore test all possible y-axes for the x-axis "Area", and then all possible x-axes
for the y-axis "# of climbs".
"""

from time import sleep
from collections import Counter
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sqlalchemy import text

from .conftest import HOME_TITLE


def get_plotted_data(driver: webdriver.Chrome, x_axis: str, y_axis: str) -> list:
    """
    Returns the plotted data for the given x- and y-axes.

    Args:
        x_axis: the x-axis value
        y_axis: the y-axis value
    Returns:
        the plotted data as a list of tuples, where each tuple is of the form
        (key, value).
    """

    # check that the URL is correct
    home_url = "http://127.0.0.1:5000"
    if driver.current_url not in [home_url, home_url + "/"]:
        driver.get(home_url)
        WebDriverWait(driver, 30).until(EC.title_is(HOME_TITLE))

    # toggle to show plot
    btn = driver.find_element(By.XPATH, "//a[@id='display-form-toggle']")
    if "plot" in btn.text.lower():
        btn.click()

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

    return plotted_data


def test_climbs_per_area(driver, db_session) -> None:
    """
    Ensures that the correct data is plotted for the 'Climbs sent/tried per Area' and
    'Success rate per Area' graphs. The areas are sorted alphabetically by name.
    ! In DB, not in plot: Ghost Rider, Rámájama, Louis Je Master
    """

    sql_query = text(
        """
        SELECT DISTINCT area.name, route.id, climb.sent
        FROM climber
        JOIN climbing_session ON climber.id = climbing_session.climber_id
        JOIN climb ON climbing_session.id = climb.session_id
        JOIN route ON climb.route_id = route.id
        JOIN sector ON route.sector_id = sector.id
        JOIN area ON sector.area_id = area.id
        WHERE climbing_session.climber_id = 1
        """
    )
    results = db_session.execute(sql_query).fetchall()

    unique_areas = set(result[0] for result in results)
    area_data = {area: list() for area in unique_areas}
    for area in unique_areas:
        n_routes = len(set([result[1] for result in results if result[0] == area]))
        n_sent_routes = len(
            set(
                [
                    result[1]
                    for result in results
                    if result[0] == area and result[2] == 1
                ]
            )
        )
        area_data[area] = {
            "n_routes": n_routes,
            "n_sent_routes": n_sent_routes,
            "success_rate": n_sent_routes / n_routes if n_routes > 0 else 0,
        }

    for area_data_key, y_axis in zip(
        ["n_routes", "n_sent_routes", "success_rate"],
        ["Climbs: total tried", "Climbs: total sent", "Climbs: success rate"],
    ):
        plotted_data = get_plotted_data(driver, "Area", y_axis)
        assert len(plotted_data) == len(area_data), f"Failed for key {area_data_key}"
        for area, value in plotted_data:
            assert (
                value == area_data[area][area_data_key]
            ), f"Failed for key {area_data_key} and area {area}"
        area_names = [area for area, _ in plotted_data]
        assert [area for area, _ in plotted_data] == sorted(
            area_names
        ), f"Failed for key {area_data_key}"


def test_attempts_per_area(driver, db_session) -> None:
    """
    Ensures that the correct data is plotted for all four 'Attempts per Area' graphs: with
    total, avg. min. and max. values. Here we want to know how many attempts it took to send
    a route. Routes that have not been sent are not included in the graph.
    """
    sql_query = text(
        """
        SELECT DISTINCT
            area.name,
            route.id,
            climb.id,
            climb.n_attempts,
            climb.sent,
            climbing_session.date
        FROM climber
        JOIN climbing_session ON climber.id = climbing_session.climber_id
        JOIN climb ON climbing_session.id = climb.session_id
        JOIN route ON climb.route_id = route.id
        JOIN sector ON route.sector_id = sector.id
        JOIN area ON sector.area_id = area.id
        WHERE climbing_session.climber_id = 1
        """
    )
    results = db_session.execute(sql_query).fetchall()

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
    'Max. Grade per Area' graphs. If the climber has added his own opinion of the
    grade, that grade is taken. Otherwise, the consensus grade (avg. grade of all
    opinions, rounded).
    """

    # gather the opinions of each climber
    sql_query = text(
        """
        SELECT DISTINCT route.id, opinion.climber_id, grade.level
        FROM route
        JOIN climb ON route.id = climb.route_id
        JOIN opinion ON route.id = opinion.route_id
        JOIN grade ON opinion.grade_id = grade.id
        """
    )
    opinion_results = db_session.execute(sql_query).fetchall()
    opinions = dict()
    for result in opinion_results:
        if result[1] not in opinions:
            opinions[result[1]] = dict()
        opinions[result[1]][result[0]] = result[2]

    # iterate over the routes tried by climber 1
    sql_query = text(
        """
        SELECT DISTINCT area.name, route.id
        FROM climber
        JOIN climbing_session ON climber.id = climbing_session.climber_id
        JOIN climb ON climbing_session.id = climb.session_id
        JOIN route ON climb.route_id = route.id
        JOIN sector ON route.sector_id = sector.id
        JOIN area ON sector.area_id = area.id
        WHERE climbing_session.climber_id = 1
        """
    )
    climber_results = db_session.execute(sql_query).fetchall()

    area_data = dict()
    for result in climber_results:
        area_name, route_id = result
        if area_name not in area_data:
            area_data[area_name] = list()
        if route_id in opinions[1]:
            area_data[area_name].append(opinions[1][route_id])
        else:
            route_opinions = list()
            for climber_id in opinions:
                if climber_id != 1 and route_id in opinions[climber_id]:
                    route_opinions.append(opinions[climber_id][route_id])
            if len(route_opinions) > 0:
                area_data[area_name].append(
                    Counter(route_opinions).most_common(1)[0][0]
                )

    area_grades_avg, area_grades_max = dict(), dict()
    for area in area_data:
        area_grades_avg[area] = sum(area_data[area]) / len(area_data[area])
        area_grades_max[area] = max(area_data[area])

    plotted_data = get_plotted_data(driver, "Area", "Grade: avg.")
    assert len(plotted_data) == len(area_data)
    for area, avg_grade_plotted in plotted_data:
        assert avg_grade_plotted == area_grades_avg[area], f"Failed for {area}"

    plotted_data = get_plotted_data(driver, "Area", "Grade: max.")
    assert len(plotted_data) == len(area_data)
    for area, max_grade_plotted in plotted_data:
        assert max_grade_plotted == area_grades_max[area], f"Failed for {area}"


def test_climbs_per_sector(driver, db_session) -> None:
    """
    Ensures that the correct data is plotted for the 'Climbs per Sector' graph. The
    sectors are sorted alphabetically by name.
    """
    sql_query = text(
        """
        SELECT DISTINCT sector.name, route.id, climb.sent
        FROM climber
        JOIN climbing_session ON climber.id = climbing_session.climber_id
        JOIN climb ON climbing_session.id = climb.session_id
        JOIN route ON climb.route_id = route.id
        JOIN sector ON route.sector_id = sector.id
        WHERE climbing_session.climber_id = 1
        """
    )
    results = db_session.execute(sql_query).fetchall()

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
    """

    # gather the opinions of each climber
    sql_query = text(
        """
        SELECT DISTINCT route.id, opinion.climber_id, grade.font
        FROM route
        JOIN climb ON route.id = climb.route_id
        JOIN opinion ON route.id = opinion.route_id
        JOIN grade ON opinion.grade_id = grade.id
        """
    )
    opinion_results = db_session.execute(sql_query).fetchall()
    opinions = dict()
    for result in opinion_results:
        if result[1] not in opinions:
            opinions[result[1]] = dict()
        opinions[result[1]][result[0]] = result[2]

    # iterate over the routes tried by climber 1
    sql_query = text(
        """
        SELECT DISTINCT climb.route_id
        FROM climber
        JOIN climbing_session ON climber.id = climbing_session.climber_id
        JOIN climb ON climbing_session.id = climb.session_id
        WHERE climbing_session.climber_id = 1
        """
    )
    climber_results = db_session.execute(sql_query).fetchall()

    grade_data = dict()
    for result in climber_results:
        route_id = result[0]

        level = None
        if route_id in opinions[1]:
            level = opinions[1][route_id]
        elif route_id in opinions[2]:
            level = opinions[2][route_id]

        if level is not None:
            if level not in grade_data:
                grade_data[level] = 1
            else:
                grade_data[level] += 1

    # check that all plotted grades are correct
    plotted_data = get_plotted_data(driver, "Grade", "Climbs: total tried")
    for grade, n_sent_routes_plotted in plotted_data:
        if n_sent_routes_plotted == 0:
            assert grade not in grade_data
        else:
            assert grade in grade_data
            assert n_sent_routes_plotted == grade_data[grade], f"Failed for {grade}"

    # check that all appropriate grades are plotted
    plotted_grades = [grade for grade, _ in plotted_data]
    data_grades = list(grade_data.keys())
    plotted_grades_indices = list()
    for grade in data_grades:
        assert grade in plotted_grades, f"Failed for {grade}"
        plotted_grades_indices.append(data_grades.index(grade))

    # check that the plotted grades are sorted correctly
    assert plotted_grades_indices == sorted(plotted_grades_indices)


def test_climbs_per_route_chars(driver, db_session) -> None:
    """
    Ensures that the correct data is plotted for the 'Climbs per Inclination' and
    'Climbs per Height'graphs. The characteristics are sorted alphabetically by name.
    """
    sql_query = text(
        """
        SELECT DISTINCT route.name, route.height, route.inclination, sit_start
        FROM climber
        JOIN climbing_session ON climber.id = climbing_session.climber_id
        JOIN climb ON climbing_session.id = climb.session_id
        JOIN route ON climb.route_id = route.id
        WHERE climbing_session.climber_id = 1
        """
    )
    results = db_session.execute(sql_query).fetchall()

    keys = {
        "height": list(range(1, 10)),
        "inclination": list(range(-50, 91, 5)),
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
        SELECT DISTINCT(route.id), opinion.rating, opinion.landing
        FROM opinion
        INNER JOIN route ON opinion.route_id = route.id
        INNER JOIN climb ON climb.route_id = route.id
        WHERE opinion.climber_id = :climber_id
        """
    )
    results = db_session.execute(sql_query, {"climber_id": 1}).fetchall()

    keys = list(range(1, 6))
    ratings = ["rating", "landing"]
    climbs_per_ratings = {rating: {key: 0 for key in keys} for rating in ratings}
    for result in results:
        for rat_idx, rat in enumerate(["rating", "landing"]):
            value = result[rat_idx + 1]
            climbs_per_ratings[rat][value] += 1

    for rat in ratings:
        climbs_per_ratings[rat] = remove_trailing(climbs_per_ratings[rat])

    for rat in climbs_per_ratings:
        plotted_data = get_plotted_data(driver, rat.capitalize(), "Climbs: total tried")
        assert len(plotted_data) == len(climbs_per_ratings[rat]), f"Failed for {rat}"
        for rat_value, n_sent_routes_plotted in plotted_data:
            assert (
                n_sent_routes_plotted == climbs_per_ratings[rat][rat_value]
            ), f"Failed for {rat}, {rat_value}"
        assert [rat_value for rat_value, _ in plotted_data] == list(
            climbs_per_ratings[rat].keys()
        ), f"Failed for {rat}, {rat_value}"


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
    Ensures that the correct data is plotted for the 'Climbs per Date' graphs.
    Contrary to most plots, routes can appear here more than once.
    """
    sql_query = text(
        """
        SELECT climbing_session.date
        FROM climbing_session
        JOIN climb ON climb.session_id = climbing_session.id
        WHERE climbing_session.climber_id = 1
        """
    )
    results = db_session.execute(sql_query).fetchall()
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
        SELECT climbing_session.conditions
        FROM climbing_session
        JOIN climb ON climb.session_id = climbing_session.id
        WHERE climbing_session.climber_id = 1
        """
    )
    results = db_session.execute(sql_query).fetchall()
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
