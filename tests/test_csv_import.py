from time import sleep
import os

from flask.testing import FlaskClient
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from tests.conftest import run_app, driver

from time import sleep


def test_csv_import(driver):
    driver.get("http://127.0.0.1:5000")
    WebDriverWait(driver, 30).until(EC.title_is("Routes"))

    csv_path = os.path.join(
        os.getcwd(), "climbz", "static", "data", "csv_import_test.csv"
    )
    this_file_path = os.path.abspath(__file__)
    csv_button = driver.find_element(By.ID, "import_csv_button")
    csv_button.click()

    # send wrong file type
    csv_input = driver.find_element(By.ID, "csv_file_form")
    csv_input.send_keys(this_file_path)
    # assert that alert is shown
    alert = driver.switch_to.alert
    assert alert.text
    alert.accept()
    # sleep(1)

    csv_input.send_keys(csv_path)

    name_select = driver.find_element(By.ID, "csv_select_name")
    assert name_select.accessible_name == "Name"
    # assert that the option "Area" of the name select is disabled
    assert not driver.find_element(
        By.CSS_SELECTOR, '#csv_select_name option[value="Area"]'
    ).is_enabled()

    # remove the option "Name" from the select
    name_select.send_keys("--")
    # assert that alert sent when confirm is clicked
    confirm_button = driver.find_element(By.ID, "confirm_csv_import_button")
    confirm_button.click()
    driver.get_screenshot_as_file("screenshot.png")
    alert = driver.switch_to.alert
    assert alert.text
    alert.accept()
    name_select.send_keys("Name")

    grade_select = driver.find_element(By.ID, "csv_select_level")
    # set the option "Angle"
    grade_select.send_keys("Angle")
    # assert that alert sent
    alert = driver.switch_to.alert
    assert alert.text
    alert.accept()
    assert grade_select.accessible_name == "Grade"

    height_select = driver.find_element(By.ID, "csv_select_height")
    # set the option "Date"
    height_select.send_keys("Date")
    # assert that alert sent
    alert = driver.switch_to.alert
    assert alert.text
    alert.accept()
    assert height_select.accessible_name == "Height"

    landing_select = driver.find_element(By.ID, "csv_select_landing")
    # set the option "Angle"
    landing_select.send_keys("Angle")
    # assert that alert sent
    alert = driver.switch_to.alert
    assert alert.text
    alert.accept()
    assert landing_select.accessible_name == "Landing"

    sent_select = driver.find_element(By.ID, "csv_select_sent")
    # set the option "Angle"
    sent_select.send_keys("Angle")
    # assert that alert sent
    alert = driver.switch_to.alert
    assert alert.text
    alert.accept()
    assert sent_select.accessible_name == "--"

    sent_select.send_keys("Sent")

    dates_select = driver.find_element(By.ID, "csv_select_dates")
    # set the option "Angle"
    dates_select.send_keys("Angle")
    # assert that alert sent
    alert = driver.switch_to.alert
    assert alert.text
    alert.accept()
    assert dates_select.accessible_name == "--"
    # Confirm import with sent and without dates and check that alert is shown
    confirm_button.click()
    alert = driver.switch_to.alert
    assert alert.text
    alert.accept()

    dates_select.send_keys("Date")

    cancel_button = driver.find_element(By.ID, "cancel_csv_import_button")
    cancel_button.click()

    csv_button.click()
    assert name_select.options.length == 1
    csv_input.send_keys(csv_path)

    request = None

    def get_request(x):
        nonlocal request
        request = x

    confirm_button.click()
