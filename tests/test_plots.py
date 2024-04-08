"""
Tests the analysis page. The steps performed when plotting data are defined in the
docstring of the plot_data() function in `main.js`. Given that the x- and y-axes are
processed independently, we don't need to test all possible combinations of axes. We
therefore test all possible y-axes for the x-axis "Area", and then all possible x-axes
for the y-axis "# of climbs".

Useful commands when implementing tests:

- Command to run these tests: pytest --driver -s tests/test_analysis.py
- Command to see open ports: lsof -i -P | grep -i "listen"
- Command to kill process on port: kill $(lsof -t -i:5000)
"""

import requests


def test_request():
    response = requests.get("http://localhost:5000")
    assert response.status_code == 200
