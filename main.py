import logging
import signal
import sys
import threading
import time

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


logger = logging.getLogger(__name__)
running = True


def handle_exit(signum, frame):
    global running
    logger.info(f"Received signal {signum}, shutting down...")
    running = False


def main():
    # --- Init ---
    init_db()
    setup_logging()

    global logger
    logger = logging.getLogger(__name__)

    logger.info("Starting BirdCam application")

    # --- Services ---
    repo = EventRepository()
    camera = CameraService("/dev/video0")
    temp = TemperatureSensor()
    network = NetworkChecker()
    azure = AzureClient(
        "https://ktor-env.politecliff-5fb4f1a7.polandcentral.azurecontainerapps.io"
    )
    motion = MotionSensorService(pin=21)

    event_service = EventService(repo, camera, temp, network, azure)
    sync_service = SyncService(repo, network, azure)

    # --- Signals (важливо для systemd) ---
    signal.signal(signal.SIGTERM, handle_exit)
    signal.signal(signal.SIGINT, handle_exit)

    # --- Camera ---
    logger.info("Initializing camera...")
    camera.open()
    camera.start_keepalive(interval=1.0)

    # --- Background sync ---
    threading.Thread(target=sync_service.run, daemon=True).start()

    # --- Main loop ---
    try:
        while running:
            motion.wait_for_motion()

            if not running:
                break

            logger.debug("Motion detected, handling event")
            event_service.handle_motion()

    except Exception:
        logger.exception("Unexpected error in main loop")

    finally:
        logger.info("Shutting down services...")

        try:
            camera.shutdown()
        except Exception:
            logger.exception("Error while shutting down camera")

        logger.info("Application stopped")


if __name__ == "__main__":
    main()
