import requests
from typing import Dict, Any
from ..logger import logger


class ShellyController:
    """Controls a Shelly relay device based on sensor data."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.ip = config.get('ip')
        self.username = config.get('username')
        self.password = config.get('password')
        self.mode = config.get('mode', 'presence')
        self.person_threshold = config.get('person_threshold', 1)
        self.iaqi_threshold = config.get('iaqi_threshold', 100)
        self.auth = (self.username, self.password) if self.username and self.password else None

    def update(self, data: Dict[str, Any]):
        if not self.ip:
            logger.warning("Shelly IP not configured")
            return

        try:
            if self.mode == 'presence':
                active = int(data.get('person_count', 0)) >= self.person_threshold
            elif self.mode == 'iaqi':
                active = int(data.get('IAQI', 0)) >= self.iaqi_threshold
            else:
                active = False

            self._set_relay(active)
        except Exception as e:
            logger.error(f"Shelly update failed: {e}")

    def _set_relay(self, turn_on: bool):
        action = 'on' if turn_on else 'off'
        url = f"http://{self.ip}/rpc/relay/0?turn={action}"
        try:
            response = requests.get(url, auth=self.auth, timeout=6)
            response.raise_for_status()
            logger.info(f"Shelly relay set to {action}")
        except Exception as e:
            logger.error(f"Shelly relay request failed: {e}")
