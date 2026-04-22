import os

import cv2
import numpy as np
import pytest
from network.client import AzureClient


@pytest.mark.integration
def test_upload_real_api(tmp_path):

    file_path = tmp_path / "test.jpg"

    # создаём реальное изображение
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    cv2.imwrite(str(file_path), img)

    client = AzureClient(
        "https://ktor-env.politecliff-5fb4f1a7.polandcentral.azurecontainerapps.io"
    )

    file_url = client.upload_media(str(file_path))

    assert file_url is not None
    assert file_url.startswith("http")

@pytest.mark.integration
def test_send_telemetry_real_api():

    client = AzureClient(
        "https://ktor-env.politecliff-5fb4f1a7.polandcentral.azurecontainerapps.io"
    )

    payload = {
        "device_id": "raspberry-1",
        "temperature": 25.5,
        "timestamp": "2025-01-01T00:00:00Z",
        "file_url": "http://example.com/file.jpg",
        "event_type": "image"
    }

    response = client.send_telemetry(payload)

    assert response is not None
