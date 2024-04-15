import requests


response = requests.get("https://app:5000")
assert response.status_code == 200
