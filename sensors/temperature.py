import logging
import os

logger: logging.Logger = logging.getLogger(__name__)

class TemperatureSensor:
    def __init__(self):
        self.base_dir = '/sys/bus/w1/devices/'
        self.device_folder = self._find_sensor()
        self.device_file = self.device_folder + '/w1_slave'

    def _find_sensor(self):
        devices = os.listdir(self.base_dir)
        for d in devices:
            if d.startswith('28-'):
                return self.base_dir + d
        raise Exception("DS18B20 not found")

    def read(self):
        logger.debug("reading DS18B20 sensor")
        with open(self.device_file, 'r') as f:
            lines = f.readlines()
            logger.debug(f"raw lines: {lines}")

        if 'YES' not in lines[0]:
            logger.error('Temperature read failed')
            raise Exception("Temperature read failed")

        temp_line = lines[1]
        temp_string = temp_line.split('t=')[-1]

        logger.debug(f'temperature: {temp_string}')

        return float(temp_string) / 1000.0
