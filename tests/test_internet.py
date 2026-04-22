from network.checker import NetworkChecker
from unittest.mock import patch


@patch("requests.get")
def test_online(mock_get):
    mock_get.return_value.status_code = 200

    checker = NetworkChecker()
    assert checker.is_online()
