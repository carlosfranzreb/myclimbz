"""
pyvirtualdisplay?
https://github.com/MarketingPipeline/Python-Selenium-Action/blob/main/.github/workflows/Selenium-Action_Template.yaml
"""

import requests
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


HOME_URL = "http://127.0.0.1:5000"

response = requests.get(HOME_URL)
assert response.status_code == 200


driver_options = webdriver.ChromeOptions()
driver_options.add_argument("--headless")
driver = webdriver.Chrome(options=driver_options)
driver.get(HOME_URL)
WebDriverWait(driver, 10).until(EC.title_is("Routes"))
