import time

class SyncService:
    def __init__(self, repo, network, azure_client):
        self.repo = repo
        self.network = network
        self.azure = azure_client

    def run(self):
        while True:
            if self.network.is_online():
                events = self.repo.get_unsynced()

                for event in events:
                    file_url = self.azure.upload_media(event.media_path)

                    payload = {
                        "device_id": event.device_id,
                        "temperature": event.temperature,
                        "timestamp": event.timestamp,
                        "file_url": file_url,
                        "event_type": event.event_type
                    }

                    self.azure.send_telemetry(payload)
                    self.repo.mark_synced(event.id, file_url)

            time.sleep(10)
