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

from multiprocessing import Process
from time import sleep

from flask.testing import FlaskClient
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from climbz.models import Area, Sector, Grade, Route
from tests.conftest import run_app


def test_page_request(test_client: FlaskClient):
    """Ensures that the analysis page loads correctly."""
    response = test_client.get("/analysis")
    assert response.status_code == 200
    assert b"Analysis" in response.data


def get_plotted_data(
    x_axis: str,
    y_axis: str,
    toggle_grade_scale: bool = False,
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

    app_process = Process(target=run_app)
    app_process.start()
    sleep(10)

    # start a headless Chrome browser
    driver_options = webdriver.ChromeOptions()
    driver_options.add_argument("--headless=new")
    driver = webdriver.Chrome(options=driver_options)
    driver.get("http://127.0.0.1:5000/analysis")
    WebDriverWait(driver, 10).until(EC.title_is("Analysis"))

    if toggle_grade_scale:
        btn = driver.find_element(By.XPATH, "//input[@id='grade-scale-toggle']")
        btn.find_element(By.XPATH, "..").click()

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

    driver.quit()
    app_process.terminate()

    return plotted_data


def test_climbs_per_area(app) -> None:
    """
    Ensures that the correct data is plotted for the 'Climbs per Area' and 'Success
    rate per Area' graphs. The areas are sorted alphabetically by name. Check also
    the 'Climbs per Area' numbers when the "Include unsent boulders" checkbox is
    checked.
    """
    with app.app_context():
        areas = Area.query.all()
        n_routes = {area.name: area.n_routes for area in areas}
        n_sent_routes = {area.name: area.n_sent_routes for area in areas}
    success_rates = {
        area.name: n_sent_routes[area.name] / n_routes[area.name] for area in areas
    }

    plotted_data = get_plotted_data("Area", "Climbs: total")
    assert len(plotted_data) == len(areas)
    for area, n_sent_routes_plotted in plotted_data:
        assert n_sent_routes_plotted == n_sent_routes[area]
    area_names = [area for area, _ in plotted_data]
    assert [area for area, _ in plotted_data] == sorted(area_names)

    plotted_data = get_plotted_data("Area", "Climbs: success rate")
    assert len(plotted_data) == len(areas)
    for area, success_rate_plotted in plotted_data:
        assert success_rate_plotted == success_rates[area]

    plotted_data = get_plotted_data("Area", "Climbs: total", check_unsent=True)
    assert len(plotted_data) == len(areas)
    for area, n_routes_plotted in plotted_data:
        assert n_routes_plotted == n_routes[area]


def test_attempts_per_area(app) -> None:
    """
    Ensures that the correct data is plotted for all four 'Attempts per Area' graphs: with
    total, avg. min. and max. values. Here we want to know how many attempts it took to send
    a route. Routes that have not been sent are not included in the graph.
    """
    with app.app_context():
        areas = Area.query.all()
        n_attempts = dict()
        for area in areas:
            n_attempts[area.name] = list()
            for sector in area.sectors:
                for route in sector.routes:
                    if not route.sent:
                        continue
                    route_attempts = 0
                    for climb in route.climbs:
                        route_attempts += climb.n_attempts
                        if climb.sent:
                            break
                    n_attempts[area.name].append(route_attempts)

    plotted_data = get_plotted_data("Area", "Attempts: total")
    assert len(plotted_data) == len(areas)
    for area, n_sent_routes_plotted in plotted_data:
        assert n_sent_routes_plotted == sum(n_attempts[area])

    plotted_data = get_plotted_data("Area", "Attempts: avg.")
    assert len(plotted_data) == len(areas)
    for area, avg_attempts_plotted in plotted_data:
        assert avg_attempts_plotted == sum(n_attempts[area]) / len(n_attempts[area])

    plotted_data = get_plotted_data("Area", "Attempts: min.")
    assert len(plotted_data) == len(areas)
    for area, min_attempts_plotted in plotted_data:
        assert min_attempts_plotted == min(n_attempts[area])

    plotted_data = get_plotted_data("Area", "Attempts: max.")
    assert len(plotted_data) == len(areas)
    for area, max_attempts_plotted in plotted_data:
        assert max_attempts_plotted == max(n_attempts[area])


def test_grade_per_area(app) -> None:
    """Ensures that the correct data is plotted for the 'Avg. Grade per Area' and
    'Max. Grade per Area' graphs."""
    with app.app_context():
        areas = Area.query.all()
        area_levels = dict()
        for area in areas:
            area_levels[area.name] = list()
            for sector in area.sectors:
                for route in sector.routes:
                    if route.sent:
                        area_levels[area.name].append(route.grade.level)
    area_grades_avg, area_grades_max = dict(), dict()
    for area in areas:
        name = area.name
        area_grades_avg[name] = sum(area_levels[name]) / len(area_levels[name])
        area_grades_max[name] = max(area_levels[name])

    plotted_data = get_plotted_data("Area", "Grade: avg.")
    assert len(plotted_data) == len(areas)
    for area, avg_grade_plotted in plotted_data:
        assert avg_grade_plotted == area_grades_avg[area]

    plotted_data = get_plotted_data("Area", "Grade: max.")
    assert len(plotted_data) == len(areas)
    for area, max_grade_plotted in plotted_data:
        assert max_grade_plotted == area_grades_max[area]


def test_climbs_per_sector(app) -> None:
    """
    Ensures that the correct data is plotted for the 'Climbs per Sector' graph. The
    sectors are sorted alphabetically by name.
    """
    with app.app_context():
        sectors = Sector.query.all()
        n_sent_routes = {sector.name: sector.n_sent_routes for sector in sectors}

    plotted_data = get_plotted_data("Sector", "Climbs: total")
    assert len(plotted_data) == len(sectors)
    for sector, n_sent_routes_plotted in plotted_data:
        assert n_sent_routes_plotted == n_sent_routes[sector]

    sector_names = [sector for sector, _ in plotted_data]
    assert [sector for sector, _ in plotted_data] == sorted(sector_names)


def test_climbs_per_grade(app):
    """
    Ensures that the correct data is plotted for the 'Climbs per Grade' graph. The
    grades are sorted by level. The number of columns in the graph is equal to the
    number of grades between the lowest and highest level that have climbs, inclusive.
    Check also the 'Climbs per Grade' numbers when the "Grade scale" switch is toggled,
    i.e. change to V-scale,
    """
    with app.app_context():
        grades = Grade.query.all()
        n_sent_routes = {"font": dict(), "hueco": dict()}
        first_nonzero = None
        last_nonzero = 0
        for grade in grades:
            value = sum([route.sent for route in grade.routes])
            n_sent_routes["font"][grade.font] = value
            n_sent_routes["hueco"][grade.hueco] = value + n_sent_routes["hueco"].get(
                grade.hueco, 0
            )
            if value > 0 and first_nonzero is None:
                first_nonzero = grade.level
            elif value > 0 and last_nonzero < grade.level:
                last_nonzero = grade.level

        hueco_grades_unique = set()
        for level in range(first_nonzero, last_nonzero + 1):
            hueco_grade = grades[level].hueco
            hueco_grades_unique.add(hueco_grade)

    n_columns = {
        "font": last_nonzero - first_nonzero + 1,
        "hueco": len(hueco_grades_unique),
    }

    for scale in n_sent_routes:
        plotted_data = get_plotted_data(
            "Grade", "Climbs: total", toggle_grade_scale=scale == "hueco"
        )
        assert len(plotted_data) == n_columns[scale]
        for grade, n_sent_routes_plotted in plotted_data:
            assert n_sent_routes_plotted == n_sent_routes[scale][grade]
        plotted_grades = [grade for grade, _ in plotted_data]
        grades_sorted = list()
        for grade in grades:
            grade = getattr(grade, scale)
            if grade in grades_sorted:
                continue
            grades_sorted.append(grade)
            if len(grades_sorted) == n_columns[scale]:
                break
        assert plotted_grades == grades_sorted


def test_climbs_per_route_chars(app):
    """
    Ensures that the correct data is plotted for the 'Climbs per Landing', 'Climbs per
    Inclination', 'Climbs per Height' and 'Climbs per Crux' graphs. The characteristics
    are sorted alphabetically by name.
    """
    with app.app_context():
        routes = Route.query.all()
        climbs_per_chars = {
            "landing": dict(),
            "inclination": dict(),
            "height": dict(),
        }
        for route in routes:
            if not route.sent:
                continue
            for char in climbs_per_chars:
                char_value = getattr(route, char)
                if char_value not in climbs_per_chars[char]:
                    climbs_per_chars[char][char_value] = 0
                climbs_per_chars[char][char_value] += 1

    for char in climbs_per_chars:
        plotted_data = get_plotted_data(char.capitalize(), "Climbs: total")
        assert len(plotted_data) == len(climbs_per_chars[char])
        for char_value, n_sent_routes_plotted in plotted_data:
            assert n_sent_routes_plotted == climbs_per_chars[char][char_value]
        char_values = [char_value for char_value, _ in plotted_data]
        assert [char_value for char_value, _ in plotted_data] == sorted(char_values)


def test_climbs_per_crux(app) -> None:
    """
    Ensures that the correct data is plotted for the 'Climbs per Crux' graph.
    """
    with app.app_context():
        routes = Route.query.all()
        climbs_per_crux = dict()
        for route in routes:
            if not route.sent:
                continue
            for crux in route.cruxes:
                if crux.name not in climbs_per_crux:
                    climbs_per_crux[crux.name] = 0
                climbs_per_crux[crux.name] += 1

    plotted_data = get_plotted_data("Crux", "Climbs: total")
    assert len(plotted_data) == len(climbs_per_crux)
    for crux, n_sent_routes_plotted in plotted_data:
        assert n_sent_routes_plotted == climbs_per_crux[crux]
    cruxes = [crux for crux, _ in plotted_data]
    assert [crux for crux, _ in plotted_data] == sorted(cruxes)


def test_climbs_per_month(app) -> None:
    """
    Ensures that the correct data is plotted for the 'Climbs per Month' graph.
    Dates are aggregated by month and year, and sorted chronologically.
    """
    with app.app_context():
        routes = Route.query.all()
        climbs_per_month = dict()
        for route in routes:
            if not route.sent:
                continue
            for climb in route.climbs:
                month = climb.session.date.strftime("%Y-%m")
                if month not in climbs_per_month:
                    climbs_per_month[month] = 0
                climbs_per_month[month] += 1

    plotted_data = get_plotted_data("Date: month", "Climbs: total")
    assert len(plotted_data) == len(climbs_per_month)
    for month, n_sent_routes_plotted in plotted_data:
        assert n_sent_routes_plotted == climbs_per_month[month]
    months = [month for month, _ in plotted_data]
    assert [month for month, _ in plotted_data] == sorted(months)


def test_climbs_per_conditions(app) -> None:
    """
    Ensures that the correct data is plotted for the 'Climbs per Conditions' graph.
    Conditions are sorted alphabetically by name.
    """
    with app.app_context():
        routes = Route.query.all()
        climbs_per_conditions = dict()
        for route in routes:
            if not route.sent:
                continue
            for climb in route.climbs:
                conditions = climb.session.conditions
                if conditions not in climbs_per_conditions:
                    climbs_per_conditions[conditions] = 0
                climbs_per_conditions[conditions] += 1

    plotted_data = get_plotted_data("Conditions", "Climbs: total")
    assert len(plotted_data) == len(climbs_per_conditions)
    for conditions, n_sent_routes_plotted in plotted_data:
        assert n_sent_routes_plotted == climbs_per_conditions[conditions]
    conditions = [conditions for conditions, _ in plotted_data]
    assert [conditions for conditions, _ in plotted_data] == sorted(conditions)
