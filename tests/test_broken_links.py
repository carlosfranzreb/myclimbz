from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import TimeoutException


SKIP_ACTIONS = ["delete", "reopen", "cancel", "logout", "edit", "add"]
OBJECTS = ["route", "session", "area", "climber"]
SEEN_URLS = list()
BROKEN_URLS = list()


def test_broken_links(driver):
    check_page_links(driver)
    other_urls = [f"http://127.0.0.1:5000/{obj}/1" for obj in OBJECTS]
    other_urls += [f"http://127.0.0.1:5000/edit_{obj}/1" for obj in OBJECTS]
    check_links(driver, other_urls)
    assert len(SEEN_URLS) > len(OBJECTS) * 2, "Suspiciously few URLs were checked."
    assert len(BROKEN_URLS) == 0, f"The following links are broken: {BROKEN_URLS}"


def check_page_links(driver):
    urls = get_urls(driver.find_elements(By.TAG_NAME, "a"))
    return check_links(driver, urls)


def check_links(driver, urls: list[str]) -> list[str]:
    for url in urls:
        if url in SEEN_URLS:
            continue
        print(url)
        SEEN_URLS.append(url)
        driver.get(url)
        try:
            WebDriverWait(driver, 10).until(
                lambda driver: url == clean_url(driver.current_url)
            )
        except TimeoutException:
            BROKEN_URLS.append(url)
            continue

        if "Error" in driver.title or "Exception" in driver.title:
            BROKEN_URLS.append(url)
        else:
            check_page_links(driver)


def get_urls(links: list[WebElement]) -> list[str]:
    """Returns a list of URLs from the links"""
    urls = list()
    for link in links:
        try:
            url = link.get_attribute("href")
        except Exception:
            continue
        if url:
            if "reddit" in url or "github" in url:
                continue
            url = clean_url(url)

            # skip duplicates and URLs that have already been checked
            if url in urls or url in SEEN_URLS:
                continue

            # skip URLs that refer to objects; these are checked separately
            is_valid = True
            for obj in OBJECTS:
                if f"/{obj}/" in url:
                    is_valid = False
                    break
            if not is_valid:
                continue

            # skip URLs that include certain actions
            for action in SKIP_ACTIONS:
                if action in url:
                    is_valid = False
                    break
            if is_valid:
                urls.append(url)
    return urls


def clean_url(url: str) -> str:
    if url.endswith("#"):
        url = url[:-1]
    if url.endswith("/"):
        url = url[:-1]
    return url
