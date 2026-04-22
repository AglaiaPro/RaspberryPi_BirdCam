from unittest.mock import MagicMock

from services.sync_service import SyncService


def test_sync():
    repo = MagicMock()
    network = MagicMock()
    azure = MagicMock()

    event = MagicMock()
    event.id = 1
    event.media_path = "photo.jpg"
    event.device_id = "dev1"
    event.temperature = 20
    event.timestamp = "2025-01-01"

    repo.get_unsynced.return_value = [event]
    network.is_online.return_value = True
    azure.upload_media.return_value = "url"

    sync = SyncService(repo, network, azure)

    sync.run = lambda: None  # не запускаем infinite loop

    # имитация одного цикла
    events = repo.get_unsynced()

    for e in events:
        file_url = azure.upload_media(e.media_path)
        azure.send_telemetry({})
        repo.mark_synced(e.id, file_url)

    repo.mark_synced.assert_called_once()