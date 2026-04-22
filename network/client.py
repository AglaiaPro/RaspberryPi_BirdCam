import logging
import os

import requests

logger: logging.Logger = logging.getLogger(__name__)

class AzureClient:
    def __init__(self, base_url):
        self.base_url = base_url

    def upload_media(self, file_path):
        logger.debug(f"uploading file: {file_path}")
        if not os.path.exists(file_path):
            logger.error(f"upload failed")
            raise FileNotFoundError(f"{file_path} not found")

        url = f"{self.base_url}/media/upload"
        with open(file_path, 'rb') as f:
            response = requests.post(url, files={"file": ("file.jpg", f, "image/jpeg")})

        print("STATUS:", response.status_code)
        print("RESPONSE:", response.text)

        response.raise_for_status()
        logger.info(f"upload success: {file_path}")
        return response.json()["file_url"]

    def send_telemetry(self, payload):
        logger.debug("sending telemetry")
        url = f"{self.base_url}/telemetry"

        response = requests.post(url, json=payload)

        print("STATUS:", response.status_code)
        print("RESPONSE:", response.text)

        response.raise_for_status()
        logger.info("telemetry sent successfully")
        return response.json()
