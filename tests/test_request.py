import requests


def test_request():
    response = requests.get("http://127.0.0.1:5000")
    assert response.status_code == 200, response.text
