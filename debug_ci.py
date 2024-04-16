"""
pyvirtualdisplay?
https://github.com/MarketingPipeline/Python-Selenium-Action/blob/main/.github/workflows/Selenium-Action_Template.yaml
"""

import requests
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sqlalchemy import create_engine
from sqlalchemy.orm import Session


HOME_URL = "http://127.0.0.1:5000"


engine = create_engine("sqlite:///instance/test_100.db")
session = Session(engine)


response = requests.get(HOME_URL)
assert response.status_code == 200, response.text


# driver_options = webdriver.ChromeOptions()
# driver_options.add_argument("--headless")
# driver = webdriver.Chrome(options=driver_options)
# driver.get(HOME_URL)
# for i in range(10):
#     try:
#         print(driver.title, driver.current_url)
#         WebDriverWait(driver, 1).until(EC.title_is("Routes"))
#         break
#     except:
#         pass
