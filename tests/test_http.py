import pytest
from unittest.mock import patch
from network.client import AzureClient


@patch("requests.post")
def test_upload(mock_post, tmp_path):

    # создаём временный файл
    file_path = tmp_path / "test.jpg"
    file_path.write_bytes(b"fake-image-data")

    # мок ответа
    mock_post.return_value.json.return_value = {"file_url": "test"}
    mock_post.return_value.raise_for_status.return_value = None

    client = AzureClient("http://test")

    url = client.upload_media(str(file_path))

    assert url == "test"