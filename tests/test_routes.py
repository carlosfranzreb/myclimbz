import pytest
from climbs import create_app
from flask.testing import FlaskClient
from timeit import default_timer as timer
import json

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup

from multiprocessing import Process

import time


def app():
    app = create_app(True)
    app.config["WTF_CSRF_ENABLED"] = False

    app.config.update(
        {
            "TESTING": True,
        }
    )
    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()


def test_request_time_and_size(client: FlaskClient):
    """Test that the request time and size are logged."""
    beg = timer()
    response = client.get("/routes")
    end = timer()
    assert response.status_code == 200
    with open("tests/routes_request_time_and_size.txt", "w") as f:
        f.write(f"Time: {end - beg}\n")
        f.write(f"Size: {len(response.data)}\n")


HEADERS = [
    "Name",
    "Grade",
    "Sector",
    "Area",
    "Sessions",
    "Sent",
    "Height",
    "Landing",
    "Inclination",
]


def run_app():
    app = create_app(True)
    app.run()


def test_sorting():  # client: FlaskClient):
    # Start the Chrome browser
    # response = client.get("/routes")
    app_process = Process(target=run_app)
    app_process.start()

    time.sleep(10)
    driver = webdriver.Chrome()
    # driver.implicitly_wait(10)

    try:
        # driver.get("data:text/html;charset=utf-8," + response.data.decode("utf-8"))
        while driver.title != "Home":
            driver.get("http://127.0.0.1:5000/")
        routes_button = driver.find_element(By.XPATH, "//a[text()='Routes']")
        routes_button.click()
        WebDriverWait(driver, 10).until(EC.title_contains("Routes"))
        HEADER = "Name"
        sorted_names = json.load(
            open("tests/sorted_columns.json", "r", encoding="utf-8")
        )
        for dir in ["asc", "desc"]:
            driver.execute_script(f"window.data_table.columns().sort(1, '{dir}');")
            html = driver.page_source
            elems = get_column_names(html, 20, 0)
            assert elems == sorted_names[HEADER][dir]

    finally:
        # Close the browser window
        driver.quit()
        app_process.terminate()


def get_column_names(html: str, count: int, header_index: int):
    soup = BeautifulSoup(html, "html.parser")

    table = soup.find("table")

    elems = []

    for row in table.find_all("tr")[1:]:  # Skip the header row
        name = row.find_all("td")[header_index].text.strip()

        elems.append(name)

        if len(elems) == count:
            break

    return elems
