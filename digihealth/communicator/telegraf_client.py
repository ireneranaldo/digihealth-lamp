import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
from typing import Dict, Any
from ..config import config
from ..logger import logger

class TelegrafClient:
    """Invia i dati direttamente a InfluxDB Cloud usando il formato del vecchio script."""

    def __init__(self):
        # Configurazioni estratte dal tuo telegraf.conf
        self.url = config.communicator.telegraf.get('url', 'https://influxdb1.digisense.it')
        self.token = config.communicator.telegraf.get('token', '')
        self.org = config.communicator.telegraf.get('org', '')
        self.bucket = config.communicator.telegraf.get('bucket', '')
        self.measurement = config.communicator.telegraf.get('measurement', 'ZPHSensor_sensore')
        self.tags = config.communicator.telegraf.get('tags', {}) or {}

        # Inizializzazione Client
        self.client = influxdb_client.InfluxDBClient(
            url=self.url,
            token=self.token,
            org=self.org
        )
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)

    def send(self, data: Dict[str, Any]):
        """Invia i dati mantenendo i nomi originali delle variabili."""
        try:
            # Creazione del punto per InfluxDB
            point = influxdb_client.Point(self.measurement)
            
            # Mappiamo i campi esattamente come faceva il vecchio parse_sensor_data
            # Questi nomi sono quelli che Telegraf riceveva e mandava al database
            fields = {
                "PM1-Particolato-[µg/m^3]": data.get("PM1-Particolato-[µg/m^3]"),
                "PM2_5-Particolato-[µg/m^3]": data.get("PM2_5-Particolato-[µg/m^3]"),
                "PM10-Particolato-[µg/m^3]": data.get("PM10-Particolato-[µg/m^3]"),
                "CO2-AnidrideCarbonica-[ppm]": data.get("CO2-AnidrideCarbonica-[ppm]"),
                "TVOC-QualitaAria-[G]": data.get("TVOC-QualitaAria-[G]"),
                "TEMP-[C]": data.get("TEMP-[C]"),
                "HUM-[%]": data.get("HUM-[%]"),
                "CH2O-Formaldeie-[mg/m^3]": data.get("CH2O-Formaldeie-[mg/m^3]"),
                "CO-MonossidoDiCarbonio-[ppm]": data.get("CO-MonossidoDiCarbonio-[ppm]"),
                "O3-Ozono-[ppm]": data.get("O3-Ozono-[ppm]"),
                "NO2-BiossidoDiAzoto-[ppm]": data.get("NO2-BiossidoDiAzoto-[ppm]"),
                "lux-IntensitaLuminosa": data.get("lux-IntensitaLuminosa"),
                "IAQI": data.get("IAQI"),
                "people_count": data.get("people_count"),
                "window_open": data.get("window_open"),
                "door_open": data.get("door_open"),
                "door_count": data.get("door_count")
            }

            # Aggiungiamo solo i campi che non sono None
            field_count = 0
            for key, val in fields.items():
                if val is not None:
                    point.field(key, float(val))
                    field_count += 1

            if field_count == 0:
                logger.warning(f"No valid fields to send to InfluxDB. Data received: {data}")
                return

            # Aggiungiamo i tag configurati
            for tag_name, tag_value in self.tags.items():
                if tag_value is not None:
                    point.tag(tag_name, str(tag_value))

            # Invio fisico del dato
            self.write_api.write(bucket=self.bucket, org=self.org, record=point)
            
            sent_keys = [key for key, val in fields.items() if val is not None]
            logger.debug(f"Sent {field_count} fields to InfluxDB: {sent_keys}")
            
        except Exception as e:
            logger.error(f"Errore durante l'invio a InfluxDB: {e}")
