from typing import Dict, Any
from ..config import config
from ..logger import logger

class ActuatorManager:
    """Manages all actuators."""

    def __init__(self):
        self.actuators = []
        self._load_actuators()

    def _load_actuators(self):
        """Load available actuators."""
        if config.actuators.neopixel.get('enabled', True):
            from .neopixel_controller import NeoPixelController
            self.actuators.append(NeoPixelController(config.actuators.neopixel))
            logger.info("NeoPixel actuator loaded")

        if config.actuators.shelly.get('enabled', False):
            from .shelly_controller import ShellyController
            self.actuators.append(ShellyController(config.actuators.shelly))
            logger.info("Shelly actuator loaded")

        if config.actuators.led_wifi.get('enabled', False):
            from .led_wifi_controller import LEDWiFiController
            self.actuators.append(LEDWiFiController(config.actuators.led_wifi))
            logger.info("LED WiFi actuator loaded")

    def update(self, data: Dict[str, Any]):
        """Update actuators based on sensor data."""
        for actuator in self.actuators:
            actuator.update(data)