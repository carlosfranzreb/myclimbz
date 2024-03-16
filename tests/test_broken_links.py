from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


def test_broken_links(driver):
    links = driver.find_elements(By.TAG_NAME, "a")
    broken_links = check_page_links(driver, links)
    assert len(links) > 0, "No links found on the page"
    assert len(broken_links) == 0, f"The following links are broken: {broken_links}"


def check_page_links(driver, links: list[str]):
    broken_links = list()
    for link in links:
        try:
            url = link.get_attribute("href")
        except Exception:
            continue
        if url:
            driver.execute_script("window.open('{}', '_blank');".format(url))
            WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))
            if len(driver.window_handles) == 2:
                driver.switch_to.window(driver.window_handles[1])
                if "404" in driver.page_source:
                    broken_links.append(url)
                else:
                    broken_links += check_page_links(
                        driver, driver.find_elements(By.TAG_NAME, "a")
                    )
    return broken_links
