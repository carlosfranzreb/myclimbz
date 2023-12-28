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

from climbs.models import Area, Sector, Grade, Route
from tests.conftest import run_app


def test_page_request(test_client: FlaskClient):
    """Ensures that the analysis page loads correctly."""
    response = test_client.get("/analysis")
    assert response.status_code == 200
    assert b"Analysis" in response.data


def get_plotted_data(x_axis: str, y_axis: str) -> list:
    """
    Returns the plotted data for the given x- and y-axes.

    Args:
        x_axis: the x-axis value
        y_axis: the y-axis value

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
    rate per Area' graphs. The areas are sorted alphabetically by name.
    """
    with app.app_context():
        areas = Area.query.all()
        n_routes = {area.name: area.n_routes for area in areas}
        n_sent_routes = {area.name: area.n_sent_routes for area in areas}
    success_rates = {
        area.name: n_sent_routes[area.name] / n_routes[area.name] for area in areas
    }

    plotted_data = get_plotted_data("area", "# of climbs")
    assert len(plotted_data) == len(areas)
    for area, n_sent_routes_plotted in plotted_data:
        assert n_sent_routes_plotted == n_sent_routes[area]

    plotted_data = get_plotted_data("area", "Success rate")
    assert len(plotted_data) == len(areas)
    for area, success_rate_plotted in plotted_data:
        assert success_rate_plotted == success_rates[area]

    area_names = [area for area, _ in plotted_data]
    assert [area for area, _ in plotted_data] == sorted(area_names)


def test_tries_per_area(app) -> None:
    """
    Ensures that the correct data is plotted for the 'Tries per Area' graph. Here we
    want to know how many tries it took to send a route. Routes that have not been
    sent are not included in the graph.
    """
    with app.app_context():
        areas = Area.query.all()
        n_tries = dict()
        for area in areas:
            n_tries[area.name] = 0
            for sector in area.sectors:
                for route in sector.routes:
                    if not route.sent:
                        continue
                    route_tries = 0
                    for climb in route.climbs:
                        route_tries += climb.n_attempts
                        if climb.sent:
                            break
                    n_tries[area.name] += route_tries

    plotted_data = get_plotted_data("area", "# of tries")
    assert len(plotted_data) == len(areas)
    for area, n_sent_routes_plotted in plotted_data:
        assert n_sent_routes_plotted == n_tries[area]


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

    plotted_data = get_plotted_data("area", "Avg. grade")
    assert len(plotted_data) == len(areas)
    for area, avg_grade_plotted in plotted_data:
        assert avg_grade_plotted == area_grades_avg[area]

    plotted_data = get_plotted_data("area", "Max. grade")
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

    plotted_data = get_plotted_data("sector", "# of climbs")
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
    """
    with app.app_context():
        grades = Grade.query.all()
        n_sent_routes = {
            grade.font: sum([route.sent for route in grade.routes]) for grade in grades
        }
    all_levels = [grade.level for grade in grades if n_sent_routes[grade.font] > 0]
    n_columns = max(all_levels) - min(all_levels) + 1

    plotted_data = get_plotted_data("level", "# of climbs")
    assert len(plotted_data) == n_columns
    for grade, n_sent_routes_plotted in plotted_data:
        assert n_sent_routes_plotted == n_sent_routes[grade]

    grades = [grade for grade, _ in plotted_data]
    assert [grade for grade, _ in plotted_data] == sorted(grades)


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
        climbs_per_crux = dict()
        for route in routes:
            if not route.sent:
                continue
            for char in climbs_per_chars:
                char_value = getattr(route, char)
                if char_value not in climbs_per_chars[char]:
                    climbs_per_chars[char][char_value] = 0
                climbs_per_chars[char][char_value] += 1
            for crux in route.cruxes:
                if crux.name not in climbs_per_crux:
                    climbs_per_crux[crux.name] = 0
                climbs_per_crux[crux.name] += 1

    for char in climbs_per_chars:
        plotted_data = get_plotted_data(char, "# of climbs")
        assert len(plotted_data) == len(climbs_per_chars[char])
        for char_value, n_sent_routes_plotted in plotted_data:
            assert n_sent_routes_plotted == climbs_per_chars[char][char_value]
        char_values = [char_value for char_value, _ in plotted_data]
        assert [char_value for char_value, _ in plotted_data] == sorted(char_values)

    plotted_data = get_plotted_data("cruxes", "# of climbs")
    assert len(plotted_data) == len(climbs_per_crux)
    for crux, n_sent_routes_plotted in plotted_data:
        assert n_sent_routes_plotted == climbs_per_crux[crux]
    cruxes = [crux for crux, _ in plotted_data]
    assert [crux for crux, _ in plotted_data] == sorted(cruxes)
