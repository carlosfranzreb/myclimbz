"""
Test the filters used for the tables and plots. The filters are stored in the JS
global variable ACTIVE_FILTERS.
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


def get_filtered_data(
    filter_key: str,
    filter_element: str,
    start_value: str,
    end_value: str,
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
    # driver_options = webdriver.ChromeOptions()
    # driver_options.add_argument("--headless=new")
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

    # select the start value
    filter_div = filter_container.find_element(
        By.XPATH, ".//div[contains(@class, 'filter_div')][1]"
    )
    for name, value in zip(["start", "end"], [start_value, end_value]):
        input_field = filter_div.find_element(
            By.XPATH, f".//{filter_element}[contains(@class, '{name}-range')][1]"
        )
        input_field.click()
        input_field.find_element(By.XPATH, f".//option[. = '{value}']").click()
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
        grade_levels = [Grade.query.filter_by(font=grade).first() for grade in grades]
        routes = Route.query.all()
        sent_routes = [
            route for route in routes if route.sent and route.grade.font in grades
        ]
    active_filters, displayed_data = get_filtered_data(
        "Grade", "select", grades[0], grades[-1]
    )
    assert len(active_filters) == 1
    assert active_filters["Grade"] == grade_levels
    assert len(displayed_data) == len(sent_routes)
    for route in displayed_data:
        assert route in sent_routes
