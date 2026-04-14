import requests
import datetime
from typing import Dict, Any
from ..logger import logger


class LEDWiFiController:
    """Controls LED WiFi dimmable lights for circadian lighting based on lux values."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.ip = config.get('ip')
        self.username = config.get('username')
        self.password = config.get('password')
        self.mode = config.get('mode', 'circadian')
        self.min_lux = config.get('min_lux', 10)
        self.max_lux = config.get('max_lux', 500)
        self.auth = (self.username, self.password) if self.username and self.password else None

    def update(self, data: Dict[str, Any]):
        if not self.ip:
            logger.warning("LED WiFi IP not configured")
            return

        try:
            lux = data.get('lux-IntensitaLuminosa', 0)

            if self.mode == 'circadian':
                brightness, color_temp = self._calculate_circadian_from_lux(lux)
                self._set_light(brightness, color_temp)
            elif self.mode == 'adaptive':
                brightness = self._calculate_adaptive_brightness(lux)
                self._set_light(brightness, 2700)  # Fixed warm white
            else:
                logger.warning(f"Unknown LED WiFi mode: {self.mode}")

        except Exception as e:
            logger.error(f"LED WiFi update failed: {e}")

    def _calculate_circadian_from_lux(self, lux: float) -> tuple:
        """Calculate brightness and color temperature based on lux for circadian rhythm."""
        # Normalize lux to 0-1 range
        normalized_lux = min(max((lux - self.min_lux) / (self.max_lux - self.min_lux), 0), 1)

        # Brightness: higher when lux is lower (compensate for low light)
        brightness = int((1 - normalized_lux) * 100)  # 0-100%

        # Color temperature: warmer (2700K) when lux is low, cooler (6500K) when lux is high
        if normalized_lux < 0.3:
            color_temp = 2700  # Warm white for low light
        elif normalized_lux < 0.7:
            color_temp = 4000  # Neutral white for medium light
        else:
            color_temp = 6500  # Cool white for high light

        return brightness, color_temp

    def _calculate_adaptive_brightness(self, lux: float) -> int:
        """Calculate adaptive brightness based on ambient lux."""
        # Simple inverse relationship: brighter when ambient light is lower
        normalized_lux = min(max((lux - self.min_lux) / (self.max_lux - self.min_lux), 0), 1)
        brightness = int((1 - normalized_lux) * 100)
        return max(brightness, 10)  # Minimum 10% brightness

    def _set_light(self, brightness: int, color_temp: int):
        """Set LED light brightness and color temperature."""
        # Assuming the LED controller accepts HTTP commands similar to Tuya/Smart Life devices
        # This is a generic implementation - may need adjustment based on specific device API

        try:
            # Example API calls - adjust based on actual device protocol
            brightness_cmd = {
                "method": "set_brightness",
                "params": {"brightness": brightness}
            }

            color_temp_cmd = {
                "method": "set_color_temperature",
                "params": {"color_temperature": color_temp}
            }

            # Send brightness command
            response = requests.post(
                f"http://{self.ip}/api",
                json=brightness_cmd,
                auth=self.auth,
                timeout=5
            )
            response.raise_for_status()

            # Send color temperature command
            response = requests.post(
                f"http://{self.ip}/api",
                json=color_temp_cmd,
                auth=self.auth,
                timeout=5
            )
            response.raise_for_status()

            logger.info(f"LED WiFi set to {brightness}% brightness, {color_temp}K")

        except Exception as e:
            logger.error(f"LED WiFi command failed: {e}")
            # Fallback: try simple on/off if dimming fails
            try:
                action = "on" if brightness > 0 else "off"
                url = f"http://{self.ip}/relay/0?turn={action}"
                requests.get(url, auth=self.auth, timeout=3)
            except:
                pass