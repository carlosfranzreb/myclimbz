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


@pytest.fixture()
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


def run_app():
    app = create_app(True)
    app.run()


def test_sorting():
    app_process = Process(target=run_app)
    app_process.start()

    time.sleep(10)
    driver = webdriver.Chrome()

    try:
        while driver.title != "Home":
            driver.get("http://127.0.0.1:5000/")
        routes_button = driver.find_element(By.XPATH, "//a[text()='Routes']")
        routes_button.click()
        WebDriverWait(driver, 10).until(EC.title_contains("Routes"))
        sorted_names = json.load(
            open("tests/sorted_columns.json", "r", encoding="utf-8")
        )
        rows_to_test = 50
        for header in sorted_names.keys():
            header_index = get_header_index(driver.page_source, header)
            for dir in ["asc", "desc"]:
                driver.execute_script(
                    f"window.data_table.columns().sort({header_index+1}, '{dir}');"
                )
                time.sleep(0.5)
                html = driver.page_source
                elems = get_column_names(html, rows_to_test, header_index)
                # assert elems == sorted_names[header][dir][:rows_to_test]

    finally:
        driver.quit()
        app_process.terminate()


def get_header_index(html: str, header: str):
    soup = BeautifulSoup(html, "html.parser")

    table = soup.find("table")
    headers = table.find_all("th")
    return headers.index(soup.find("th", text=header))


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
