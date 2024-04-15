import requests


response = requests.get("app:5000")
assert response.status_code == 200
