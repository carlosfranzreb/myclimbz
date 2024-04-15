import requests


response = requests.get("127.0.0.1:5000")
assert response.status_code == 200
