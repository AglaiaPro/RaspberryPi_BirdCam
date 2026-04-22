import logging

from gpiozero import MotionSensor

logger: logging.Logger = logging.getLogger(__name__)

class MotionSensorService:

    def __init__(self, pin=21):
        self.sensor = MotionSensor(pin, pull_up=False)

    def wait_for_motion(self):
        logger.debug('waiting for motion')
        self.sensor.wait_for_motion()
        logger.debug('motion is detected')
        return True
