import requests
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session


HOME_URL = "http://127.0.0.1:5000"


engine = create_engine("sqlite:///instance/test_100.db")
session = Session(engine)
sql_query = text(
    """
    SELECT 
        area.name,
        route.id,
        climb.id,
        climb.n_attempts,
        climb.sent,
        session.date
    FROM area 
    JOIN sector ON area.id = sector.area_id 
    JOIN route ON sector.id = route.sector_id 
    LEFT JOIN climb ON route.id = climb.route_id AND climb.climber_id = :climber_id
    LEFT JOIN session ON climb.session_id = session.id
    WHERE climb.id IS NOT NULL
    """
)
results = session.execute(sql_query, {"climber_id": 1}).fetchall()
assert len(results) > 0, "No climbs found for climber 1"


response = requests.get(HOME_URL)
assert response.status_code == 200, response.text


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
