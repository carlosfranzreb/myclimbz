from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement


SKIP_URLS = [
    "http://localhost:5000/logout",
    "http://localhost:5000/cancel_form",
]
SEEN_URLS = list()


def test_broken_links(driver):
    broken_links = check_page_links(driver)
    assert len(SEEN_URLS) > 0, "No links found on the page"
    assert len(broken_links) == 0, f"The following links are broken: {broken_links}"


def check_page_links(driver):
    urls = get_urls(driver.find_elements(By.TAG_NAME, "a"))
    broken_links = list()
    for url in urls:
        if url in SEEN_URLS:
            continue
        SEEN_URLS.append(url)
        driver.get(url)
        WebDriverWait(driver, 10).until(
            lambda driver: url == clean_url(driver.current_url)
        )
        if "404" in driver.title or "Not Found" in driver.title:
            broken_links.append(url)
        else:
            broken_links += check_page_links(driver)
    return broken_links


def get_urls(links: list[WebElement]) -> list[str]:
    """Returns a list of URLs from the links"""
    urls = list()
    for link in links:
        try:
            url = link.get_attribute("href")
        except Exception:
            continue
        if url:
            url = clean_url(url)
            if url not in SKIP_URLS:
                urls.append(url)
    return urls


def clean_url(url: str) -> str:
    if url.endswith("#"):
        url = url[:-1]
    if url.endswith("/"):
        url = url[:-1]
    return url
