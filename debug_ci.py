"""
pyvirtualdisplay?
https://github.com/MarketingPipeline/Python-Selenium-Action/blob/main/.github/workflows/Selenium-Action_Template.yaml
"""

import requests
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# from pyvirtualdisplay import Display
# import chromedriver_autoinstaller


HOME_URL = "http://127.0.0.1:5000"


# chromedriver_autoinstaller.install()


# display = Display(visible=0, size=(800, 800))
# display.start()


response = requests.get(HOME_URL)
assert response.status_code == 200


driver_options = webdriver.ChromeOptions()
driver_options.add_argument("--headless")
driver = webdriver.Chrome(options=driver_options)
driver.get(HOME_URL)
for i in range(10):
    try:
        print(driver.title, driver.current_url)
        WebDriverWait(driver, 1).until(EC.title_is("Routes"))
        break
    except:
        pass
