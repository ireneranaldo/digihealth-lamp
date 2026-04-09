from typing import Dict, Any
from telegraf_pyplug.main import print_influxdb_format
from ..config import config

class TelegrafClient:
    """Client for sending data to InfluxDB via Telegraf."""

    def __init__(self):
        self.measurement = config.communicator.telegraf.get('measurement', 'ZPHSensor')
        self.tags = config.communicator.telegraf.get('tags', {})

    def send(self, data: Dict[str, Any]):
        """Send data to Telegraf."""
        # Remove dashboard data from main fields
        fields = {k: v for k, v in data.items() if k != 'dashboard'}
        print_influxdb_format(
            measurement=self.measurement,
            fields=fields,
            tags=self.tags
        )