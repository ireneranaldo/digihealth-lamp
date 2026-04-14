from typing import Dict, Any
from .base import BaseSensor
from ..logger import logger

try:
    import RPi.GPIO as GPIO
except Exception:
    GPIO = None


class GPIOContactSensor(BaseSensor):
    """Base class for door/window contact sensors."""

    def __init__(self, config: Dict[str, Any], name: str):
        super().__init__(config)
        self.name = name
        self.pin = config.get('gpio_pin')
        self.pull_up_down = config.get('pull_up_down', 'up').lower()
        self._gpio_ready = False
        self.count = 0
        self.last_state = None

    def is_available(self) -> bool:
        if GPIO is None:
            self.logger.error("RPi.GPIO library is not available")
            return False
        if self.pin is None:
            self.logger.error(f"GPIO pin not configured for {self.name} sensor")
            return False

        try:
            GPIO.setwarnings(False)
            GPIO.setmode(GPIO.BCM)
            pud = GPIO.PUD_UP if self.pull_up_down == 'up' else GPIO.PUD_DOWN
            GPIO.setup(self.pin, GPIO.IN, pull_up_down=pud)
            self._gpio_ready = True
            return True
        except Exception as e:
            self.logger.error(f"GPIO sensor {self.name} not available: {e}")
            return False

    def read(self) -> Dict[str, Any]:
        if GPIO is None or not self._gpio_ready:
            return {}

        try:
            value = GPIO.input(self.pin)
            is_open = value == 0 if self.pull_up_down == 'up' else value == 1
            
            # Track count for door sensor (increment on open)
            if self.name == 'door' and self.last_state is not None and not self.last_state and is_open:
                self.count += 1
            
            self.last_state = is_open
            
            result = {f"{self.name}_open": int(is_open)}
            if self.name == 'door':
                result[f"{self.name}_count"] = self.count
            
            return result
        except Exception as e:
            self.logger.error(f"Error reading {self.name} sensor: {e}")
            return {}


class DoorSensor(GPIOContactSensor):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config, 'door')


class WindowSensor(GPIOContactSensor):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config, 'window')
