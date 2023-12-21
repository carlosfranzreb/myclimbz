from multiprocessing import Process
from time import sleep

import pytest
from flask.testing import FlaskClient
from flask import Flask
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from climbs import create_app


def app():
    app = create_app()
    app.run()


@pytest.fixture()
def app_subprocess():
    app_process = Process(target=app)
    app_process.start()
    return app_process


@pytest.fixture()
def client():
    app = create_app()  # (debug=True, short=True)
    app.run()
    return app.test_client()


@pytest.fixture()
def driver(app_subprocess: Process):
    """Starts the Chrome webdriver and opens the analysis page."""
    driver = webdriver.Chrome()
    while driver.title != "Analysis":
        driver.get("http://127.0.0.1:5000/analysis")
        sleep(1)
    return driver


def test_page_request(client: FlaskClient):
    """Ensures that the analysis page loads correctly."""
    response = client.get("/analysis")
    assert response.status_code == 200
    assert b"Analysis" in response.data


def test_climbs_per_area(driver: webdriver.Chrome):
    """
    Test the graph content for axes:
    - x: area
    - y: number of climbs
    """

    x_axis_select = driver.find_element(By.XPATH, "//select[@id='x-axis-select']")
    x_axis_select.click()
    x_axis_select.find_element(By.XPATH, "//option[. = 'area']").click()

    y_axis_select = driver.find_element(By.XPATH, "//select[@id='y-axis-select']")
    y_axis_select.click()
    y_axis_select.find_element(By.XPATH, "//option[. = '# of climbs']").click()

    # get the content of the PLOTTED_DATA global variable of JavaScript
    plotted_data = driver.execute_script("return PLOTTED_DATA")
    print(plotted_data)
