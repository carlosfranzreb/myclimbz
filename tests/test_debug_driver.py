from selenium import webdriver
from selenium.webdriver.common.by import By


def test_request(driver: webdriver.Chrome):
    btn = driver.find_element(By.XPATH, "//input[@id='display-form-toggle']")
    btn.click()
