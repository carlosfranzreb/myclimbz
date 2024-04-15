import requests

from tests.conftest import BASE_URL


def test_request():
    response = requests.get(BASE_URL)
    assert response.status_code == 200
