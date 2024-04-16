"""
Test the filters used for the tables and plots. Each filter is tested individually,
and for the checkbox filters, only one option is selected. Multiple filters, multiple
checkboxes, and removing filters are not tested.
"""

from time import sleep
from datetime import datetime

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def reset(driver):
    driver.get("http://localhost:5000/")
    WebDriverWait(driver, 30).until(EC.title_is("Routes"))

    filter_button = driver.find_element(By.ID, "filter_button")
    filter_button.click()
    sleep(2)
    driver.find_element(By.ID, "filter_reset").click()
    sleep(1)
    apply_button = driver.find_element(By.ID, "filter_apply")
    apply_button.click()

    return filter_button, apply_button


def test_grade_filter(driver) -> None:
    filter_button, apply_button = reset(driver)
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


# def test_date_filter(driver) -> None:
#     filter_button, apply_button = reset(driver)
#     filter = driver.find_element(By.ID, "filter_Date_start")
#     # set "02/01/2023" as the start date
#     min_date = "02/01/2023"
#     driver.execute_script(f"arguments[0].value = '{min_date}'", filter)

#     filter_button.click()
#     apply_button.click()
#     displayed_data = driver.execute_script("return Array.from(DISPLAYED_DATA);")
#     min_date = datetime.strptime(min_date, "%d/%m/%Y")
#     assert all(
#         datetime.strptime(route["dates"][-1], "%d/%m/%Y") >= min_date
#         for route in displayed_data
#     )
#     reset(driver)


# def test_cruxes_filter(driver) -> None:
#     filter_button, apply_button = reset(driver)
#     filter = driver.find_element(By.ID, "filter_Crux_button")
#     filter_button.click()
#     filter.click()
#     crux_button = driver.find_element(By.ID, "filter_Crux_1")
#     crux_button.click()

#     apply_button.click()
#     displayed_data = driver.execute_script("return Array.from(DISPLAYED_DATA);")

#     crux = driver.execute_script(
#         "return document.getElementById('filter_Crux_1').textContent"
#     )
#     assert all(crux in route["cruxes"] for route in displayed_data)
#     reset(driver)


# def sent_filter(driver) -> None:
#     filter_button, apply_button = reset(driver)
#     filter = driver.find_element(By.ID, "filter_Sends_1")
#     filter_button.click()
#     filter.click()

#     apply_button.click()
#     displayed_data = driver.execute_script("return Array.from(DISPLAYED_DATA);")

#     assert all(not route["sent"] for route in displayed_data)
#     reset(driver)
