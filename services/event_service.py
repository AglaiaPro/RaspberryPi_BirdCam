import logging
import os
import time
from datetime import datetime, timezone

MAX_STORAGE_BYTES = 10 * 1024 * 1024 * 1024

logger: logging.Logger = logging.getLogger(__name__)

class EventService:
    def __init__(self, repo, camera, temp_sensor, network, azure_client):
        self.repo = repo
        self.camera = camera
        self.temp_sensor = temp_sensor
        self.network = network
        self.azure = azure_client

        self.device_id = "raspberry-1"
        self.cooldown = 60
        self.last_event_time = 0

    def handle_motion(self):
        logger.info("motion detected")
        if time.time() - self.last_event_time < self.cooldown:
            logger.debug(f"cooldown active: skipping event")
            return

        self.last_event_time = time.time()

        temperature = self.temp_sensor.read()
        logger.info(f"temperature read: {temperature}")

        if self.network.is_online():
            logger.info("handling ONLINE event")
            self._handle_online_event(temperature)
        else:
            logger.info("handling OFFLINE event")
            self._handle_offline_event(temperature)

    def _handle_online_event(self, temperature):
        video_path = f"/home/pi/data/{datetime.now().timestamp()}.mp4"
        self.camera.record_video(video_path)
        logger.debug(f"video saved: {video_path}")

        try:
            file_url = self.azure.upload_media(video_path)

            payload = {
                "device_id": self.device_id,
                "temperature": temperature,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "file_url": file_url,
                "event_type": "video"
            }

            self.azure.send_telemetry(payload)
        finally:
            if os.path.exists(video_path):
                os.remove(video_path)

    def _handle_offline_event(self, temperature):
        image_path = f"/home/pi/data/{datetime.now().timestamp()}.jpg"
        self.camera.take_photo(image_path)
        logger.debug(f"image saved: {image_path}")

        self.repo.add_event(
            device_id=self.device_id,
            temperature=temperature,
            media_path=image_path,
            event_type="image"
        )
        self._cleanup_storage()

    def _cleanup_storage(self):
        logger.info("cleanup triggered")
        size = self._storage_size()
        logger.info(f"storage size: {size}")
        if size <= MAX_STORAGE_BYTES:
            return

        events = self.repo.get_synced()

        for event in events:
            if size <= MAX_STORAGE_BYTES:
                break

            if event.media_path and os.path.exists(event.media_path):
                file_size = os.path.getsize(event.media_path)
                os.remove(event.media_path)
                size -= file_size

            self.repo.delete_event(event.id)

    def _storage_size(self):
        total = 0

        events = self.repo.get_all_events()

        for event in events:
            if event.media_path and os.path.exists(event.media_path):
                total += os.path.getsize(event.media_path)

        return total
