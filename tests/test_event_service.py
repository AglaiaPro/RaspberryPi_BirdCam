import pytest
from unittest.mock import MagicMock
from services.event_service import EventService


def test_online_event():

    repo = MagicMock()
    camera = MagicMock()
    temp = MagicMock()
    network = MagicMock()
    azure = MagicMock()

    temp.read.return_value = 25.0
    network.is_online.return_value = True
    camera.record_video.return_value = "video.mp4"
    azure.upload_media.return_value = "http://file.url"

    service = EventService(repo, camera, temp, network, azure)

    service.handle_motion()

    azure.upload_media.assert_called_once()
    azure.send_telemetry.assert_called_once()

def test_offline_event():

    repo = MagicMock()
    camera = MagicMock()
    temp = MagicMock()
    network = MagicMock()
    azure = MagicMock()

    temp.read.return_value = 22.0
    network.is_online.return_value = False
    camera.take_photo.return_value = "photo.jpg"

    service = EventService(repo, camera, temp, network, azure)

    service.handle_motion()

    repo.add_event.assert_called_once()
