"""
Tests the analysis page.

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

from climbs.models import Area
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
    """Ensures that the correct data is plotted for the 'Climbs per Area' graph."""
    with app.app_context():
        areas = Area.query.all()
        n_sent_routes = {area.name: area.n_sent_routes for area in areas}
    plotted_data = get_plotted_data("area", "# of climbs")
    assert len(plotted_data) == len(areas)
    for area, n_sent_routes_plotted in plotted_data:
        assert n_sent_routes_plotted == n_sent_routes[area]
