import logging
import threading
import time
from pathlib import Path

import cv2

logger = logging.getLogger(__name__)

class CameraService:
    def __init__(self, device_path="/dev/video0"):
        self.device_path = device_path
        self.cap = None
        self.lock = threading.Lock()
        self.keepalive_thread = None
        self.stop_event = threading.Event()
        self.last_frame = None

    def open(self):
        with self.lock:
            if self.cap is not None and self.cap.isOpened():
                return

            logger.info("opening camera")

            cap = cv2.VideoCapture(self.device_path, cv2.CAP_V4L2)
            if not cap.isOpened():
                logger.error("camera not available")
                raise Exception("Camera not available")

            # Жорстко ставимо єдиний стабільний режим камери
            cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            cap.set(cv2.CAP_PROP_FPS, 30)

            # Даємо камері трохи часу
            time.sleep(1.0)

            # Прогріваємо потік
            ok = False
            frame = None
            for _ in range(10):
                ok, frame = cap.read()
                if ok and frame is not None:
                    break
                time.sleep(0.2)

            if not ok or frame is None:
                cap.release()
                logger.error("failed to read initial frame from camera")
                raise Exception("Camera not available")

            self.cap = cap
            self.last_frame = frame
            logger.info("camera opened successfully")

    def start_keepalive(self, interval=1.0):
        if self.keepalive_thread and self.keepalive_thread.is_alive():
            return

        logger.info("starting camera keepalive thread")
        self.stop_event.clear()
        self.keepalive_thread = threading.Thread(
            target=self._keepalive_loop,
            args=(interval,),
            daemon=True,
        )
        self.keepalive_thread.start()

    def _keepalive_loop(self, interval):
        while not self.stop_event.is_set():
            try:
                self.ping()
            except Exception:
                logger.exception("camera keepalive failed, trying reopen")
                self.reopen()
            time.sleep(interval)

    def ping(self):
        with self.lock:
            if self.cap is None or not self.cap.isOpened():
                self.open()
                return

            ok, frame = self.cap.read()
            if not ok or frame is None:
                logger.warning("camera ping failed")
                raise Exception("Camera ping failed")

            self.last_frame = frame

    def reopen(self):
        logger.warning("reopening camera")
        self.close()
        time.sleep(2)
        self.open()

    def record_video(self, path, duration=10, fps=20):
        Path(path).parent.mkdir(parents=True, exist_ok=True)

        with self.lock:
            if self.cap is None or not self.cap.isOpened():
                self.open()

            width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)) or 1280
            height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) or 720

            fourcc = cv2.VideoWriter_fourcc(*"avc1")
            out = cv2.VideoWriter(path, fourcc, fps, (width, height))

            if not out.isOpened():
                logger.error("failed to open video writer")
                raise Exception("Failed to open video writer")

            logger.info(f"starting video recording to {path}")

            start_time = time.time()
            frames_written = 0

            try:
                while time.time() - start_time < duration:
                    ret, frame = self.cap.read()

                    if not ret or frame is None:
                        logger.error("error while recording video: frame read failed")
                        raise Exception("Failed to read frame during recording")

                    out.write(frame)
                    self.last_frame = frame
                    frames_written += 1

                    # Легка затримка, щоб fps був ближче до бажаного
                    time.sleep(max(0, 1 / fps))
            finally:
                out.release()

            logger.info(f"video saved to {path}, frames={frames_written}")
            return path

    def take_photo(self, path):
        Path(path).parent.mkdir(parents=True, exist_ok=True)

        with self.lock:
            if self.cap is None or not self.cap.isOpened():
                self.open()

            ret, frame = self.cap.read()

            if not ret or frame is None:
                logger.error("error while taking a photo: frame read failed")
                raise Exception("Failed to capture image")

            self.last_frame = frame
            cv2.imwrite(path, frame)

            logger.info(f"photo saved to {path}")
            return path

    def close(self):
        with self.lock:
            if self.cap is not None:
                logger.info("releasing camera")
                self.cap.release()
                self.cap = None

    def shutdown(self):
        logger.info("shutting down camera service")
        self.stop_event.set()

        if self.keepalive_thread and self.keepalive_thread.is_alive():
            self.keepalive_thread.join(timeout=3)

        self.close()
