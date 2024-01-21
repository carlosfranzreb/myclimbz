"""
Test the filters used for the tables and plots. Each filter is tested individually,
and for the checkbox filters, only one option is selected. Multiple filters, multiple
checkboxes, and removing filters are not tested.
"""


from multiprocessing import Process
from time import sleep
from datetime import datetime

from flask.testing import FlaskClient
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from climbs.models import Area, Sector, Grade, Route, Crux
from tests.conftest import run_app


def test_page_request(test_client: FlaskClient):
    """Ensures that the analysis page loads correctly."""
    response = test_client.get("/analysis")
    assert response.status_code == 200
    assert b"Analysis" in response.data


def get_filtered_data(
    filter_key: str,
    filter_element: str,
    start_value: str | list,
    end_value: str = None,
) -> list:
    """
    Returns the active filters for the given x- and y-axes.

    Args:
        TODO

    Returns:
        the active filters
    """

    app_process = Process(target=run_app)
    app_process.start()
    sleep(10)

    # start a headless Chrome browser
    driver_options = webdriver.ChromeOptions()
    driver_options.add_argument("--headless=new")
    # driver = webdriver.Chrome(options=driver_options)
    driver = webdriver.Chrome()
    driver.get("http://127.0.0.1:5000/table")
    WebDriverWait(driver, 10).until(EC.title_is("Table"))

    # add the filter
    add_filter_btn = driver.find_element(
        By.XPATH, "//button[contains(@onclick, 'add_filter()')]"
    )
    add_filter_btn.click()
    sleep(1)

    # select the filter
    filter_container = driver.find_element(
        By.XPATH, "//div[contains(@class, 'filter-container')][1]"
    )
    filter_select = filter_container.find_element(By.XPATH, ".//select")
    filter_select.click()
    filter_select.find_element(By.XPATH, f".//option[. = '{filter_key}']").click()
    sleep(1)

    # select the values
    filter_div = filter_container.find_element(
        By.XPATH, ".//div[contains(@class, 'filter_div')][1]"
    )
    if filter_element == "checkbox":
        if isinstance(start_value, str):
            start_value = [start_value]
        for label in filter_div.find_elements(By.XPATH, ".//label"):
            if label.text in start_value:
                label.click()
    else:
        for name, value in zip(["start", "end"], [start_value, end_value]):
            if filter_element == "input":
                field = filter_div.find_element(
                    By.XPATH,
                    f".//{filter_element}[contains(@class, '{name}-range')][1]",
                )
                field.clear()
                field.send_keys(value)
            elif filter_element == "select":
                field = filter_div.find_element(
                    By.XPATH,
                    f".//{filter_element}[contains(@class, '{name}-range')][1]",
                )
                field.click()
                field.find_element(By.XPATH, f".//option[. = '{value}']").click()

    # click outside the filter to close it
    driver.find_element(By.XPATH, "//h1").click()
    sleep(1)

    # get the content of the ACTIVE_FILTERS global variable of JavaScript
    active_filters = dict()
    while len(active_filters) == 0:
        sleep(0.5)
        active_filters = driver.execute_script("return Array.from(ACTIVE_FILTERS);")

    # get the content of the DISPLAYED_DATA global variable of JavaScript
    displayed_data = dict()
    while len(displayed_data) == 0:
        sleep(0.5)
        displayed_data = driver.execute_script("return Array.from(DISPLAYED_DATA);")

    driver.quit()
    app_process.terminate()

    return active_filters, displayed_data


def test_grade_filter(app) -> None:
    grades = ["6A", "6A+", "6B"]
    with app.app_context():
        grade_levels = [
            Grade.query.filter_by(font=grade).first().level for grade in grades
        ]
        all_routes = Route.query.all()
        filtered_routes = [
            route.name
            for route in all_routes
            if route.sent and route.grade.font in grades
        ]
    active_filters, displayed_data = get_filtered_data(
        "Grade", "select", grades[0], grades[-1]
    )
    assert len(active_filters) == 1
    assert active_filters[0][0] == "level"
    assert active_filters[0][1] == grade_levels
    assert len(displayed_data) == len(filtered_routes)
    for route in displayed_data:
        assert route["name"] in filtered_routes


def test_attempt_filters(app) -> None:
    values = [1, 4]
    with app.app_context():
        all_routes = Route.query.all()
        filtered_routes = list()
        for route in all_routes:
            if not route.sent:
                continue
            n_attempts = 0
            for climb in route.climbs:
                n_attempts += climb.n_attempts
                if climb.sent:
                    if n_attempts >= values[0] and n_attempts <= values[-1]:
                        filtered_routes.append(route.name)
                        break

    active_filters, displayed_data = get_filtered_data(
        "n_attempts_send", "input", str(values[0]), str(values[-1])
    )
    assert len(active_filters) == 1
    assert active_filters[0][0] == "Attempts"
    assert min(active_filters[0][1]) >= values[0]
    assert max(active_filters[0][1]) <= values[-1]
    assert len(displayed_data) == len(filtered_routes)
    for route in displayed_data:
        assert route["name"] in filtered_routes


def test_number_filters(app) -> None:
    """Test height, landing and inclination filters."""
    for name, values in zip(
        ["height", "landing", "inclination"], [[4.5, 6], [7, 10], [20, 40]]
    ):
        with app.app_context():
            all_routes = Route.query.all()
            filtered_routes = [
                route.name
                for route in all_routes
                if route.sent
                and getattr(route, name) >= values[0]
                and getattr(route, name) <= values[-1]
            ]
        active_filters, displayed_data = get_filtered_data(
            name.capitalize(), "input", str(values[0]), str(values[-1])
        )
        assert len(active_filters) == 1
        assert active_filters[0][0] == name
        assert min(active_filters[0][1]) >= values[0]
        assert max(active_filters[0][1]) <= values[-1]
        assert len(displayed_data) == len(filtered_routes)
        for route in displayed_data:
            assert route["name"] in filtered_routes


def test_date_filter(app) -> None:
    dates_str = ["01/05/2023", "01/12/2023"]
    dates_obj = [datetime.strptime(date, "%d/%m/%Y") for date in dates_str]
    with app.app_context():
        all_routes = Route.query.all()
        filtered_routes, filtered_dates = list(), set()
        for route in all_routes:
            if not route.sent:
                continue
            route_date = datetime.max
            add_climb = False
            for climb in route.climbs:
                if (
                    climb.sent
                    and climb.session.date >= dates_obj[0].date()
                    and climb.session.date <= dates_obj[-1].date()
                ):
                    route_date = min(route_date.date(), climb.session.date)
                    add_climb = True
            if add_climb:
                filtered_routes.append(route.name)
                filtered_dates.add(route_date)

    active_filters, displayed_data = get_filtered_data(
        "Date", "input", dates_str[0], dates_str[-1]
    )
    assert len(active_filters) == 1
    assert active_filters[0][0] == "dates"
    returned_dates = [
        datetime.strptime(date, "%Y-%m-%d").date() for date in active_filters[0][1]
    ]
    assert returned_dates == list(filtered_dates)
    assert len(displayed_data) == len(filtered_routes)
    for route in displayed_data:
        assert route["name"] in filtered_routes


def test_area_filter(app) -> None:
    area = "A1"
    with app.app_context():
        all_routes = Route.query.all()
        filtered_routes = [
            route.name
            for route in all_routes
            if route.sent and route.sector.area.name == area
        ]
    active_filters, displayed_data = get_filtered_data("Area", "checkbox", [area])
    assert len(active_filters) == 1
    assert active_filters[0][0] == "area"
    assert active_filters[0][1] == [area]
    assert len(displayed_data) == len(filtered_routes)
    for route in displayed_data:
        assert route["name"] in filtered_routes


def test_crux_filter(app) -> None:
    crux = "Drag"
    with app.app_context():
        crux_obj = Crux.query.filter_by(name=crux).first()
        all_routes = Route.query.all()
        filtered_routes = [
            route.name
            for route in all_routes
            if route.sent and crux_obj in route.cruxes
        ]
    active_filters, displayed_data = get_filtered_data("Crux", "checkbox", [crux])
    assert len(active_filters) == 1
    assert active_filters[0][0] == "cruxes"
    assert active_filters[0][1] == [crux]
    assert len(displayed_data) == len(filtered_routes)
    for route in displayed_data:
        assert route["name"] in filtered_routes
