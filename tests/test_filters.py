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

from climbz.models import Grade, Route, Crux
from tests.conftest import run_app, driver


def test_filters(driver):
    driver.get("http://127.0.0.1:5000/")
    while driver.title != "Routes":
        sleep(1)
        driver.get("http://127.0.0.1:5000/")

    reset_button = driver.find_element(By.ID, "filter_reset")
    apply_button = driver.find_element(By.ID, "filter_apply")
    filter_button = driver.find_element(By.ID, "filter_button")

    def reset_filters() -> None:
        filter_button.click()
        reset_button.click()
        apply_button.click()

    filters = [grade_filter, date_filter, cruxes_filter, sent_filter]

    for filter in filters:
        filter(driver, filter_button, apply_button)
        reset_filters()


def grade_filter(driver, filter_button, apply_button) -> None:
    grade_filter = driver.find_element(By.ID, "widget_filter_Grade")
    driver.execute_script(
        "arguments[0].removeAttribute('se-min-current')", grade_filter
    )
    driver.execute_script(
        "arguments[0].setAttribute('se-min-current','5')",
        grade_filter,
    )
    filter_button.click()
    apply_button.click()
    min_level = int(grade_filter.get_attribute("se-min-current"))
    assert min_level == 5
    max_level = int(grade_filter.get_attribute("se-max-current"))

    displayed_data = driver.execute_script("return Array.from(DISPLAYED_DATA);")
    assert all(
        route["level"] >= min_level and route["level"] <= max_level
        for route in displayed_data
    )


def date_filter(driver, filter_button, apply_button) -> None:
    filter = driver.find_element(By.ID, "filter_Date_start")
    # set "02/01/2023" as the start date
    min_date = "02/01/2023"
    driver.execute_script(f"arguments[0].value = '{min_date}'", filter)

    filter_button.click()
    apply_button.click()
    displayed_data = driver.execute_script("return Array.from(DISPLAYED_DATA);")
    min_date = datetime.strptime(min_date, "%d/%m/%Y")
    assert all(
        datetime.strptime(route["dates"][-1], "%d/%m/%Y") >= min_date
        for route in displayed_data
    )


def cruxes_filter(driver, filter_button, apply_button) -> None:
    filter = driver.find_element(By.ID, "filter_Crux_button")
    filter_button.click()
    filter.click()
    crux_button = driver.find_element(By.ID, "filter_Crux_1")
    crux_button.click()

    apply_button.click()
    displayed_data = driver.execute_script("return Array.from(DISPLAYED_DATA);")

    crux = "Sloper"
    assert all(crux in route["cruxes"] for route in displayed_data)


def sent_filter(driver, filter_button, apply_button) -> None:

    filter = driver.find_element(By.ID, "filter_Sends_1")
    filter_button.click()
    filter.click()

    apply_button.click()
    displayed_data = driver.execute_script("return Array.from(DISPLAYED_DATA);")

    assert all(not route["sent"] for route in displayed_data)
