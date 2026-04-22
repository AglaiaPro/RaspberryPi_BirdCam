import pytest
from unittest.mock import MagicMock
from services.event_service import EventService


def test_cleanup_triggered(monkeypatch):

    repo = MagicMock()
    camera = MagicMock()
    temp = MagicMock()
    network = MagicMock()
    azure = MagicMock()

    temp.read.return_value = 25
    network.is_online.return_value = False

    service = EventService(repo, camera, temp, network, azure)

    # имитируем большой размер
    monkeypatch.setattr(service, "_storage_size", lambda: 11 * 1024 * 1024 * 1024)

    # synced события
    event = MagicMock()
    event.media_path = "file.jpg"
    event.id = 1

    repo.get_synced.return_value = [event]

    service._cleanup_storage()

    repo.delete_event.assert_called()

def test_cleanup_respects_limit(monkeypatch):

    repo = MagicMock()
    camera = MagicMock()
    temp = MagicMock()
    network = MagicMock()
    azure = MagicMock()

    service = EventService(repo, camera, temp, network, azure)

    monkeypatch.setattr(service, "_storage_size", lambda: 12)

    repo.get_synced.return_value = []

    service._cleanup_storage()

    repo.delete_event.assert_not_called()
