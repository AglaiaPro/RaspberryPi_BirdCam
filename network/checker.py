import logging

import requests

logger: logging.Logger = logging.getLogger(__name__)

class NetworkChecker:
    def is_online(self):
        logger.debug("checking internet connection")
        try:
            requests.get("https://www.google.com", timeout=2)
            logger.info("internet available")
            return True
        except:
            logger.warning("no internet connection")
            return False
