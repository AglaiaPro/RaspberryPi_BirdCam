import logging
import time
import cv2

logger: logging.Logger = logging.getLogger(__name__)

class CameraService:
    def __init__(self, device_index=0):
        self.device_index = device_index
        logger.debug(f"camera init device={self.device_index}")

    def record_video(self, path, duration=10, fps=20):
        logger.debug("starting video capture")
        cap = cv2.VideoCapture(self.device_index)

        if not cap.isOpened():
            logger.error('camera not available')
            raise Exception("Camera not available")

        # Получаем размеры кадра
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # Кодек (mp4)
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(path, fourcc, fps, (width, height))

        start_time = time.time()

        while time.time() - start_time < duration:
            ret, frame = cap.read()

            if not ret:
                logger.error('error while recording a video, ret not found')
                break

            out.write(frame)

        cap.release()
        out.release()

        logger.info(f"video saved to {path}")
        return path

    def take_photo(self, path):
        logger.debug("frame captured")
        cap = cv2.VideoCapture(self.device_index)

        if not cap.isOpened():
            logger.error('camera not available')
            raise Exception("Camera not available")

        ret, frame = cap.read()

        if not ret:
            cap.release()
            logger.error('error while taking a photo, ret not found')
            raise Exception("Failed to capture image")

        cv2.imwrite(path, frame)
        cap.release()

        logger.info(f"photo saved to {path}")
        return path
