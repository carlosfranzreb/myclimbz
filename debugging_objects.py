from datetime import datetime

# to create a session
transcript = "On January 18th I climbed in La Faka, where there is granite, the conditions were a 7."
entities = {
    "AREA": "La Faka",
    "ROCK": "granite",
    "CONDITIONS": 7,
    "DATE": "January 18th 2023",
}
entities["DATE"] = datetime.strptime(entities["DATE"], "%B %dth %Y")

# ! tmp
flask_session["entities"] = {
    "NAME": "La Zorrera Sit",
    "SECTOR": "A2_S1",
    "GRADE": "7A",
    "N_ATTEMPTS": 15,
    "SENT": True,
    "SIT_START": True,
    "CRUX": ["crimp", "top out"],
    "HEIGHT": 3.0,
}
flask_session["session_id"] = 3
flask_session["area_id"] = 2
# ! end tmp
