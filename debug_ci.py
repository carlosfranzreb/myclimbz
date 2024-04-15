import requests


response = requests.get("https:127.0.0.1:5000")
assert response.status_code == 200
