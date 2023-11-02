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
