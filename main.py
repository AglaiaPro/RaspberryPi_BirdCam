import logging
import threading

from logging_config import setup_logging
from media.camera import CameraService
from network.checker import NetworkChecker
from network.client import AzureClient
from sensors.motion import MotionSensorService
from sensors.temperature import TemperatureSensor
from services.event_service import EventService
from services.sync_service import SyncService
from storage.db import init_db
from storage.repository import EventRepository


def main():
    init_db()
    setup_logging()
    logger = logging.getLogger(__name__)

    repo = EventRepository()
    camera = CameraService()
    temp = TemperatureSensor()
    network = NetworkChecker()
    azure = AzureClient("https://ktor-env.politecliff-5fb4f1a7.polandcentral.azurecontainerapps.io")
    motion = MotionSensorService(pin=21)

    event_service = EventService(repo, camera, temp, network, azure)
    sync_service = SyncService(repo, network, azure)

    threading.Thread(target=sync_service.run, daemon=True).start()

    while True:
        motion.wait_for_motion()
        logger.debug('Motion is detected, start to handle')
        event_service.handle_motion()
